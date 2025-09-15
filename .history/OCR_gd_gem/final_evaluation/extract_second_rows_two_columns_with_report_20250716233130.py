import os
import csv
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

def get_all_docx_files(root_dir):
    docx_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.docx'):
                docx_files.append(os.path.join(dirpath, filename))
    return docx_files

def get_cell_text_with_inner_tables(cell):
    """Extracts all text from a cell, including text from any tables inside the cell."""
    texts = []
    for item in cell._element:
        if item.tag.endswith('tbl'):
            table = Table(item, cell)
            for row in table.rows:
                row_text = [get_cell_text_with_inner_tables(c) for c in row.cells]
                texts.append(' | '.join(row_text))
        elif item.tag.endswith('p'):
            para = Paragraph(item, cell)
            texts.append(para.text)
    return '\n'.join(texts)

def extract_second_rows_to_csv(docx_files, csv_path, root_dir):
    header_written = False
    processed_files = []
    skipped_files = []
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for docx_file in docx_files:
            try:
                doc = Document(docx_file)
                found_table = False
                for t_idx, table in enumerate(doc.tables):
                    rows = table.rows
                    if len(rows) < 2 or len(rows[1].cells) < 2:
                        continue  # skip tables with no second row or less than 2 columns
                    found_table = True
                    # Write header only once, from the first table processed
                    if not header_written:
                        header = [cell.text.strip() for cell in rows[0].cells[:2]]
                        writer.writerow(header)
                        header_written = True
                    # Write only the first two cells of the second row (index 1), extracting inner tables as text
                    cells = [get_cell_text_with_inner_tables(cell).strip() for cell in rows[1].cells[:2]]
                    # Pad/truncate to 2 columns
                    cells = (cells + ['']*2)[:2]
                    writer.writerow(cells)
                if found_table:
                    processed_files.append(os.path.relpath(docx_file, root_dir))
                else:
                    skipped_files.append(os.path.relpath(docx_file, root_dir))
            except Exception as e:
                skipped_files.append(os.path.relpath(docx_file, root_dir))
                print(f"Error processing {docx_file}: {e}")
    return processed_files, skipped_files

if __name__ == "__main__":
    root_dir = '/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/OCR_gd_gem/final_evaluation/tables'
    csv_path = '/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/OCR_gd_gem/final_evaluation/all_tables_second_row_two_columns.csv'

    all_docx_files = get_all_docx_files(root_dir)
    processed_files, skipped_files = extract_second_rows_to_csv(all_docx_files, csv_path, root_dir)
    print(f"CSV saved to {csv_path}")
    print(f"Total DOCX files found: {len(all_docx_files)}")
    print(f"Total DOCX files processed (with at least one table/second row): {len(processed_files)}")
    print(f"Total DOCX files skipped (no valid table/second row or error): {len(skipped_files)}")
    if skipped_files:
        print("Skipped files:")
        for f in skipped_files:
            print("  -", f) 