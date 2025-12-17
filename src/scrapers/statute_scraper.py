"""
Scraper for Vermont statutes
"""
from urllib.parse import urljoin
from config.settings import STATUTES_URL
from .base_scraper import BaseScraper


class StatuteScraper(BaseScraper):
    """
    Scraper for Vermont statutes from legislature.vermont.gov
    """
    
    def __init__(self):
        """Initialize the statute scraper"""
        super().__init__(STATUTES_URL, "statute")
    
    def find_pdf_links(self, soup):
        """
        Find PDF links for statutes in the page
        
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
                    'type': 'statute',
                    'link_text': link.get_text(strip=True)
                }
                
                # Try to extract statute number from title or URL
                text = title.lower()
                if 'title' in text:
                    metadata['statute_title'] = title
                
                pdf_links.append((pdf_url, metadata))
        
        return pdf_links
    
    def scrape(self, limit=None):
        """
        Scrape statute PDFs from Vermont Legislature website
        
        Args:
            limit: Maximum number of PDFs to download (None for all)
        
        Returns:
            List of tuples (filepath, metadata)
        """
        self.logger.info(f"Starting statute scraper for {self.base_url}")
        
        # Fetch the main statutes page
        response = self.fetch_page(self.base_url)
        if not response:
            self.logger.error("Failed to fetch main statutes page")
            return []
        
        # Parse the page
        soup = self.parse_page(response.content)
        
        # Find all PDF links
        pdf_links = self.find_pdf_links(soup)
        self.logger.info(f"Found {len(pdf_links)} statute PDF links")
        
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
        
        self.logger.info(f"Successfully downloaded {len(downloaded)} statute PDFs")
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
        # Try to create a meaningful filename
        title = metadata.get('title', 'statute')
        # Remove invalid characters
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        
        if safe_title:
            return f"statute_{safe_title}_{index}.pdf"
        return f"statute_{index}.pdf"
