# rbiparser

A utility for downloading, parsing and sanitizing bank database (IFSC, MICR, address etc.) Excel sheets from the [RBI website](https://www.rbi.org.in/scripts/bs_viewcontent.aspx?Id=2009).

### Installation.
`pip install rbiparser`

### Usage:
```shell
# Download the Excel files from the RBI website.
python rbi.py -a download

# Convert the downloaded files to CSV.
python rbi.py -a convert

# Combine the CSV records into one master file.
python rbi.py -a combine -master all.csv
```
