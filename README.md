# rbiparser

A utility for downloading, parsing and sanitizing bank database (IFSC, MICR, address etc.) Excel sheets from the [RBI website](https://www.rbi.org.in/scripts/bs_viewcontent.aspx?Id=2009).

### Installation.
`pip install rbiparser`

### Usage:
```shell
# Create directories for storing the sheets.
mkdir xls csv

# Download the Excel files from the RBI website.
rbiparser -a download -xls "./xls"

# Convert the downloaded files to CSV.
rbiparser -a convert  -xls "./xls" -csv "./xls"

# Combine the CSV records into one master file.
rbiparser -a combine -xls "./xls" -csv "./xls" -master all.csv
```
