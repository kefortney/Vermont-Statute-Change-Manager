# Vermont Statute Change Manager

A Python-based tool for scraping, downloading, and converting Vermont legislative documents (statutes, bills, and acts) from the [Vermont Legislature website](https://legislature.vermont.gov/) into XML format with structured metadata.

## Features

- **Web Scraping**: Automated scraping of PDFs from the Vermont Legislature website
- **Document Types**: Supports three document types with specialized handling:
  - **Statutes**: Vermont state statutes with title and chapter information
  - **Bills**: Legislative bills with bill numbers and session years
  - **Acts**: Enacted legislation with act numbers and enactment dates
- **PDF to XML Conversion**: Converts downloaded PDFs to structured XML format
- **Metadata Extraction**: Extracts and preserves document metadata specific to each document type
- **Robust Error Handling**: Includes retry logic and comprehensive logging

## Project Structure

```
Vermont-Statute-Change-Manager/
├── config/                  # Configuration settings
│   ├── __init__.py
│   └── settings.py         # URLs, paths, and scraping settings
├── src/
│   ├── __init__.py
│   ├── scrapers/           # Web scrapers for different document types
│   │   ├── __init__.py
│   │   ├── base_scraper.py     # Base scraper class
│   │   ├── statute_scraper.py  # Statute-specific scraper
│   │   ├── bill_scraper.py     # Bill-specific scraper
│   │   └── act_scraper.py      # Act-specific scraper
│   ├── converters/         # PDF to XML converters
│   │   ├── __init__.py
│   │   ├── pdf_parser.py       # PDF text and metadata extraction
│   │   └── xml_generator.py    # XML generation with metadata
│   └── utils/              # Utility functions
│       ├── __init__.py
│       └── logger.py           # Logging utilities
├── data/
│   ├── pdfs/               # Downloaded PDF files (organized by type)
│   └── xml/                # Generated XML files (organized by type)
├── main.py                 # Main CLI entry point
├── requirements.txt        # Python dependencies
├── .gitignore
├── LICENSE
└── README.md

```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kefortney/Vermont-Statute-Change-Manager.git
cd Vermont-Statute-Change-Manager
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Scrape and convert statutes:
```bash
python main.py statute
```

Scrape and convert bills:
```bash
python main.py bill
```

Scrape and convert acts:
```bash
python main.py act
```

Scrape and convert all document types:
```bash
python main.py all
```

### Advanced Options

Limit the number of downloads:
```bash
python main.py statute --limit 10
```

Skip XML conversion (download PDFs only):
```bash
python main.py bill --no-convert
```

Enable verbose logging:
```bash
python main.py act --verbose
```

### Command-Line Arguments

```
positional arguments:
  document_type         Type of document to scrape (statute, bill, act, all)

optional arguments:
  -h, --help           Show help message and exit
  --limit LIMIT        Maximum number of PDFs to download (default: all)
  --no-convert         Skip PDF to XML conversion
  --verbose            Enable verbose logging
```

## XML Output Format

The tool generates XML files with metadata structures specific to each document type:

### Statute XML Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<statute xmlns="http://legislature.vermont.gov/statute">
  <metadata>
    <document_type>statute</document_type>
    <source_file>statute_example.pdf</source_file>
    <parsed_date>2025-01-01T12:00:00</parsed_date>
    <title>Title 1 - General Provisions</title>
    <source_url>https://legislature.vermont.gov/statutes/...</source_url>
    <statute_title>Title 1</statute_title>
    <pdf_metadata>
      <num_pages>50</num_pages>
      <pdf_title>Vermont Statutes</pdf_title>
      <creation_date>2024-01-01</creation_date>
    </pdf_metadata>
  </metadata>
  <content>
    <full_text>...</full_text>
  </content>
</statute>
```

### Bill XML Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<bill xmlns="http://legislature.vermont.gov/bill">
  <metadata>
    <document_type>bill</document_type>
    <source_file>bill_H123.pdf</source_file>
    <parsed_date>2025-01-01T12:00:00</parsed_date>
    <title>H.123 - An act relating to...</title>
    <source_url>https://legislature.vermont.gov/bills/...</source_url>
    <bill_number>H.123</bill_number>
    <session_year>2024</session_year>
    <pdf_metadata>
      <num_pages>15</num_pages>
    </pdf_metadata>
  </metadata>
  <content>
    <full_text>...</full_text>
  </content>
</bill>
```

### Act XML Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<act xmlns="http://legislature.vermont.gov/act">
  <metadata>
    <document_type>act</document_type>
    <source_file>act_No_42.pdf</source_file>
    <parsed_date>2025-01-01T12:00:00</parsed_date>
    <title>Act No. 42</title>
    <source_url>https://legislature.vermont.gov/acts/...</source_url>
    <act_number>Act No. 42</act_number>
    <enactment_year>2024</enactment_year>
    <pdf_metadata>
      <num_pages>25</num_pages>
    </pdf_metadata>
  </metadata>
  <content>
    <full_text>...</full_text>
  </content>
</act>
```

## Configuration

Settings can be modified in `config/settings.py`:

- **URLs**: Base URLs for different document types
- **Directories**: Output paths for PDFs and XML files
- **Scraping Settings**: Request timeout, retry attempts, user agent
- **Rate Limiting**: Delay between requests

## Dependencies

- `requests` - HTTP library for web scraping
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser
- `PyPDF2` - PDF metadata extraction
- `pdfplumber` - PDF text extraction
- `python-dateutil` - Date parsing utilities

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is intended for educational and research purposes. Please respect the Vermont Legislature website's terms of service and use reasonable rate limiting when scraping. Always verify the accuracy of scraped and converted data against original sources.