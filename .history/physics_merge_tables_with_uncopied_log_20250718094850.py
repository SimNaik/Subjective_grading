import os
from glob import glob

# Paths
tables_root = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Physics/Tables"
gemini_root = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Physics/gemini_md"
final_md_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Physics/Physics_final.md"

def parse_md_table(md_lines):
    table = []
    for line in md_lines:
        line = line.strip()
        if line.startswith('|') and line.endswith('|'):
            cells = [cell.strip() for cell in line[1:-1].split('|')]
            table.append(cells)
    return table

def format_md_table(table):
    return '\n'.join(['| ' + ' | '.join(row) + ' |' for row in table])

all_final_rows = []
total_rows = 0
copied_rows = 0
uncopied_rows = 0
header_written = False
uncopied_details = []  # To store details of uncopied rows

# Find all tables md files
for tables_md_path in glob(os.path.join(tables_root, "*", "*.md")):
    base = os.path.basename(tables_md_path).replace('.md', '')
    gemini_md_path = os.path.join(gemini_root, f"{base}_gemini_output.md")
    if not os.path.exists(gemini_md_path):
        print(f"Gemini file not found for {tables_md_path}, skipping.")
        continue

    with open(tables_md_path, 'r') as f:
        tables_lines = f.readlines()
    with open(gemini_md_path, 'r') as f:
        gemini_lines = f.readlines()

    tables_table = parse_md_table(tables_lines)
    gemini_table = parse_md_table(gemini_lines)

    if len(tables_table) < 3 or len(gemini_table) < 3:
        print(f"Table too short in {tables_md_path}, skipping.")
        continue

    header_rows = 2
    tables_data = tables_table[header_rows:]
    gemini_data = gemini_table[header_rows:]

    total_rows += len(tables_data)

    # Write header only once
    if not header_written:
        all_final_rows.extend(tables_table[:header_rows])
        header_written = True

    for i, t_row in enumerate(tables_data):
        if i < len(gemini_data):
            g_row = gemini_data[i]
            trimmed = t_row[:-2]
            gemini_last2 = g_row[-2:]
            all_final_rows.append(trimmed + gemini_last2)
            copied_rows += 1
        else:
            uncopied_rows += 1
            uncopied_details.append({
                "file": tables_md_path,
                "row_number": i + 1,  # 1-based index for user clarity
                "row_content": t_row
            })

# Write the combined final md
with open(final_md_path, 'w') as f:
    f.write(format_md_table(all_final_rows))

print(f"Total data rows in all tables md: {total_rows}")
print(f"Number of rows copied/combined: {copied_rows}")
print(f"Number of rows that could not be copied: {uncopied_rows}")
print(f"Final combined file saved to: {final_md_path}")

# Print details of uncopied rows
if uncopied_details:
    print("\nRows that could not be copied (no matching Gemini MD row):")
    for detail in uncopied_details:
        print(f"File: {detail['file']}, Row: {detail['row_number']}, Content: {detail['row_content']}")
else:
    print("All rows were copied successfully.") 