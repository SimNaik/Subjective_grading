import os
import json
from difflib import ndiff

# === CONFIGURATION ===
GEMINI_JSON_PATH = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/Maths_Gemini/Maths_json/01_10021165141080491171694788750/01_10021165141080491171694788750.json"
HUMAN_JSON_PATH = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/Maths_human/pdf_docx_json/01_10021165141080491171694788750/01_10021165141080491171694788750.json"
OUTPUT_MD_DIR = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/Tables"

os.makedirs(OUTPUT_MD_DIR, exist_ok=True)

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

# === CER CALCULATION ===
def char_error_rate(s1, s2):
    if s1 == "na" or s2 == "na":
        return "na"
    diff = list(ndiff(s1, s2))
    insertions = sum(1 for d in diff if d[0] == '+')
    deletions = sum(1 for d in diff if d[0] == '-')
    ref_len = len(s1)
    if ref_len == 0:
        return 0 if len(s2) == 0 else 1
    cer = (insertions + deletions) / ref_len
    return f"{cer:.4f}"

# === HIGHLIGHT DIFFERENCES ===
def highlight_differences(s1, s2):
    if s1 == "na" or s2 == "na":
        return "na"
    diff = list(ndiff(s1, s2))
    result = []
    for d in diff:
        if d[0] == ' ':
            result.append(d[2])
        elif d[0] == '-':
            result.append(f"[-{d[2]}-]")
        elif d[0] == '+':
            result.append(f"[+{d[2]}+]")
    return ''.join(result)

# === SANITIZE FOR MARKDOWN ===
def sanitize(text):
    if text == "na":
        return text
    text = text.replace("\n", " ").replace("|", "\\|").replace(",", "&#44;")
    return text

# === OUTPUT HEADERS ===
header = [
    "docx source",
    "question number",
    "Human_ocr",
    "Gemini_ocr",
    "cer",
    "highlighted differences",
    "type of error",
    "Discrepancy Analysis"
]

# === OUTPUT FILE NAME ===
json_base = os.path.splitext(os.path.basename(GEMINI_JSON_PATH))[0]
output_md_path = os.path.join(OUTPUT_MD_DIR, f"{json_base}.md")

# === BUILD TABLE ===
md_lines = ["# OCR Comparison Table", "\n", "| " + " | ".join(header) + " |", "| " + " | ".join(['---'] * len(header)) + " |"]

for qnum in sorted(set(gemini_q.keys()) | set(human_q.keys())):
    human_text = sanitize(human_q.get(qnum, "na"))
    gemini_text = sanitize(gemini_q.get(qnum, "na"))
    if human_text == "na" or gemini_text == "na":
        cer_value = "na"
        highlighted_diff = "na"
    else:
        cer_value = char_error_rate(human_text, gemini_text)
        highlighted_diff = sanitize(highlight_differences(human_text, gemini_text))
    row = [
        os.path.basename(GEMINI_JSON_PATH),
        str(qnum),
        human_text,
        gemini_text,
        cer_value,
        highlighted_diff,
        "",
        "",
    ]
    md_lines.append("| " + " | ".join(row) + " |")

# === WRITE OUTPUT ===
with open(output_md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"Markdown table written to {output_md_path}") 