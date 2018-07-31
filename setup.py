#!/usr/bin/env python
from codecs import open
from setuptools import setup

README = open("README.md").read()

setup(
	name="rbiparser",
	version="0.6.1",
	description="A utility for downloading, parsing and sanitizing bank database (IFSC, MICR, address etc.) Excel sheets from the RBI website.",
	long_description=README,
	author="Kailash Nadh",
	author_email="kailash@nadh.in",
	url="https://github.com/zerodhatech/rbiparser",
	packages=['rbiparser'],
	include_package_data=True,
	download_url="https://github.com/zerodhatech/rbiparser",
	license="MIT License",
	entry_points={
		'console_scripts': [
			'rbiparser = rbiparser.console:cli'
		],
	},
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Programming Language :: Python",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 2.6",
		"Programming Language :: Python :: 2.7",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Database",
		"Topic :: Software Development :: Libraries"
	],
	install_requires=["requests", "xlrd", "beautifulsoup4", "click"]
)
