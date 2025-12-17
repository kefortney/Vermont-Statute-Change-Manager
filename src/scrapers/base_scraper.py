"""
Base scraper class for Vermont Legislature website
"""
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config.settings import (
    REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY, USER_AGENT, PDF_DIR
)
from src.utils import setup_logger


class BaseScraper:
    """
    Base class for scraping Vermont Legislature website
    """
    
    # Directory name mapping for document types (singular to plural)
    DIR_MAPPING = {
        'statute': 'statutes',
        'bill': 'bills',
        'act': 'acts'
    }
    
    def __init__(self, base_url, document_type):
        """
        Initialize the scraper
        
        Args:
            base_url: Base URL for the document type
            document_type: Type of document (statute, bill, act) - singular form
        """
        self.base_url = base_url
        self.document_type = document_type
        self.logger = setup_logger(f"{document_type}_scraper")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
        
        # Create subdirectory for this document type using mapping
        dir_name = self.DIR_MAPPING.get(document_type, document_type)
        self.output_dir = os.path.join(PDF_DIR, dir_name)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def fetch_page(self, url):
        """
        Fetch a web page with retry logic
        
        Args:
            url: URL to fetch
        
        Returns:
            Response object or None if failed
        """
        for attempt in range(MAX_RETRIES):
            try:
                self.logger.info(f"Fetching {url} (attempt {attempt + 1}/{MAX_RETRIES})")
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                self.logger.warning(f"Error fetching {url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    self.logger.error(f"Failed to fetch {url} after {MAX_RETRIES} attempts")
                    return None
        return None
    
    def download_pdf(self, pdf_url, filename):
        """
        Download a PDF file
        
        Args:
            pdf_url: URL of the PDF
            filename: Filename to save the PDF as
        
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            self.logger.info(f"Downloading PDF: {pdf_url}")
            response = self.fetch_page(pdf_url)
            if not response:
                return None
            
            # Save PDF
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Successfully downloaded: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error downloading PDF {pdf_url}: {e}")
            return None
    
    def parse_page(self, html_content):
        """
        Parse HTML content with BeautifulSoup
        
        Args:
            html_content: HTML content to parse
        
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html_content, 'lxml')
    
    def find_pdf_links(self, soup):
        """
        Find PDF links in a page (to be overridden by subclasses)
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            List of PDF URLs with metadata
        """
        raise NotImplementedError("Subclasses must implement find_pdf_links")
    
    def scrape(self):
        """
        Main scraping method (to be overridden by subclasses)
        
        Returns:
            List of downloaded PDF paths
        """
        raise NotImplementedError("Subclasses must implement scrape")
