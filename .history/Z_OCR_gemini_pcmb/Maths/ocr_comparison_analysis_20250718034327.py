import os
import json
from difflib import ndiff
import pandas as pd

# === CONFIGURATION ===
GEMINI_JSON_PATH = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/Maths_Gemini/Maths_json/01_10021165141080491171694788750/01_10021165141080491171694788750.json"
HUMAN_JSON_PATH = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/Maths_human/pdf_docx_json/01_10021165141080491171694788750/01_10021165141080491171694788750.json"
OUTPUT_MD_DIR = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/analysis_md"
OUTPUT_CSV_DIR = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/analysis_csv"

os.makedirs(OUTPUT_MD_DIR, exist_ok=True)
os.makedirs(OUTPUT_CSV_DIR, exist_ok=True)

# === LOAD JSONS ===
with open(GEMINI_JSON_PATH, "r", encoding="utf-8") as f:
    gemini_data = json.load(f)
with open(HUMAN_JSON_PATH, "r", encoding="utf-8") as f:
    human_data = json.load(f)

# === BUILD QUESTION MAPS ===
def build_q_map(data):
    q_map = {}
    for entry in data:
        qnum = entry.get("question_number")
        text = entry.get("ocr_text", "")
        q_map[qnum] = text
    return q_map

gemini_q = build_q_map(gemini_data)
human_q = build_q_map(human_data)

# === SANITIZE FOR MARKDOWN/CSV ===
def sanitize(text):
    if text == "na":
        return text
    text = text.replace("\n", " ").replace("|", "\\|").replace(",", "&#44;")
    return text

# === OUTPUT HEADERS (4 columns) ===
header = [
    "Human_ocr",
    "Gemini_ocr",
    "type of error",
    "Discrepancy Analysis"
]

# === OUTPUT FILE NAMES ===
json_base = os.path.splitext(os.path.basename(GEMINI_JSON_PATH))[0]
output_md_path = os.path.join(OUTPUT_MD_DIR, f"{json_base}.md")
output_csv_path = os.path.join(OUTPUT_CSV_DIR, f"{json_base}.csv")

# === BUILD TABLES ===
md_lines = ["# OCR Analysis Table", "\n", "| " + " | ".join(header) + " |", "| " + " | ".join(['---'] * len(header)) + " |"]
csv_data = []

for qnum in sorted(set(gemini_q.keys()) | set(human_q.keys())):
    human_text = sanitize(human_q.get(qnum, "na"))
    gemini_text = sanitize(gemini_q.get(qnum, "na"))
    row = [
        human_text,
        gemini_text,
        "",  # type of error (to be filled manually or by further logic)
        "",  # Discrepancy Analysis (to be filled manually or by further logic)
    ]
    md_lines.append("| " + " | ".join(row) + " |")
    csv_data.append(row)

# === WRITE OUTPUTS ===
with open(output_md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

csv_df = pd.DataFrame(csv_data, columns=header)
csv_df.to_csv(output_csv_path, index=False, encoding="utf-8", quoting=1)  # quoting=1 means QUOTE_ALL

print(f"Markdown analysis table written to {output_md_path}")
print(f"CSV analysis table written to {output_csv_path}") 