#!/usr/bin/env python3
"""
Statute to Akoma Ntoso XML Converter

Converts plain text statutes into Akoma Ntoso 3.0 XML format.
This is a basic converter that handles common legislative structures.
"""

import os
import glob
import re
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
try:
    # Preferred modern library
    from pypdf import PdfReader
except Exception:
    try:
        # Fallback to legacy PyPDF2 if available
        from PyPDF2 import PdfReader
    except Exception:
        PdfReader = None
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None


class AkomaNtosoConverter:
    def __init__(self, jurisdiction="us", state="", date_enacted=""):
        """
        Initialize converter with jurisdiction information.
        
        Args:
            jurisdiction: Country code (default: "us")
            state: State code (e.g., "vt" for Vermont)
            date_enacted: Date in YYYY-MM-DD format
        """
        self.jurisdiction = jurisdiction
        self.state = state
        self.date_enacted = date_enacted or datetime.now().strftime("%Y-%m-%d")
        self.ns = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"
        
    def create_root(self, act_name="act"):
        """Create the root akomaNtoso element with namespace."""
        root = Element("akomaNtoso")
        root.set("xmlns", self.ns)
        act = SubElement(root, "act")
        act.set("name", act_name)
        return root, act
    
    def create_metadata(self, act, title="", act_number=""):
        """Create metadata section with FRBR structure."""
        meta = SubElement(act, "meta")
        identification = SubElement(meta, "identification")
        identification.set("source", "#source")
        
        # FRBRWork - abstract intellectual creation
        work = SubElement(identification, "FRBRWork")
        work_this = SubElement(work, "FRBRthis")
        work_uri = SubElement(work, "FRBRuri")
        work_date = SubElement(work, "FRBRdate")
        work_author = SubElement(work, "FRBRauthor")
        work_country = SubElement(work, "FRBRcountry")
        
        uri_path = f"/akn/{self.jurisdiction}"
        if self.state:
            uri_path += f"-{self.state}"
        uri_path += f"/act/{self.date_enacted[:4]}/{act_number or 'statute'}"
        
        work_this.set("value", f"{uri_path}/!main")
        work_uri.set("value", uri_path)
        work_date.set("date", self.date_enacted)
        work_date.set("name", "Generation")
        work_author.set("href", "#legislature")
        work_country.set("value", self.jurisdiction)
        
        # FRBRExpression - specific version
        expression = SubElement(identification, "FRBRExpression")
        expr_this = SubElement(expression, "FRBRthis")
        expr_uri = SubElement(expression, "FRBRuri")
        expr_date = SubElement(expression, "FRBRdate")
        expr_author = SubElement(expression, "FRBRauthor")
        expr_lang = SubElement(expression, "FRBRlanguage")
        
        expr_this.set("value", f"{uri_path}/eng@{self.date_enacted}/!main")
        expr_uri.set("value", f"{uri_path}/eng@{self.date_enacted}")
        expr_date.set("date", self.date_enacted)
        expr_date.set("name", "Expression")
        expr_author.set("href", "#legislature")
        expr_lang.set("language", "eng")
        
        # FRBRManifestation - physical embodiment
        manifest = SubElement(identification, "FRBRManifestation")
        man_this = SubElement(manifest, "FRBRthis")
        man_uri = SubElement(manifest, "FRBRuri")
        man_date = SubElement(manifest, "FRBRdate")
        man_author = SubElement(manifest, "FRBRauthor")
        
        man_this.set("value", f"{uri_path}/eng@{self.date_enacted}/!main.xml")
        man_uri.set("value", f"{uri_path}/eng@{self.date_enacted}.xml")
        man_date.set("date", datetime.now().strftime("%Y-%m-%d"))
        man_date.set("name", "XMLConversion")
        man_author.set("href", "#converter")
        
        # Publication info
        publication = SubElement(meta, "publication")
        publication.set("date", self.date_enacted)
        publication.set("name", "enacted")
        publication.set("showAs", "Enacted")
        
        # References
        references = SubElement(meta, "references")
        references.set("source", "#source")
        
        org_leg = SubElement(references, "TLCOrganization")
        org_leg.set("eId", "legislature")
        org_leg.set("href", f"/akn/{self.jurisdiction}-{self.state}/legislature" if self.state else f"/akn/{self.jurisdiction}/legislature")
        org_leg.set("showAs", "Legislature")
        
        org_source = SubElement(references, "TLCOrganization")
        org_source.set("eId", "source")
        org_source.set("href", "#")
        org_source.set("showAs", "Original Source")
        
        person = SubElement(references, "TLCPerson")
        person.set("eId", "converter")
        person.set("href", "#")
        person.set("showAs", "Document Converter")
        
        return meta
    
    def parse_text(self, text):
        """
        Parse statute text and identify structure.
        Returns a structured representation.
        """
        lines = text.strip().split('\n')
        structure = {
            'preamble': [],
            'sections': []
        }
        
        current_section = None
        current_subsection = None
        in_preamble = True
        
        # Pattern matching
        section_pattern = r'^(Sec\.|Section)\s+(\d+[A-Za-z]?)\.\s*(.*)$'
        subsection_pattern = r'^§\s*(\d+[A-Za-z]?)\.\s*(.*)$'
        lettered_subsec_pattern = r'^\(([a-z])\)\s*(.*)$'
        numbered_item_pattern = r'^\((\d+)\)\s*(.*)$'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section
            section_match = re.match(section_pattern, line)
            if section_match:
                in_preamble = False
                current_section = {
                    'type': 'section',
                    'number': section_match.group(2),
                    'heading': section_match.group(3),
                    'content': [],
                    'subsections': []
                }
                structure['sections'].append(current_section)
                current_subsection = None
                continue
            
            # Check for subsection (§)
            subsec_match = re.match(subsection_pattern, line)
            if subsec_match and current_section:
                current_subsection = {
                    'type': 'subsection',
                    'number': subsec_match.group(1),
                    'heading': subsec_match.group(2),
                    'content': [],
                    'items': []
                }
                current_section['subsections'].append(current_subsection)
                continue
            
            # Check for lettered subsection
            lettered_match = re.match(lettered_subsec_pattern, line)
            if lettered_match and current_subsection:
                letter_subsec = {
                    'type': 'lettered_subsection',
                    'letter': lettered_match.group(1),
                    'content': [lettered_match.group(2)]
                }
                current_subsection['items'].append(letter_subsec)
                continue
            
            # Check for numbered item
            numbered_match = re.match(numbered_item_pattern, line)
            if numbered_match:
                content_text = numbered_match.group(2).strip()
                item = {
                    'type': 'numbered_item',
                    'number': numbered_match.group(1),
                    'content': [content_text] if content_text else []
                }
                if current_subsection:
                    current_subsection['items'].append(item)
                elif current_section:
                    current_section['content'].append(item)
                continue
            
            # Regular content line
            if in_preamble:
                structure['preamble'].append(line)
            elif current_subsection:
                # Add to last item if it exists, otherwise to subsection content
                if current_subsection['items']:
                    last_item = current_subsection['items'][-1]
                    if last_item['type'] == 'lettered_subsection':
                        last_item['content'].append(line)
                        continue
                    if last_item['type'] == 'numbered_item':
                        last_item['content'].append(line)
                        continue
                current_subsection['content'].append(line)
            elif current_section:
                # If the last section content is a numbered item, append as continuation
                if current_section['content'] and isinstance(current_section['content'][-1], dict) and current_section['content'][-1].get('type') == 'numbered_item':
                    current_section['content'][-1]['content'].append(line)
                else:
                    current_section['content'].append(line)
        
        return structure
    
    def build_xml(self, structure, title="Statute", act_number=""):
        """Build Akoma Ntoso XML from parsed structure."""
        root, act = self.create_root()
        self.create_metadata(act, title, act_number)
        
        # Preface
        if title:
            preface = SubElement(act, "preface")
            p = SubElement(preface, "p")
            doctype = SubElement(p, "docType")
            doctype.text = title
        
        # Preamble
        if structure['preamble']:
            preamble = SubElement(act, "preamble")
            for line in structure['preamble']:
                p = SubElement(preamble, "p")
                p.text = line
        
        # Body
        body = SubElement(act, "body")
        
        for section in structure['sections']:
            sec_elem = SubElement(body, "section")
            sec_id = f"sec_{section['number'].replace('.', '_')}"
            sec_elem.set("eId", sec_id)
            
            num_elem = SubElement(sec_elem, "num")
            num_elem.text = f"Sec. {section['number']}."
            
            if section['heading']:
                heading_elem = SubElement(sec_elem, "heading")
                heading_elem.text = section['heading']
            
            # Section content
            if section['content']:
                content_elem = SubElement(sec_elem, "content")
                
                # Check if content contains numbered items
                has_items = any(isinstance(c, dict) and c.get('type') == 'numbered_item' for c in section['content'])
                
                if has_items:
                    block_list = SubElement(content_elem, "blockList")
                    block_list.set("eId", f"{sec_id}__list_1")
                    
                    for item in section['content']:
                        if isinstance(item, dict) and item['type'] == 'numbered_item':
                            item_elem = SubElement(block_list, "item")
                            item_elem.set("eId", f"{sec_id}__list_1__item_{item['number']}")
                            
                            num_item = SubElement(item_elem, "num")
                            num_item.text = f"({item['number']})"
                            
                            # Support multiple paragraphs for the item content
                            content_lines = item.get('content', [])
                            if isinstance(content_lines, list):
                                for line in content_lines:
                                    p = SubElement(item_elem, "p")
                                    p.text = line
                            else:
                                p = SubElement(item_elem, "p")
                                p.text = str(content_lines)
                        elif isinstance(item, str):
                            p = SubElement(content_elem, "p")
                            p.text = item
                else:
                    for line in section['content']:
                        if isinstance(line, str):
                            p = SubElement(content_elem, "p")
                            p.text = line
            
            # Subsections
            for subsec in section['subsections']:
                subsec_elem = SubElement(sec_elem, "subsection")
                subsec_id = f"{sec_id}__subsec_{subsec['number']}"
                subsec_elem.set("eId", subsec_id)
                
                num_elem = SubElement(subsec_elem, "num")
                num_elem.text = f"§ {subsec['number']}."
                
                if subsec['heading']:
                    heading_elem = SubElement(subsec_elem, "heading")
                    heading_elem.text = subsec['heading']
                
                # Subsection content
                if subsec['content'] or subsec['items']:
                    # Handle lettered subsections
                    lettered_subsections = [item for item in subsec['items'] if item['type'] == 'lettered_subsection']
                    numbered_items = [item for item in subsec['items'] if item['type'] == 'numbered_item']
                    
                    if lettered_subsections:
                        for letter_sub in lettered_subsections:
                            letter_elem = SubElement(subsec_elem, "subsection")
                            letter_id = f"{subsec_id}__subsec_{letter_sub['letter']}"
                            letter_elem.set("eId", letter_id)
                            
                            num_elem = SubElement(letter_elem, "num")
                            num_elem.text = f"({letter_sub['letter']})"
                            
                            content_elem = SubElement(letter_elem, "content")
                            for line in letter_sub['content']:
                                p = SubElement(content_elem, "p")
                                p.text = line
                    
                    if numbered_items:
                        content_elem = SubElement(subsec_elem, "content")
                        block_list = SubElement(content_elem, "blockList")
                        block_list.set("eId", f"{subsec_id}__list_1")
                        
                        for item in numbered_items:
                            item_elem = SubElement(block_list, "item")
                            item_elem.set("eId", f"{subsec_id}__list_1__item_{item['number']}")
                            
                            num_item = SubElement(item_elem, "num")
                            num_item.text = f"({item['number']})"
                            
                            content_lines = item.get('content', [])
                            if isinstance(content_lines, list):
                                for line in content_lines:
                                    p = SubElement(item_elem, "p")
                                    p.text = line
                            else:
                                p = SubElement(item_elem, "p")
                                p.text = str(content_lines)
                    
                    if subsec['content']:
                        if not lettered_subsections and not numbered_items:
                            content_elem = SubElement(subsec_elem, "content")
                        
                        for line in subsec['content']:
                            p = SubElement(content_elem, "p")
                            p.text = line
        
        return root
    
    def prettify_xml(self, elem):
        """Return a pretty-printed XML string."""
        rough_string = tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('utf-8')
    
    def convert(self, text, title="Statute", act_number=""):
        """
        Convert statute text to Akoma Ntoso XML.
        
        Args:
            text: Plain text statute
            title: Title of the act
            act_number: Act number or identifier
            
        Returns:
            Pretty-printed XML string
        """
        structure = self.parse_text(text)
        xml_root = self.build_xml(structure, title, act_number)
        return self.prettify_xml(xml_root)


