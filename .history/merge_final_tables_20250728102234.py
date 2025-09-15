import os

base_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr/Physics"
final_tables_dir = os.path.join(base_dir, "final_tables")
output_file = os.path.join(base_dir, "final_table.md")

all_rows = []
header = None

def parse_md_table(md_path):
    rows = []
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or set(line.replace('|', '').replace(':', '').replace('-', '')) == set():
                continue
            if line.startswith('|'):
                parts = [cell.strip() for cell in line.strip('|').split('|')]
                rows.append(parts)
    return rows

# Loop through all subfolders and .md files
for folder_id in os.listdir(final_tables_dir):
    folder_path = os.path.join(final_tables_dir, folder_id)
    if not os.path.isdir(folder_path):
        continue
    for fname in os.listdir(folder_path):
        if not fname.endswith(".md"):
            continue
        file_path = os.path.join(folder_path, fname)
        rows = parse_md_table(file_path)
        if not rows:
            continue
        if header is None:
            header = rows[0]
            all_rows.append(header)
            all_rows.append(["---"] * len(header))
        # Add all data rows (skip header and separator)
        for row in rows[2:]:
            all_rows.append(row)

# Write merged table
with open(output_file, "w", encoding="utf-8") as f:
    for row in all_rows:
        f.write("| " + " | ".join(row) + " |\n")

print(f"Merged tables written to {output_file}") 