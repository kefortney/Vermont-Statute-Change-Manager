# Vermont-Statute-Change-Manager

Convert statute PDFs to Akoma Ntoso XML. The script now:
- Finds a PDF in the `input` folder
- Extracts text to a `.txt` file in the same folder
- Converts the text to Akoma Ntoso XML and writes it to `output/`

## Setup

Install dependencies (preferably in a virtualenv or conda env):

```bash
pip install -r requirements.txt
```

This uses `pypdf` for text extraction (falls back to `PyPDF2` if installed).

## Usage

1. Ensure there is a folder named `input/` at the repo root.
2. Place your statute PDF file in `input/` (e.g., `input/bill.pdf`).
3. Run the converter (processes all PDFs in `input/`):

```bash
python "Akoma-Ntoso-XML-Converter.py"
```

4. On success, you will see for each PDF:
- Extracted text saved as `input/<name>.txt`
- XML saved as `output/<name>.xml`

Notes:
- If `input/` is missing, the script will search the project root for a `*.pdf` and save the `.txt` next to it.
- The script creates the `output/` folder automatically if missing.