def extract_pdf_text_with_pymupdf(pdf_path: str) -> str:
    if fitz is None:
        return ""
    doc = fitz.open(pdf_path)
    pages_text = []
    for page in doc:
        # Collect strikeout annotation rects (if any)
        strike_rects = []
        try:
            a = page.first_annot
            while a:
                atype = getattr(a, "type", None)
                name = None
                if isinstance(atype, tuple) and len(atype) >= 2:
                    name = atype[1]
                if name == "StrikeOut":
                    try:
                        strike_rects.append(fitz.Rect(a.rect))
                    except Exception:
                        pass
                a = a.next
        except Exception:
            pass

        # Collect likely horizontal stroke lines (potential strike-throughs)
        stroke_lines = []
        try:
            for path in page.get_cdrawings():
                if path.get("type") not in ("s", "fs"):
                    continue
                for it in path.get("items", []):
                    if not it or it[0] != "l":
                        continue
                    _, p1, p2 = it
                    ydiff = abs(p1[1] - p2[1])
                    if ydiff <= 1.5:  # nearly horizontal, ~2 points tolerance
                        y = (p1[1] + p2[1]) / 2.0
                        x0 = min(p1[0], p2[0])
                        x1 = max(p1[0], p2[0])
                        if x1 - x0 > 2.0:  # ignore tiny dashes
                            stroke_lines.append((y, x0, x1))
        except Exception:
            pass

        def char_is_struck(bbox):
            try:
                x0, y0, x1, y1 = bbox
            except Exception:
                return False
            if x1 <= x0 or y1 <= y0:
                return False
            h = y1 - y0
            band_y0 = y0  # widen band to full height
            band_y1 = y1
            width = x1 - x0
            for y, lx0, lx1 in stroke_lines:
                if y < band_y0 or y > band_y1:
                    continue
                overlap = max(0.0, min(x1, lx1) - max(x0, lx0))
                if overlap >= 0.2 * width:
                    return True
            return False

        # Use rawdict to drop characters detected as struck-through
        d = page.get_text("rawdict")
        lines_out = []
        for block in d.get("blocks", []):
            if block.get("type", 0) != 0:
                continue
            for line in block.get("lines", []):
                buf = []
                for span in line.get("spans", []):
                    s_cf = int(span.get("char_flags", 0))
                    if s_cf & 1:
                        continue
                    chars = span.get("chars", [])
                    if not chars:
                        text = span.get("text", "")
                        if text:
                            buf.append(text)
                        continue
                    for ch in chars:
                        c = ch.get("c", "")
                        bbox = ch.get("bbox")
                        if not c:
                            continue
                        if bbox and char_is_struck(bbox):
                            continue
                        buf.append(c)
                text_line = "".join(buf).strip()
                if text_line:
                    lines_out.append(text_line)
        pages_text.append("\n".join(lines_out))
    return "\n\n".join(pages_text).strip()


