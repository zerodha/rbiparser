"""A utility for downloading, parsing and sanitizing bank database (IFSC, MICR, address etc.) Excel sheets from the RBI website.

Scrapes the RBI IFS .xls sheet dumps and imports them.
1. Reads all the .xls URLs from the RBI page
2. Downloads each file into a directory and
   converts it to a CSV in another directory.
3. Each file's http etag header is saved in a file (etags.json),
   so that unchanged files are not redownloaded each time.

Usage:
  rbiparser download
  rbiparser convert
  rbiparser combine

License: MIT License

Kailash Nadh, http://nadh.in
May 2013
"""

import re
import csv
import json
import urlparse
import os
import glob
import string

import requests
from bs4 import BeautifulSoup as soup
import xlrd

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logger = logging.getLogger("rbiparser")

HEADERS = ["BANK", "IFSC", "MICR", "BRANCH", "ADDRESS", "CONTACT", "CITY", "DISTRICT", "STATE"]

module_path = os.path.dirname(os.path.abspath(__file__))
banks_list_filename = "banks.json"
filters_filename = "filters.json"

# Regex
alphanumeric = re.compile(r"[^a-z0-9]", re.IGNORECASE)
spaces = re.compile(r"(\s+)")
brackets = re.compile(r"([^\s])(\()(.+?)(\))([a-z0-9])?")
punctuations = re.compile(r"([{}\s])\1+".format(string.punctuation))
nom = re.compile(r"([^a-z0-9]|^)(No|Number)[\,\.\s:\-]", re.IGNORECASE)
dnom = re.compile(r"([^a-z]|^)D[o\/\,\.\s:\-]+No:", re.IGNORECASE)
opp = re.compile(r"([^a-z]|^)Opp[\/\,\.\s:\-]", re.IGNORECASE)
pb = re.compile(r"([^a-z0-9]|^)(PB|Postbox)([\s\.:])", re.IGNORECASE)
po = re.compile(r"([^a-z0-9]|^)(PO|Post)([\s\.:])", re.IGNORECASE)
dist = re.compile(r"([^a-z]|^)Dist(rict|t)?([\.\s:\-]+)", re.IGNORECASE)
dangling_punctuations = re.compile(r"[^a-z0-9\)\]\.\,]+$", re.IGNORECASE)
trailing_punctuations = re.compile(r"[^a-z0-9\)\]]+$", re.IGNORECASE)
rbo = re.compile(r"RBO", re.IGNORECASE)
pin = re.compile(r"([0-9]{6}|[0-9]{3}\s[0-9]{3})")
pin_small = re.compile(r"([\s\-]?)([0-9]+)$")
pin_text = re.compile(r"(Pin|Pincode|Pin code)([^a-z0-9]+)?$", re.IGNORECASE)
number_suffix = re.compile(r"([0-9])(nd|rd|th)", re.IGNORECASE)

exclude_words = ["to", "the", "at", "of", "by", "as", "for", "via"]


def get_sheet_urls(url):
	"""Scrapes the RBI page and gets the list of .xls sheets."""
	r = requests.get(url)
	if r.status_code != 200:
		raise Exception("Invalid response from", url)

	# Extract the urls.
	s = soup(r.content, "lxml")
	links = s.findAll("a", href=re.compile("\.xls$"))

	if len(links) < 1:
		raise Exception("Couldn't find any .xls urls")

	return [l["href"] for l in links]


def convert_xls_to_csv(src, target, headers):
	"""Convert .xls to .csv files."""
	try:
		sheet = xlrd.open_workbook(src).sheet_by_index(0)
	except Exception as e:
		raise Exception("Can't open sheet.", str(e))

	with open(target, "wb") as cf:
		writer = csv.writer(cf, quoting=csv.QUOTE_ALL)

		first = False
		try:
			for n in xrange(sheet.nrows):
				vals = sheet.row_values(n)

				# There are junk unicode characters that need to be stripped.
				vals = [v.encode("ascii", errors="ignore") if type(v) is unicode else v for v in vals]

				# Validate headers.
				if not first:
					first = True

					if len(vals) != len(headers):
						raise Exception("Headers don't match.")

				writer.writerow(vals)
		except Exception as e:
			raise Exception("Can't convert sheet.", str(e))


