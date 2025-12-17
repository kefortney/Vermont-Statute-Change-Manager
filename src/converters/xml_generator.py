"""
XML generator for converting PDF data to XML with metadata
"""
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from config.settings import XML_DIR
from src.utils import setup_logger


class XMLGenerator:
    """
    Generate XML files from parsed PDF data with appropriate metadata structure
    """
    
    def __init__(self):
        """Initialize the XML generator"""
        self.logger = setup_logger("xml_generator")
        
        # Directory name mapping for document types
        self.dir_mapping = {
            'statute': 'statutes',
            'bill': 'bills',
            'act': 'acts'
        }
        
        # Ensure XML output directories exist
        for dir_name in self.dir_mapping.values():
            os.makedirs(os.path.join(XML_DIR, dir_name), exist_ok=True)
    
    def generate_xml(self, parsed_data, scraper_metadata=None):
        """
        Generate XML from parsed PDF data
        
        Args:
            parsed_data: Dictionary from PDFParser
            scraper_metadata: Additional metadata from scraper
        
        Returns:
            Path to generated XML file or None if failed
        """
        if not parsed_data:
            self.logger.error("No parsed data provided")
            return None
        
        document_type = parsed_data.get('document_type', 'unknown')
        
        try:
            # Generate XML based on document type
            if document_type == 'statute':
                xml_content = self._generate_statute_xml(parsed_data, scraper_metadata)
            elif document_type == 'bill':
                xml_content = self._generate_bill_xml(parsed_data, scraper_metadata)
            elif document_type == 'act':
                xml_content = self._generate_act_xml(parsed_data, scraper_metadata)
            else:
                self.logger.warning(f"Unknown document type: {document_type}, using generic format")
                xml_content = self._generate_generic_xml(parsed_data, scraper_metadata)
            
            # Save XML file
            output_path = self._save_xml(xml_content, parsed_data, document_type)
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating XML: {e}")
            return None
    
    def _generate_statute_xml(self, parsed_data, scraper_metadata):
        """
        Generate XML for statute documents
        
        Statute-specific metadata includes:
        - Title and chapter information
        - Section numbers
        - Effective dates
        - Amendment history
        """
        root = ET.Element('statute')
        root.set('xmlns', 'http://legislature.vermont.gov/statute')
        
        # Metadata section
        metadata = ET.SubElement(root, 'metadata')
        
        ET.SubElement(metadata, 'document_type').text = 'statute'
        ET.SubElement(metadata, 'source_file').text = parsed_data.get('filename', '')
        ET.SubElement(metadata, 'parsed_date').text = parsed_data.get('parsed_date', '')
        
        if scraper_metadata:
            ET.SubElement(metadata, 'title').text = scraper_metadata.get('title', '')
            ET.SubElement(metadata, 'source_url').text = scraper_metadata.get('url', '')
            if 'statute_title' in scraper_metadata:
                ET.SubElement(metadata, 'statute_title').text = scraper_metadata['statute_title']
        
        # PDF metadata
        pdf_meta = parsed_data.get('metadata', {})
        if pdf_meta:
            pdf_metadata_elem = ET.SubElement(metadata, 'pdf_metadata')
            ET.SubElement(pdf_metadata_elem, 'num_pages').text = str(pdf_meta.get('num_pages', 0))
            if 'title' in pdf_meta and pdf_meta['title']:
                ET.SubElement(pdf_metadata_elem, 'pdf_title').text = pdf_meta['title']
            if 'author' in pdf_meta and pdf_meta['author']:
                ET.SubElement(pdf_metadata_elem, 'author').text = pdf_meta['author']
            if 'creator' in pdf_meta and pdf_meta['creator']:
                ET.SubElement(pdf_metadata_elem, 'creator').text = pdf_meta['creator']
            if 'creationdate' in pdf_meta and pdf_meta['creationdate']:
                ET.SubElement(pdf_metadata_elem, 'creation_date').text = pdf_meta['creationdate']
        
        # Content section
        content = ET.SubElement(root, 'content')
        text_content = parsed_data.get('text_content', '')
        if text_content:
            ET.SubElement(content, 'full_text').text = text_content
        
        return root
    
    def _generate_bill_xml(self, parsed_data, scraper_metadata):
        """
        Generate XML for bill documents
        
        Bill-specific metadata includes:
        - Bill number (H.123, S.456)
        - Session year
        - Sponsors
        - Status and version
        """
        root = ET.Element('bill')
        root.set('xmlns', 'http://legislature.vermont.gov/bill')
        
        # Metadata section
        metadata = ET.SubElement(root, 'metadata')
        
        ET.SubElement(metadata, 'document_type').text = 'bill'
        ET.SubElement(metadata, 'source_file').text = parsed_data.get('filename', '')
        ET.SubElement(metadata, 'parsed_date').text = parsed_data.get('parsed_date', '')
        
        if scraper_metadata:
            ET.SubElement(metadata, 'title').text = scraper_metadata.get('title', '')
            ET.SubElement(metadata, 'source_url').text = scraper_metadata.get('url', '')
            if 'bill_number' in scraper_metadata:
                ET.SubElement(metadata, 'bill_number').text = scraper_metadata['bill_number']
            if 'year' in scraper_metadata:
                ET.SubElement(metadata, 'session_year').text = scraper_metadata['year']
        
        # PDF metadata
        pdf_meta = parsed_data.get('metadata', {})
        if pdf_meta:
            pdf_metadata_elem = ET.SubElement(metadata, 'pdf_metadata')
            ET.SubElement(pdf_metadata_elem, 'num_pages').text = str(pdf_meta.get('num_pages', 0))
            if 'title' in pdf_meta and pdf_meta['title']:
                ET.SubElement(pdf_metadata_elem, 'pdf_title').text = pdf_meta['title']
            if 'author' in pdf_meta and pdf_meta['author']:
                ET.SubElement(pdf_metadata_elem, 'author').text = pdf_meta['author']
            if 'creator' in pdf_meta and pdf_meta['creator']:
                ET.SubElement(pdf_metadata_elem, 'creator').text = pdf_meta['creator']
            if 'creationdate' in pdf_meta and pdf_meta['creationdate']:
                ET.SubElement(pdf_metadata_elem, 'creation_date').text = pdf_meta['creationdate']
        
        # Content section
        content = ET.SubElement(root, 'content')
        text_content = parsed_data.get('text_content', '')
        if text_content:
            ET.SubElement(content, 'full_text').text = text_content
        
        return root
    
    def _generate_act_xml(self, parsed_data, scraper_metadata):
        """
        Generate XML for act documents
        
        Act-specific metadata includes:
        - Act number
        - Enactment date
        - Related bills
        - Effective date
        """
        root = ET.Element('act')
        root.set('xmlns', 'http://legislature.vermont.gov/act')
        
        # Metadata section
        metadata = ET.SubElement(root, 'metadata')
        
        ET.SubElement(metadata, 'document_type').text = 'act'
        ET.SubElement(metadata, 'source_file').text = parsed_data.get('filename', '')
        ET.SubElement(metadata, 'parsed_date').text = parsed_data.get('parsed_date', '')
        
        if scraper_metadata:
            ET.SubElement(metadata, 'title').text = scraper_metadata.get('title', '')
            ET.SubElement(metadata, 'source_url').text = scraper_metadata.get('url', '')
            if 'act_number' in scraper_metadata:
                ET.SubElement(metadata, 'act_number').text = scraper_metadata['act_number']
            if 'year' in scraper_metadata:
                ET.SubElement(metadata, 'enactment_year').text = scraper_metadata['year']
        
        # PDF metadata
        pdf_meta = parsed_data.get('metadata', {})
        if pdf_meta:
            pdf_metadata_elem = ET.SubElement(metadata, 'pdf_metadata')
            ET.SubElement(pdf_metadata_elem, 'num_pages').text = str(pdf_meta.get('num_pages', 0))
            if 'title' in pdf_meta and pdf_meta['title']:
                ET.SubElement(pdf_metadata_elem, 'pdf_title').text = pdf_meta['title']
            if 'author' in pdf_meta and pdf_meta['author']:
                ET.SubElement(pdf_metadata_elem, 'author').text = pdf_meta['author']
            if 'creator' in pdf_meta and pdf_meta['creator']:
                ET.SubElement(pdf_metadata_elem, 'creator').text = pdf_meta['creator']
            if 'creationdate' in pdf_meta and pdf_meta['creationdate']:
                ET.SubElement(pdf_metadata_elem, 'creation_date').text = pdf_meta['creationdate']
        
        # Content section
        content = ET.SubElement(root, 'content')
        text_content = parsed_data.get('text_content', '')
        if text_content:
            ET.SubElement(content, 'full_text').text = text_content
        
        return root
    
    def _generate_generic_xml(self, parsed_data, scraper_metadata):
        """
        Generate generic XML for unknown document types
        """
        root = ET.Element('document')
        
        # Metadata section
        metadata = ET.SubElement(root, 'metadata')
        ET.SubElement(metadata, 'document_type').text = parsed_data.get('document_type', 'unknown')
        ET.SubElement(metadata, 'source_file').text = parsed_data.get('filename', '')
        ET.SubElement(metadata, 'parsed_date').text = parsed_data.get('parsed_date', '')
        
        if scraper_metadata:
            for key, value in scraper_metadata.items():
                if value:
                    ET.SubElement(metadata, key).text = str(value)
        
        # Content section
        content = ET.SubElement(root, 'content')
        text_content = parsed_data.get('text_content', '')
        if text_content:
            ET.SubElement(content, 'full_text').text = text_content
        
        return root
    
    def _save_xml(self, root, parsed_data, document_type):
        """
        Save XML to file with pretty formatting
        
        Args:
            root: XML root element
            parsed_data: Parsed data dictionary
            document_type: Type of document
        
        Returns:
            Path to saved XML file
        """
        # Generate filename
        original_filename = parsed_data.get('filename', 'document.pdf')
        base_name = os.path.splitext(original_filename)[0]
        xml_filename = f"{base_name}.xml"
        
        # Determine output directory using mapping
        if document_type in self.dir_mapping:
            output_dir = os.path.join(XML_DIR, self.dir_mapping[document_type])
        else:
            output_dir = XML_DIR
        
        output_path = os.path.join(output_dir, xml_filename)
        
        # Convert to pretty-printed string
        xml_string = ET.tostring(root, encoding='utf-8')
        dom = minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8')
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(pretty_xml)
        
        self.logger.info(f"Saved XML to: {output_path}")
        return output_path
