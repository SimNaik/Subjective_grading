import os
import re

INPUT_DIR = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/Tables"
OUTPUT_DIR = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/analysis_md"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# The columns to extract
COLUMNS = ["Human_ocr", "Gemini_ocr", "type of error", "Discrepancy Analysis"]

for root, dirs, files in os.walk(INPUT_DIR):
    for file in files:
        if not file.endswith(".md"):
            continue
        input_md_path = os.path.join(root, file)
        output_md_path = os.path.join(OUTPUT_DIR, file)

        with open(input_md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find header and column indices
        header_line = None
        for i, line in enumerate(lines):
            if line.strip().startswith("| ") and all(col in line for col in COLUMNS):
                header_line = i
                break
        if header_line is None:
            print(f"⚠️ No valid header in {input_md_path}")
            continue
        header = [h.strip() for h in lines[header_line].strip().split("|")][1:-1]
        col_indices = [header.index(col) for col in COLUMNS]

        # Write new markdown
        out_lines = ["| " + " | ".join(COLUMNS) + " |", "| " + " | ".join(["---"] * len(COLUMNS)) + " |"]
        for line in lines[header_line+2:]:
            if not line.strip().startswith("| "):
                continue
            row = [c.strip() for c in line.strip().split("|")][1:-1]
            if len(row) < max(col_indices)+1:
                continue
            new_row = [row[i] for i in col_indices]
            out_lines.append("| " + " | ".join(new_row) + " |")
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines))
        print(f"Extracted columns to {output_md_path}") 