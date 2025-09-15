import os

root_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Physics/Physics_human/pdf_docx_json"

for dirpath, dirnames, filenames in os.walk(root_dir):
    # 1. Rename all .docx.json files to .json
    for filename in filenames:
        if filename.endswith('.docx.json'):
            old_path = os.path.join(dirpath, filename)
            new_filename = filename.replace('.docx.json', '.json')
            new_path = os.path.join(dirpath, new_filename)
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")
            else:
                print(f"Already correct or target exists, skipping: {old_path}")

    # 2. Rename <folder>/<folder>.docx to <folder>/<folder>-
    folder_name = os.path.basename(dirpath)
    old_docx = folder_name + ".docx"
    new_name = folder_name + "-"
    old_docx_path = os.path.join(dirpath, old_docx)
    new_name_path = os.path.join(dirpath, new_name)
    if os.path.exists(old_docx_path):
        if not os.path.exists(new_name_path):
            os.rename(old_docx_path, new_name_path)
            print(f"Renamed: {old_docx_path} -> {new_name_path}")
        else:
            print(f"Already correct or target exists, skipping: {old_docx_path}") 