def url_to_file(url):
	"""Exctract the potential filename from a file url."""
	return urlparse.urlparse(url).path.split("/")[-1]


def load_etags(fname):
	"""Load the etags list."""
	try:
		with open(fname, "r") as f:
			return json.loads(f.read())
	except:
		return {}


def save_etags(etags, fname):
	"""Save the etags list."""
	try:
		with open(fname, "w") as f:
			f.write(json.dumps(etags, indent=4))
	except Exception as e:
		raise Exception("Could not write to " + fname + ": " + str(e))


def get_url_headers(url):
	"""Get the HTTP headers of a URL."""
	try:
		r = requests.head(url)
		return r.headers
	except Exception as e:
		raise Exception("Can't reach", url, ": ", str(e))


def download(url, target):
	"""Download a file and save it to disk."""
	try:
		r = requests.get(url, stream=True)
		r.raw.decode_content = True
	except Exception as e:
		raise Exception("Can't download", url, ": ", str(e))

	try:
		with open(target, "wb") as f:
			for chunk in r.iter_content(chunk_size=10000):
				if chunk:
					f.write(chunk)
	except Exception as e:
		raise Exception("Can't write ", target, ": ", str(e))

	return {
		"etag": r.headers.get("etag", ""),
		"length": int(r.headers.get("content-length", 0))
	}


def download_all(scrape_url, xls_dir, etags_file):
	"""Download all files."""
	urls = get_sheet_urls(scrape_url)
	logger.info("%d sheets to download" % (len(urls),))

	# Create xls folder if path doesn't exist
	if not os.path.exists(xls_dir):
		os.mkdir(xls_dir)

	# HTTP urls don't work.
	urls = [u.replace("http:", "https:") for u in urls]

	# Load the etags to compare against (and skip) file downloads.
	etags = load_etags(etags_file)

	# Download and convert each sheet.
	for n, url in enumerate(urls):
		logger.info("%d - %s" % (n, url))

		fname = url_to_file(url)
		xls_path = xls_dir + "/" + fname

		# Get the URL headers.
		try:
			headers = get_url_headers(url)
			et = headers.get("etag")

			if url in etags and \
				etags[url] == et and \
				os.path.isfile(xls_path):

				logger.info("> Same etag. Skipping")
				continue

			size = int(headers.get("content-length")) / 1024
			logger.info("> %d KB" % (size,))

			etags[url] = et
			save_etags(etags, "etags.json")

			download(url, xls_path)
		except Exception as e:
			logger.exception(e)
			continue


def convert_all(src, target, headers):
	"""Convert all cls files to csv."""
	# Create csv folder if path doesn't exist
	if not os.path.exists(target):
		os.mkdir(target)

	files = glob.glob(src + "/*.xls")
	for x in files:
		c = target + "/" + x.split("/")[-1].replace(".xls", ".csv")

		logger.info("%s -> %s" % (x, c))

		try:
			convert_xls_to_csv(x, c, headers)
		except Exception as e:
			logger.error("Failed: " + str(e))


def combine_csvs(src, master, headers, filters=False):
	"""Combine multiple CSVs to one."""
	out = open(master, "w")
	writer = csv.writer(out)

	# Add abbreviation to header
	headers.append("ABBREVIATION")

	writer.writerow(headers)

	files = glob.glob(src + "/*.csv")
	for fname in files:
		logging.info("processing file: {}".format(fname))
		with open(fname, "r") as f:
			reader = csv.reader(f)

			# Skip the header.
			next(reader)
			for row in reader:
				row.append(fname)
				writer.writerow(clean_row(row, filters=filters))


