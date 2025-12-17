"""
Scraper for Vermont acts
"""
from urllib.parse import urljoin
from config.settings import ACTS_URL
from .base_scraper import BaseScraper


class ActScraper(BaseScraper):
    """
    Scraper for Vermont acts from legislature.vermont.gov
    """
    
    def __init__(self):
        """Initialize the act scraper"""
        super().__init__(ACTS_URL, "acts")
    
    def find_pdf_links(self, soup):
        """
        Find PDF links for acts in the page
        
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
                    'type': 'act',
                    'link_text': link.get_text(strip=True)
                }
                
                # Try to extract act number from title or URL
                import re
                act_match = re.search(r'Act\s*No\.\s*\d+', title, re.IGNORECASE)
                if act_match:
                    metadata['act_number'] = act_match.group(0)
                
                # Try to extract year
                year_match = re.search(r'20\d{2}', href)
                if year_match:
                    metadata['year'] = year_match.group(0)
                
                pdf_links.append((pdf_url, metadata))
        
        return pdf_links
    
    def scrape(self, limit=None):
        """
        Scrape act PDFs from Vermont Legislature website
        
        Args:
            limit: Maximum number of PDFs to download (None for all)
        
        Returns:
            List of tuples (filepath, metadata)
        """
        self.logger.info(f"Starting act scraper for {self.base_url}")
        
        # Fetch the main acts page
        response = self.fetch_page(self.base_url)
        if not response:
            self.logger.error("Failed to fetch main acts page")
            return []
        
        # Parse the page
        soup = self.parse_page(response.content)
        
        # Find all PDF links
        pdf_links = self.find_pdf_links(soup)
        self.logger.info(f"Found {len(pdf_links)} act PDF links")
        
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
        
        self.logger.info(f"Successfully downloaded {len(downloaded)} act PDFs")
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
        # Try to use act number if available
        act_num = metadata.get('act_number', '')
        year = metadata.get('year', '')
        
        if act_num:
            safe_act = act_num.replace('.', '_').replace(' ', '_')
            if year:
                return f"act_{year}_{safe_act}_{index}.pdf"
            return f"act_{safe_act}_{index}.pdf"
        
        # Fallback to title-based name
        title = metadata.get('title', 'act')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]
        
        if safe_title:
            return f"act_{safe_title}_{index}.pdf"
        return f"act_{index}.pdf"
