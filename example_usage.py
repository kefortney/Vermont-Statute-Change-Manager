#!/usr/bin/env python3
"""
Example usage of the Vermont Statute Change Manager
This demonstrates how to use the scrapers and converters programmatically
"""
import os
from src.scrapers import StatuteScraper, BillScraper, ActScraper
from src.converters import PDFParser, XMLGenerator
from src.utils import setup_logger


def example_statute_scraping():
    """Example of scraping statutes"""
    print("\n" + "="*70)
    print("Example 1: Scraping Statutes")
    print("="*70)
    
    # Initialize scraper
    scraper = StatuteScraper()
    logger = setup_logger("example")
    
    # Scrape a limited number of PDFs (for testing)
    logger.info("Starting statute scraping (limited to 2 PDFs)...")
    downloaded = scraper.scrape(limit=2)
    
    if downloaded:
        logger.info(f"Successfully downloaded {len(downloaded)} statute PDFs")
        for pdf_path, metadata in downloaded:
            logger.info(f"  - {os.path.basename(pdf_path)}")
            logger.info(f"    Title: {metadata.get('title', 'N/A')}")
    else:
        logger.info("No statutes downloaded (this is expected if website structure has changed)")
    
    return downloaded


def example_pdf_to_xml_conversion(pdf_path, metadata, document_type):
    """Example of converting PDF to XML"""
    print("\n" + "="*70)
    print("Example 2: Converting PDF to XML")
    print("="*70)
    
    logger = setup_logger("example")
    
    # Initialize converters
    pdf_parser = PDFParser()
    xml_generator = XMLGenerator()
    
    # Parse PDF
    logger.info(f"Parsing PDF: {os.path.basename(pdf_path)}")
    parsed_data = pdf_parser.parse_pdf(pdf_path, document_type)
    
    if parsed_data:
        logger.info("PDF parsed successfully")
        logger.info(f"  Pages: {parsed_data.get('metadata', {}).get('num_pages', 'N/A')}")
        logger.info(f"  Text length: {len(parsed_data.get('text_content', ''))} characters")
        
        # Generate XML
        logger.info("Generating XML...")
        xml_path = xml_generator.generate_xml(parsed_data, metadata)
        
        if xml_path:
            logger.info(f"XML generated successfully: {xml_path}")
            return xml_path
        else:
            logger.error("Failed to generate XML")
    else:
        logger.error("Failed to parse PDF")
    
    return None


def example_all_document_types():
    """Example of handling all document types"""
    print("\n" + "="*70)
    print("Example 3: All Document Types")
    print("="*70)
    
    logger = setup_logger("example")
    
    document_types = [
        ("Statutes", StatuteScraper()),
        ("Bills", BillScraper()),
        ("Acts", ActScraper())
    ]
    
    for doc_name, scraper in document_types:
        logger.info(f"\nDocument type: {doc_name}")
        logger.info(f"  Base URL: {scraper.base_url}")
        logger.info(f"  Output directory: {scraper.output_dir}")


def main():
    """Run examples"""
    print("\n" + "="*70)
    print("Vermont Statute Change Manager - Usage Examples")
    print("="*70)
    
    # Example 1: Scrape statutes
    downloaded = example_statute_scraping()
    
    # Example 2: Convert PDF to XML (if we downloaded any)
    if downloaded:
        pdf_path, metadata = downloaded[0]
        example_pdf_to_xml_conversion(pdf_path, metadata, 'statute')
    
    # Example 3: Show all document types
    example_all_document_types()
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)
    print("\nTo use the CLI:")
    print("  python main.py statute --limit 5")
    print("  python main.py bill --limit 5")
    print("  python main.py act --limit 5")
    print("  python main.py all")
    print()


if __name__ == '__main__':
    main()
