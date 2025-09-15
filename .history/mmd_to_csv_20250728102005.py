import os

base_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr/Physics"
analysis_dir = os.path.join(base_dir, "table_analysis")
cer_dir = os.path.join(base_dir, "tables_cer")
final_dir = os.path.join(base_dir, "final_tables")

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

def write_md_table(md_path, rows):
    with open(md_path, "w", encoding="utf-8") as f:
        for i, row in enumerate(rows):
            f.write("| " + " | ".join(row) + " |\n")
            if i == 0:
                f.write("|" + "|".join(['---'] * len(row)) + "|\n")

# Loop over all subfolders in table_analysis
for folder_id in os.listdir(analysis_dir):
    analysis_path = os.path.join(analysis_dir, folder_id)
    cer_path = os.path.join(cer_dir, folder_id)
    out_path = os.path.join(final_dir, folder_id)
    if not os.path.isdir(analysis_path) or not os.path.isdir(cer_path):
        continue
    os.makedirs(out_path, exist_ok=True)

    for fname in os.listdir(analysis_path):
        if not fname.endswith(".md"):
            continue
        analysis_file = os.path.join(analysis_path, fname)
        cer_file = os.path.join(cer_path, fname)
        if not os.path.exists(cer_file):
            print(f"Skipping {fname} in {folder_id}: no matching file in tables_cer")
            continue

        analysis_rows = parse_md_table(analysis_file)
        cer_rows = parse_md_table(cer_file)

        if len(analysis_rows) < 2 or len(analysis_rows[0]) < 2:
            print(f"Skipping {fname} in {folder_id}: not enough columns/rows in analysis table")
            continue
        last2_header = analysis_rows[0][-2:]
        last2_row = analysis_rows[1][-2:]

        new_rows = []
        for i, row in enumerate(cer_rows):
            if i == 0:
                new_rows.append(row + last2_header)
            elif i == 1:
                new_rows.append(row + last2_row)
            else:
                new_rows.append(row)

        out_fname = fname.replace("solution", "final")
        out_file = os.path.join(out_path, out_fname)
        write_md_table(out_file, new_rows)
        print(f"Saved combined table: {out_file}")

def merge_all_final_tables():
    final_tables_dir = os.path.join(base_dir, "final_tables")
    output_file = os.path.join(base_dir, "final_table.md")
    all_rows = []
    header = None
    sep = None
    for subfolder in sorted(os.listdir(final_tables_dir)):
        subfolder_path = os.path.join(final_tables_dir, subfolder)
        if not os.path.isdir(subfolder_path):
            continue
        for fname in sorted(os.listdir(subfolder_path)):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(subfolder_path, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if not lines or len(lines) < 3:
                    continue
                if header is None:
                    header = lines[0]
                    sep = lines[1]
                # Always skip header and separator for subsequent tables
                all_rows.extend(lines[2:])
    # Write merged table
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write(sep + "\n")
        for row in all_rows:
            f.write(row + "\n")
    print(f"Merged all tables into {output_file} with {len(all_rows)} data rows.")

# Call the merge function if running as main
if __name__ == "__main__":
    merge_all_final_tables() 