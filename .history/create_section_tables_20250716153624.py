import os
from docx import Document
from docx.shared import Inches
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

# Helper to iterate through paragraphs and tables in order
def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def copy_content_to_cell(src_doc, cell):
    """Copy all paragraphs, tables, and images from src_doc into the given cell."""
    # Remove the default empty paragraph
    cell.text = ""
    for block in iter_block_items(src_doc):
        if isinstance(block, Paragraph):
            p = cell.add_paragraph(block.text)
            # Copy runs (for images)
            for run in block.runs:
                if 'graphic' in run._r.xml:
                    # Try to extract and add image if present
                    for rel in src_doc.part.rels.values():
                        if "image" in rel.reltype:
                            try:
                                cell.add_paragraph().add_run().add_picture(rel.target_ref, width=Inches(2))
                            except Exception as e:
                                print(f"Could not add image: {e}")
        elif isinstance(block, Table):
            # Recreate the table in the cell (nested tables are not supported, so add after cell)
            # Instead, add a note
            cell.add_paragraph("[Table present in original document, please refer to source file]")

def read_docx_content(path):
    if not os.path.exists(path):
        return None
    return Document(path)

# Paths
human_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/OCR_gd_gem/final_evaluation/humans_ocr/06_10021024301039611141693746957"
gemini_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/OCR_gd_gem/final_evaluation/gemini_768_ocr/06_10021024301039611141693746957"
output_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/OCR_gd_gem/final_evaluation/tables/06_10021024301039611141693746957"
os.makedirs(output_dir, exist_ok=True)

section_files = [f for f in os.listdir(human_dir) if f.startswith("section_") and f.endswith(".docx")]

for section_file in section_files:
    section_number = section_file.split("_")[1].split(".")[0]
    human_path = os.path.join(human_dir, section_file)
    gemini_path = os.path.join(gemini_dir, section_file)
    output_path = os.path.join(output_dir, f"section_{section_number}_table.docx")

    doc = Document()
    table = doc.add_table(rows=2, cols=3)
    table.style = 'Table Grid'

    # Set headers
    table.cell(0, 0).text = "human ocr"
    table.cell(0, 1).text = "gemini ocr"
    table.cell(0, 2).text = "cer"

    # Copy content from human OCR
    human_doc = read_docx_content(human_path)
    if human_doc:
        copy_content_to_cell(human_doc, table.cell(1, 0))
    else:
        table.cell(1, 0).text = "[File missing]"

    # Copy content from gemini OCR
    gemini_doc = read_docx_content(gemini_path)
    if gemini_doc:
        copy_content_to_cell(gemini_doc, table.cell(1, 1))
    else:
        table.cell(1, 1).text = "[File missing]"

    # CER left blank
    table.cell(1, 2).text = ""

    doc.save(output_path)
    print(f"Saved table for section {section_number} to {output_path}") 