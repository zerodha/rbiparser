"""A utility for downloading, parsing and sanitizing bank database Excel sheets from the RBI website."""

import argparse
import rbiparser as rbi

SOURCE_URL = "https://www.rbi.org.in/scripts/bs_viewcontent.aspx?Id=2009"


def run():
	"""Run the rbiparser library as a console program."""
	parser = argparse.ArgumentParser(description="RBI IFSC db scraper + parser")

	parser.add_argument("-a", help="Action", required=True, type=str, dest="action", choices=["download", "convert", "combine"])
	parser.add_argument("-xls", help="Diretory to write xls files", default="xls", type=str, dest="xls")
	parser.add_argument("-csv", help="Diretory to write csv files", default="csv", type=str, dest="csv")
	parser.add_argument("-etags", help="Path to the etags.json file", type=str, dest="etags", default="etags.json")
	parser.add_argument("-master", help="Path to the parsed, cleaned, and combined master csv file", required=False, type=str, dest="master", default="master.csv")
	parser.add_argument("-source", help="Full URL to the RBI page where the Excel sheets are listed", required=False, type=str, dest="source", default=SOURCE_URL)

	try:
		args = parser.parse_args()
	except Exception as e:
		print(str(e))

	if args.action == "download":
		rbi.download_all(args.source, args.xls, args.etags)
	elif args.action == "convert":
		rbi.convert_all(args.xls, args.csv, rbi.HEADERS)
	elif args.action == "combine":
		rbi.combine_csvs(args.csv, args.master, rbi.HEADERS)

if __name__ == "__main__":
	run()
