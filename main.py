#!/usr/bin/env python3
"""
Vermont Statute Change Manager
Main entry point for scraping and converting Vermont legislature documents
"""
import argparse
import logging
import sys
from src.scrapers import StatuteScraper, BillScraper, ActScraper
from src.converters import PDFParser, XMLGenerator
from src.utils import setup_logger


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Vermont Statute Change Manager - Scrape and convert legislature documents'
    )
    parser.add_argument(
        'document_type',
        choices=['statute', 'bill', 'act', 'all'],
        help='Type of document to scrape'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of PDFs to download (default: all)'
    )
    parser.add_argument(
        '--no-convert',
        action='store_true',
        help='Skip PDF to XML conversion'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger('main', log_level)
    
    logger.info("Vermont Statute Change Manager started")
    logger.info(f"Document type: {args.document_type}")
    if args.limit:
        logger.info(f"Download limit: {args.limit}")
    
    # Determine which scrapers to run
    scrapers = []
    if args.document_type == 'all':
        scrapers = [
            ('statute', StatuteScraper()),
            ('bill', BillScraper()),
            ('act', ActScraper())
        ]
    elif args.document_type == 'statute':
        scrapers = [('statute', StatuteScraper())]
    elif args.document_type == 'bill':
        scrapers = [('bill', BillScraper())]
    elif args.document_type == 'act':
        scrapers = [('act', ActScraper())]
    
    # Initialize converters if needed
    pdf_parser = None
    xml_generator = None
    if not args.no_convert:
        pdf_parser = PDFParser()
        xml_generator = XMLGenerator()
    
    # Run scrapers
    total_downloaded = 0
    total_converted = 0
    
    for doc_type, scraper in scrapers:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {doc_type}s")
        logger.info(f"{'='*60}")
        
        # Scrape PDFs
        downloaded = scraper.scrape(limit=args.limit)
        total_downloaded += len(downloaded)
        
        logger.info(f"Downloaded {len(downloaded)} {doc_type} PDFs")
        
        # Convert to XML if enabled
        if not args.no_convert and downloaded:
            logger.info(f"Converting {doc_type} PDFs to XML...")
            
            for pdf_path, metadata in downloaded:
                try:
                    # Parse PDF
                    parsed_data = pdf_parser.parse_pdf(pdf_path, doc_type)
                    if parsed_data:
                        # Generate XML
                        xml_path = xml_generator.generate_xml(parsed_data, metadata)
                        if xml_path:
                            total_converted += 1
                            logger.debug(f"Created XML: {xml_path}")
                except Exception as e:
                    logger.error(f"Error converting {pdf_path}: {e}")
            
            logger.info(f"Converted {total_converted} {doc_type} PDFs to XML")
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("Summary")
    logger.info(f"{'='*60}")
    logger.info(f"Total PDFs downloaded: {total_downloaded}")
    if not args.no_convert:
        logger.info(f"Total XMLs created: {total_converted}")
    logger.info("Vermont Statute Change Manager completed")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
