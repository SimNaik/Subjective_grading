import os

root_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Physics/Physics_human/Physics_pdf_docx_human_ocr"

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith('.docx.pdf'):
            old_path = os.path.join(dirpath, filename)
            new_filename = filename[:-9] + '.pdf'  # Remove 9 chars: '.docx.pdf'
            new_path = os.path.join(dirpath, new_filename)
            if os.path.exists(new_path):
                print(f"Could not rename (target exists): {old_path}")
            else:
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    print(f"Could not rename (error): {old_path} - {e}") 