import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# === Load API Key ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))

# Set model
model = genai.GenerativeModel("gemini-2.5-pro")

def send_files_and_prompt(txt_file_path, json_file_path, prompt):
    # Read TXT file (Human OCR)
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        txt_content = f.read()

    # Read JSON file (LLM OCR)
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_content = json.load(f)

    # Compose prompt content
    full_prompt = (
        f"{prompt}\n\n"
        f"<Human OCR>\n{txt_content}\n\n"
        f"<LLM OCR>\n{json.dumps(json_content, indent=2)}"
    )

    try:
        response = model.generate_content(
            full_prompt,
            generation_config={"temperature": 0.2},
        )
        generated_text = response.text

        # === Construct output filename ===
        base_name = os.path.splitext(os.path.basename(txt_file_path))[0]
        
        # Set the specific output folder for saving the file
        output_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/OCR_gd_gem/pre_evaluation"
        
        # Ensure the output folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        # Create the output file path
        output_txt_file_path = os.path.join(output_folder, f"{base_name}_output.mmd")

        # Save the generated output
        with open(output_txt_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(generated_text)

        print(f"🎉 Output saved to {output_txt_file_path}")

    except Exception as e:
        print(f"❌ Error generating response: {e}")

# === Your Inputs ===
json_file_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/OCR_gd_gem/gemini_2.5_pro_768/Biology/01_1002115268961841141690701450/01_1002115268961841141690701450.json"
txt_file_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/OCR_gd_gem/ocr_human/bio/01_1002115268961841141690701450.txt"
prompt = """
Role: You are a highly accurate Quality Assurance (QA) Engine for OCR systems.

Context: You will be provided with two documents for each task:

A JSON File: Contains text extracted from the original PDF by an LLM.
A TXT File: Contains text extracted by a human.
Objective: Your sole purpose is to determine which file—JSON or TXT—more accurately reflects the original content.

Specific Instructions:
From the JSON file, use the value of the "ocr_text" key.
From the TXT file, use the text between the <sol_start ...> and <sol_end> tags.
Compare both for accuracy and decide which one is more faithful to the source (assume you have access to the true content implicitly).
Report Your Verdict in the following table format:

Your entire output must be a single table that only includes rows where a discrepancy was found. The table must have the following four columns:

1. Question Number: The ID of the solution where the discrepancy occurred.
2. JSON Version: The full text of the solution from the JSON file ( where the discrepancy occurred).
3. TXT Version: The full text of the solution from the TXT file ( where the discrepancy occurred).
4. Discrepancy Analysis & Verdict: A two-part analysis:
Discrepancy Type: State the primary type of error (e.g., Spelling (Typo), Punctuation, Wording, Numerical Difference).
Verdict: State which version is correct and provide a brief justification (e.g., TXT is correct; "materials" is the more appropriate plural form.).
"""

send_files_and_prompt(txt_file_path, json_file_path, prompt)
