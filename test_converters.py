#!/usr/bin/env python3
"""
Test script for converters without needing actual PDFs from the website
"""
import os
import sys
from datetime import datetime
from src.converters import XMLGenerator
from src.utils import setup_logger


def test_xml_generation():
    """Test XML generation with mock data"""
    logger = setup_logger("test")
    logger.info("Testing XML generation with mock data...")
    
    xml_generator = XMLGenerator()
    
    # Test data for each document type
    test_cases = [
        {
            'document_type': 'statute',
            'parsed_data': {
                'pdf_path': '/fake/path/statute_example.pdf',
                'filename': 'statute_example.pdf',
                'document_type': 'statute',
                'metadata': {
                    'num_pages': 10,
                    'title': 'Vermont Statutes - Title 1',
                    'author': 'Vermont Legislature',
                    'creator': 'PDF Creator',
                    'creationdate': '2024-01-01'
                },
                'text_content': 'This is sample statute text content...',
                'parsed_date': datetime.now().isoformat()
            },
            'scraper_metadata': {
                'url': 'https://legislature.vermont.gov/statutes/title/01',
                'title': 'Title 1 - General Provisions',
                'type': 'statute',
                'statute_title': 'Title 1'
            }
        },
        {
            'document_type': 'bill',
            'parsed_data': {
                'pdf_path': '/fake/path/bill_H123.pdf',
                'filename': 'bill_H123.pdf',
                'document_type': 'bill',
                'metadata': {
                    'num_pages': 5,
                    'title': 'H.123 - An act relating to education',
                    'creationdate': '2024-02-01'
                },
                'text_content': 'This is sample bill text content...',
                'parsed_date': datetime.now().isoformat()
            },
            'scraper_metadata': {
                'url': 'https://legislature.vermont.gov/bills/H.123',
                'title': 'H.123 - An act relating to education',
                'type': 'bill',
                'bill_number': 'H.123',
                'year': '2024'
            }
        },
        {
            'document_type': 'act',
            'parsed_data': {
                'pdf_path': '/fake/path/act_No_42.pdf',
                'filename': 'act_No_42.pdf',
                'document_type': 'act',
                'metadata': {
                    'num_pages': 8,
                    'title': 'Act No. 42',
                    'creationdate': '2024-03-01'
                },
                'text_content': 'This is sample act text content...',
                'parsed_date': datetime.now().isoformat()
            },
            'scraper_metadata': {
                'url': 'https://legislature.vermont.gov/acts/42',
                'title': 'Act No. 42 - An act relating to transportation',
                'type': 'act',
                'act_number': 'Act No. 42',
                'year': '2024'
            }
        }
    ]
    
    # Generate XML for each test case
    results = []
    for test_case in test_cases:
        doc_type = test_case['document_type']
        logger.info(f"\nTesting {doc_type} XML generation...")
        
        xml_path = xml_generator.generate_xml(
            test_case['parsed_data'],
            test_case['scraper_metadata']
        )
        
        if xml_path:
            logger.info(f"✓ Successfully generated {doc_type} XML: {xml_path}")
            
            # Verify file exists and has content
            if os.path.exists(xml_path):
                file_size = os.path.getsize(xml_path)
                logger.info(f"  File size: {file_size} bytes")
                
                # Read and display first few lines
                with open(xml_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:10]
                    logger.info(f"  First lines of XML:")
                    for line in lines:
                        logger.info(f"    {line.rstrip()}")
                
                results.append((doc_type, xml_path, True))
            else:
                logger.error(f"✗ XML file not found: {xml_path}")
                results.append((doc_type, xml_path, False))
        else:
            logger.error(f"✗ Failed to generate {doc_type} XML")
            results.append((doc_type, None, False))
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("Test Summary")
    logger.info("="*70)
    
    success_count = sum(1 for _, _, success in results if success)
    total_count = len(results)
    
    for doc_type, xml_path, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status}: {doc_type} XML generation")
    
    logger.info(f"\nResults: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        logger.info("\n✓ All tests passed!")
        return 0
    else:
        logger.error("\n✗ Some tests failed")
        return 1


def main():
    """Run tests"""
    print("\n" + "="*70)
    print("Vermont Statute Change Manager - Converter Tests")
    print("="*70)
    
    result = test_xml_generation()
    
    print("\n" + "="*70)
    print("Tests completed!")
    print("="*70)
    
    return result


if __name__ == '__main__':
    sys.exit(main())
