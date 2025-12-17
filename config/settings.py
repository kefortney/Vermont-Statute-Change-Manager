"""
Configuration settings for Vermont Statute Change Manager
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
PDF_DIR = os.path.join(DATA_DIR, 'pdfs')
XML_DIR = os.path.join(DATA_DIR, 'xml')

# Create directories if they don't exist
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(XML_DIR, exist_ok=True)

# Vermont Legislature URLs
BASE_URL = "https://legislature.vermont.gov"
STATUTES_URL = f"{BASE_URL}/statutes/"
BILLS_URL = f"{BASE_URL}/bills/"
ACTS_URL = f"{BASE_URL}/acts/"

# Scraping settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

# User agent for requests
USER_AGENT = "Vermont-Statute-Change-Manager/1.0 (Educational/Research Purpose)"
