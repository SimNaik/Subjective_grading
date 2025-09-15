import os

root_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Physics/Physics_human/Physics_pdf_docx_human_ocr"

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith('.doc.pdf'):
            old_path = os.path.join(dirpath, filename)
            new_filename = filename[:-8] + '.pdf'  # Remove .doc.pdf, add .pdf
            new_path = os.path.join(dirpath, new_filename)
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")
            else:
                print(f"Already correct or target exists, skipping: {old_path}") 