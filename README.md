### RBI Parser:

A utility for downloading, parsing and sanitizing bank database (IFSC, MICR, address etc.) Excel sheets from the [RBI website](https://www.rbi.org.in/scripts/bs_viewcontent.aspx?Id=2009).

## Installalation:
`pip install rbiparser`

## Usage:
```shell

# Download the Excel files from the RBI website.
rbiparser download -d "./xls"

# Convert the downloaded files to CSV.
rbiparser convert  -s "./xls" -d "./csv"

# Combine the CSV records into one master file.
rbiparser combine -s "./csv" -d "data.csv"

# Help for individual command
rbiparser combine --help

# Apply advanced clean filters
rbiparser combine -s "./csv" -d "data.csv" -f
```