def extract_pdf_text_with_pypdf(pdf_path: str) -> str:
    if PdfReader is None:
        return ""
    reader = PdfReader(pdf_path)
    extracted = []
    for page in getattr(reader, "pages", []):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        extracted.append(text)
    return "\n\n".join(extracted).strip()


def main():
    """Pipeline: PDF in input -> TXT -> Akoma Ntoso XML in output."""

    # Resolve paths
    cwd = os.getcwd()
    input_path = os.path.join(cwd, "input")
    output_dir = os.path.join(cwd, "output")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Determine where to look for PDFs
    search_dir = input_path if os.path.isdir(input_path) else cwd

    # Find all PDF files
    pdf_files = sorted(glob.glob(os.path.join(search_dir, "*.pdf")))
    if not pdf_files:
        print("No PDF files found in 'input' folder."
              " If 'input' is not a folder in this workspace, I'll look in the project root."
              f" Searched: {search_dir}")
        return

    date_today = datetime.now().strftime("%Y-%m-%d")
    converter = AkomaNtosoConverter(
        jurisdiction="us",
        state="vt",
        date_enacted=date_today
    )

    processed = 0
    for pdf_path in pdf_files:
        try:
            basename = os.path.splitext(os.path.basename(pdf_path))[0]
            print(f"Reading PDF: {pdf_path}")
            full_text = ""
            if fitz is not None:
                full_text = extract_pdf_text_with_pymupdf(pdf_path)
            if not full_text:
                if fitz is None:
                    print("Info: PyMuPDF not available; falling back to pypdf without strikeout removal.")
                full_text = extract_pdf_text_with_pypdf(pdf_path)
            if not full_text:
                print(f"Warning: Extracted empty text from PDF: {pdf_path}. Skipping.")
                continue

            # Save TXT next to source PDF (prefer 'input' if directory exists)
            txt_dir = input_path if os.path.isdir(input_path) else os.path.dirname(pdf_path)
            txt_path = os.path.join(txt_dir, f"{basename}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            print(f"Text saved: {txt_path}")

            # Convert to Akoma Ntoso XML
            xml_output = converter.convert(
                text=full_text,
                title=basename.replace("_", " ").title(),
                act_number=basename
            )

            # Save XML in output folder
            xml_path = os.path.join(output_dir, f"{basename}.xml")
            with open(xml_path, "w", encoding="utf-8") as f:
                f.write(xml_output)
            print(f"XML saved: {xml_path}")
            processed += 1
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")

    print(f"Done. Processed {processed} PDF(s).")


if __name__ == "__main__":
    main()