def clean_row(row, filters=False):
	"""Clean a single row from the CSV."""
	# Load map of bank abbrivations
	bank_map = load_json(banks_list_filename)

	row = [r.strip() for r in row]
	row = [spaces.sub(" ", r) for r in row]

	# Bank name
	row[0] = clean_name(clean_line(row[0]), bank_map)

	# IFSC.
	row[1] = row[1].upper()

	# MICR.
	if len(row[2]) > 5:
		try:
			row[2] = str(int(float(row[2])))
		except:
			row[2] = ""
	else:
		row[2] = ""

	# Branch.
	row[3] = clean_line(row[3], complicated=True)

	# Extract the pincode from the address.
	pincode = pin.findall(row[4])
	if len(pincode) > 0:
		pincode = pincode[0].replace(" ", "")

		# Remove the pincode.
		row[4] = pin.sub("", row[4]).strip()
	else:
		# Didn't find a 6 digit pin; check if there's a 2 digit one.
		pincode = pin_small.findall(row[4])
		if len(pincode) > 0:
			pincode = pincode[0][1]

			# Remove the pincode.
			row[4] = pin_small.sub("", row[4]).strip()
		else:
			pincode = ""

	# Address.
	row[4] = clean_line(row[4], complicated=True)

	# Contact
	if len(row[5]) < 6:
		row[5] = ""

	# City, district, state.
	row[6] = clean_line(row[6], True)
	row[7] = clean_line(row[7], True)

	if len(alphanumeric.sub("", row[7])) < 4:
		row[7] = row[6]

	row[8] = clean_line(row[8])

	# Reattach pin to the address.
	if pincode:
		row[4] += " - " + pincode

	# Add abbreviation
	row[9] = get_abbreviation(clean_line(row[0]), bank_map)

	# clean fields
	if filters:
		filters_map = load_json(filters_filename)
		# Apply replace filter
		row = apply_replace_filter(row, filters_map["replace"])

	return row


def clean_line(line, complicated=False):
	"""Try and clean up malformatted words, especially addresses."""
	# Remove duplicate punctuations.
	line = punctuations.sub("\\1", line.strip())

	# Uppercase potential abbreviations.
	chunks = line.split(" ")
	for n, c in enumerate(chunks):
		if len(alphanumeric.sub("", c)) >= 3 and c not in exclude_words:
			chunks[n] = c.title()
		else:
			chunks[n] = c.upper()

	line = " ".join(chunks)

	if complicated:
		# ADDRESS.
		# Fix 'No' (number).
		line = nom.sub("\\1No: ", line)
		line = dnom.sub("\\1Door No:", line)
		line = opp.sub("\\1Opp: ", line)

		# Postbox.
		line = pb.sub("\\1Post Box ", line)
		line = po.sub("\\1Post Office ", line)

		# 'Dist' prefix.
		line = dist.sub("\\1", line)
		# RBO.
		line = rbo.sub("Regional Business Office", line)

		# "Pin" suffix.
		line = pin_text.sub("", line)

		# Remove duplicate words.
		chunks = line.split(",")
		line = ",".join(sorted(set(chunks), key=lambda x: chunks.index(x)))

		# Number suffix casing.
		line = number_suffix.sub(lambda s: s.group(0).lower(), line)

	# Remove extra spaces.
	line = spaces.sub(" ", line)

	# Fix the commas.
	line = ", ".join([l.strip() for l in line.split(",")])

	# Fix brackets.
	line = brackets.sub("\\1 (\\3)", line)

	# Dangling punctuations.
	chunks = line.split(" ")
	chunks2 = []
	for c in chunks:
		c = c.strip()
		if len(c) > 1 and not dangling_punctuations.match(c):
			chunks2.append(dangling_punctuations.sub("", c))

	line = " ".join(chunks2)

	# Trailing punctuations.
	line = trailing_punctuations.sub("", line)

	# fix caps 'OF'
	line = line.replace(" OF ", " of ")

	return line


def clean_name(name, bank_map):
	"""Clean bank name by properly capitalizing the name"""
	name = name.upper()
	abbreviation = bank_map.get(name, "")

	cleaned_name = ""
	for s in name.split(" "):
		if s == abbreviation:
			cleaned_name += s + " "
		elif s == "OF":
			cleaned_name += "of "
		else:
			cleaned_name += s[:1].upper() + s[1:].lower() + " "

	return cleaned_name.strip()


def get_abbreviation(name, bank_map):
	"""Get abbreviation for given bank name"""
	return bank_map.get(name.upper(), "")


def load_json(file_path):
	"""Load json file as dict"""
	path = os.path.normpath(os.path.join(module_path, file_path))
	with open(path, "r") as f:
		return json.load(f)


def apply_replace_filter(row, filters_map):
	"""Apply string replace filter. Currently supports only wildcard string replace"""
	for c in filters_map:
		pattern, source_str, replace_str = c
		if pattern == "*":
			# Combine all the fields in rown, replace the string and again split the string to row
			row = "|".join(row).replace(source_str, replace_str).strip().split("|")
		else:
			# Todo
			pass

	return row
