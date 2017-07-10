import click
import rbiparser as rbi

SOURCE_URL = "https://www.rbi.org.in/scripts/bs_viewcontent.aspx?Id=2009"


@click.group()
def cli():
	"""
	Rbiparser command line utility
	"""


@cli.command()
@click.option('-s', '--source', type=click.STRING, default=SOURCE_URL,
	help="Source url to download documents. Defaults to RBI data source.")
@click.option('-d', '--dest', type=click.Path(dir_okay=True), default="xls",
	help="Download destination directory.")
@click.option('-e', '--etag', type=click.Path(file_okay=True), default="etags.json",
	help="Etags file")
def download(source, dest, etag):
	"""Download all listed bank documents from RBI as .xls format."""
	rbi.download_all(source, dest, etag)


@cli.command()
@click.option('-s', '--source', type=click.Path(dir_okay=True, exists=True), default="xls",
	help="xls documents directory")
@click.option('-d', '--dest', type=click.Path(dir_okay=True), default="csv",
	help="Target directory for CSV files.")
def convert(source, dest):
	"""Convert all xls documents to CSV"""
	rbi.convert_all(source, dest, rbi.HEADERS)


@cli.command()
@click.option('-s', '--source', type=click.Path(dir_okay=True, exists=True), default="csv",
	help="CSV files directory")
@click.option('-d', '--dest', type=click.Path(), default="data.csv",
	help="Name of the combined csv file.")
@click.option('-f', '--filters', type=click.BOOL, default=False, is_flag=True,
	help="Apply advanced filters to clean the data")
def combine(source, dest, filters):
	"""Combine and clean all the indivdual CSV files"""
	rbi.combine_csvs(source, dest, rbi.HEADERS, filters)
