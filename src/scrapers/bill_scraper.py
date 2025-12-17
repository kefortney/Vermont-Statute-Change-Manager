"""
Scraper for Vermont bills
"""
import re
from urllib.parse import urljoin
from config.settings import BILLS_URL
from .base_scraper import BaseScraper


class BillScraper(BaseScraper):
    """
    Scraper for Vermont bills from legislature.vermont.gov
    """
    
    def __init__(self):
        """Initialize the bill scraper"""
        super().__init__(BILLS_URL, "bills")
    
    def find_pdf_links(self, soup):
        """
        Find PDF links for bills in the page
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            List of tuples (pdf_url, metadata_dict)
        """
        pdf_links = []
        
        # Find all links that might be PDFs
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf') or '/pdf/' in href.lower():
                # Build full URL
                pdf_url = urljoin(self.base_url, href)
                
                # Extract metadata
                title = link.get_text(strip=True)
                metadata = {
                    'url': pdf_url,
                    'title': title,
                    'type': 'bill',
                    'link_text': link.get_text(strip=True)
                }
                
                # Try to extract bill number from title or URL
                # Bills are typically formatted as H.123 or S.456
                bill_match = re.search(r'[HS]\.?\s*\d+', title, re.IGNORECASE)
                if bill_match:
                    metadata['bill_number'] = bill_match.group(0)
                
                # Try to extract year
                year_match = re.search(r'20\d{2}', href)
                if year_match:
                    metadata['year'] = year_match.group(0)
                
                pdf_links.append((pdf_url, metadata))
        
        return pdf_links
    
    def scrape(self, limit=None):
        """
        Scrape bill PDFs from Vermont Legislature website
        
        Args:
            limit: Maximum number of PDFs to download (None for all)
        
        Returns:
            List of tuples (filepath, metadata)
        """
        self.logger.info(f"Starting bill scraper for {self.base_url}")
        
        # Fetch the main bills page
        response = self.fetch_page(self.base_url)
        if not response:
            self.logger.error("Failed to fetch main bills page")
            return []
        
        # Parse the page
        soup = self.parse_page(response.content)
        
        # Find all PDF links
        pdf_links = self.find_pdf_links(soup)
        self.logger.info(f"Found {len(pdf_links)} bill PDF links")
        
        # Download PDFs
        downloaded = []
        count = 0
        for pdf_url, metadata in pdf_links:
            if limit and count >= limit:
                break
            
            # Generate filename from metadata
            filename = self._generate_filename(metadata, count)
            
            # Download the PDF
            filepath = self.download_pdf(pdf_url, filename)
            if filepath:
                downloaded.append((filepath, metadata))
                count += 1
        
        self.logger.info(f"Successfully downloaded {len(downloaded)} bill PDFs")
        return downloaded
    
    def _generate_filename(self, metadata, index):
        """
        Generate a safe filename for the PDF
        
        Args:
            metadata: Metadata dictionary
            index: Index for uniqueness
        
        Returns:
            Filename string
        """
        # Try to use bill number if available
        bill_num = metadata.get('bill_number', '')
        year = metadata.get('year', '')
        
        if bill_num:
            safe_bill = bill_num.replace('.', '_').replace(' ', '')
            if year:
                return f"bill_{year}_{safe_bill}_{index}.pdf"
            return f"bill_{safe_bill}_{index}.pdf"
        
        # Fallback to title-based name
        title = metadata.get('title', 'bill')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]
        
        if safe_title:
            return f"bill_{safe_title}_{index}.pdf"
        return f"bill_{index}.pdf"
