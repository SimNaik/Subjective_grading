import os
from dotenv import load_dotenv
import google.generativeai as genai

# === Load API Key ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))

# Set model
model = genai.GenerativeModel("gemini-2.5-pro")

def send_md_and_prompt(input_md_path, prompt, output_md_dir):
    # Read Markdown file
    with open(input_md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Compose prompt content
    full_prompt = f"{prompt}\n\n<Markdown Table Input>\n{md_content}"

    try:
        response = model.generate_content(
            full_prompt,
            generation_config={"temperature": 0.2},
        )
        generated_text = response.text

        # Try to extract Markdown from the response (strip markdown code block if present)
        if generated_text.strip().startswith('```markdown'):
            generated_text = generated_text.strip().removeprefix('```markdown').removesuffix('```').strip()
        elif generated_text.strip().startswith('```'):
            generated_text = generated_text.strip().removeprefix('```').removesuffix('```').strip()

        # Output file name
        base_name = os.path.splitext(os.path.basename(input_md_path))[0]
        os.makedirs(output_md_dir, exist_ok=True)
        output_md_path = os.path.join(output_md_dir, f"{base_name}_gemini_output.md")

        # Save the generated output
        with open(output_md_path, 'w', encoding='utf-8') as out_file:
            out_file.write(generated_text)

        print(f"🎉 Output saved to {output_md_path}")

    except Exception as e:
        print(f"❌ Error generating response: {e}")

# === Example Usage ===
if __name__ == "__main__":
    input_md_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/analysis_md/01_10021165141080491171694788750.md"  # Change as needed
    output_md_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/Z_OCR_gemini_pcmb/Maths/gemini_csv"
    prompt = """
You are an expert OCR evaluator. For each row in the input Markdown table, analyze the differences between the Human_ocr and Gemini_ocr columns. Fill in the 'type of error' and 'Discrepancy Analysis' columns with your best judgment. Only use the provided columns. Output the result as a Markdown table with the same columns and order as the input, but with the last two columns filled in.
"""
    send_md_and_prompt(input_md_path, prompt, output_md_dir) 