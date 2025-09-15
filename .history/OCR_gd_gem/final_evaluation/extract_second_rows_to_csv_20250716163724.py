import os
import csv
from docx import Document


def get_all_docx_files(root_dir):
    docx_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.docx'):
                docx_files.append(os.path.join(dirpath, filename))
    return docx_files


def extract_second_rows_to_csv(docx_files, csv_path, root_dir):
    header_written = False
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for docx_file in docx_files:
            doc = Document(docx_file)
            for t_idx, table in enumerate(doc.tables):
                rows = table.rows
                if len(rows) < 2:
                    continue  # skip tables with no second row
                # Write header only once, from the first table processed
                if not header_written:
                    header = [cell.text.strip() for cell in rows[0].cells]
                    writer.writerow(['docx_file', 'table_index'] + header)
                    header_written = True
                # Write only the second row (index 1)
                cells = [cell.text.strip() for cell in rows[1].cells]
                # Pad/truncate to match header length
                cells = (cells + ['']*len(header))[:len(header)]
                writer.writerow([
                    os.path.relpath(docx_file, root_dir),
                    t_idx,
                    *cells
                ])


if __name__ == "__main__":
    root_dir = '/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/OCR_gd_gem/final_evaluation/tables'
    csv_path = '/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/OCR_gd_gem/final_evaluation/all_tables_second_row.csv'

    all_docx_files = get_all_docx_files(root_dir)
    extract_second_rows_to_csv(all_docx_files, csv_path, root_dir)
    print(f"CSV saved to {csv_path}") 