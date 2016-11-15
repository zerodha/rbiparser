#!/usr/bin/env python

from setuptools import setup

setup(
	name="rbiparser",
	version="0.01",
	description="A utility for downloading, parsing and sanitizing bank database Excel sheets from the RBI website",
	author="Kailash Nadh",
	author_email="kailash@nadh.in",
	url="https://github.com/knadh/rbiparser",
	packages=['rbiparser'],
	download_url="https://github.com/knadh/rbiparser",
	license="MIT License",
	entry_points={
		'console_scripts': [
			'rbiparser = rbiparser.console:run'
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
	install_requires=["requests", "xlrd"]
)
