"""
PDF parser for extracting text and metadata from PDFs
"""
import os
from datetime import datetime
import pdfplumber
from PyPDF2 import PdfReader
from src.utils import setup_logger


class PDFParser:
    """
    Parse PDF files and extract text content and metadata
    """
    
    def __init__(self):
        """Initialize the PDF parser"""
        self.logger = setup_logger("pdf_parser")
    
    def parse_pdf(self, pdf_path, document_type=None):
        """
        Parse a PDF file and extract text and metadata
        
        Args:
            pdf_path: Path to the PDF file
            document_type: Type of document (statute, bill, act)
        
        Returns:
            Dictionary containing text and metadata
        """
        if not os.path.exists(pdf_path):
            self.logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        try:
            self.logger.info(f"Parsing PDF: {pdf_path}")
            
            # Extract basic metadata using PyPDF2
            metadata = self._extract_metadata(pdf_path)
            
            # Extract text using pdfplumber
            text_content = self._extract_text(pdf_path)
            
            # Combine results
            result = {
                'pdf_path': pdf_path,
                'filename': os.path.basename(pdf_path),
                'document_type': document_type,
                'metadata': metadata,
                'text_content': text_content,
                'parsed_date': datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully parsed PDF: {pdf_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error parsing PDF {pdf_path}: {e}")
            return None
    
    def _extract_metadata(self, pdf_path):
        """
        Extract metadata from PDF using PyPDF2
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                
                # Get number of pages
                metadata['num_pages'] = len(reader.pages)
                
                # Get PDF metadata
                if reader.metadata:
                    for key, value in reader.metadata.items():
                        # Clean up metadata keys
                        clean_key = key.replace('/', '').lower()
                        metadata[clean_key] = str(value) if value else None
        
        except Exception as e:
            self.logger.warning(f"Error extracting metadata from {pdf_path}: {e}")
        
        return metadata
    
    def _extract_text(self, pdf_path):
        """
        Extract text from PDF using pdfplumber
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text as string
        """
        text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num} ---\n"
                            text += page_text
                    except Exception as e:
                        self.logger.warning(f"Error extracting text from page {page_num}: {e}")
        
        except Exception as e:
            self.logger.warning(f"Error extracting text from {pdf_path}: {e}")
        
        return text.strip()
