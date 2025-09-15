import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# === Load API Key ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))

# Set model
model = genai.GenerativeModel("gemini-2.5-pro")

def send_csv_and_prompt(input_csv_path, prompt, output_csv_dir):
    # Read CSV file
    df = pd.read_csv(input_csv_path)
    csv_content = df.to_csv(index=False)

    # Compose prompt content
    full_prompt = f"{prompt}\n\n<CSV Input>\n{csv_content}"

    try:
        response = model.generate_content(
            full_prompt,
            generation_config={"temperature": 0.2},
        )
        generated_text = response.text

        # Try to extract CSV from the response (strip markdown if present)
        if generated_text.strip().startswith('```csv'):
            generated_text = generated_text.strip().removeprefix('```csv').removesuffix('```').strip()
        elif generated_text.strip().startswith('```'):
            generated_text = generated_text.strip().removeprefix('```').removesuffix('```').strip()

        # Output file name
        base_name = os.path.splitext(os.path.basename(input_csv_path))[0]
        os.makedirs(output_csv_dir, exist_ok=True)
        output_csv_path = os.path.join(output_csv_dir, f"{base_name}_gemini_output.csv")

        # Save the generated output
        with open(output_csv_path, 'w', encoding='utf-8') as out_file:
            out_file.write(generated_text)

        print(f"🎉 Output saved to {output_csv_path}")

    except Exception as e:
        print(f"❌ Error generating response: {e}")

# === Example Usage ===
if __name__ == "__main__":
    input_csv_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/analysis_csv/01_10021165141080491171694788750.csv"  # Change as needed
    output_csv_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/gemini_csv"
    prompt = """
You are an expert OCR evaluator. For each row in the input CSV, analyze the differences between the Human_ocr and Gemini_ocr columns. Fill in the 'type of error' and 'Discrepancy Analysis' columns with your best judgment. Only use the provided columns. Output the result as a CSV with the same columns and order as the input, but with the last two columns filled in.
"""
    send_csv_and_prompt(input_csv_path, prompt, output_csv_dir) 