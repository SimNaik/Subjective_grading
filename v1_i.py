import streamlit as st
import os
import fitz  # PyMuPDF
from PIL import Image
import json
import google.generativeai as genai
from dotenv import load_dotenv

# === Load API Key ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
model = genai.GenerativeModel('gemini-2.5-pro')

# === Prompt for Gemini ===
PROMPT = """
Carefully extract all text content from the PDF, maintaining the exact order and formatting as it appears.
Preserve all mathematical equations, formulas, and special characters exactly as they appear in the PDF.
Do not add any headers, descriptions, or labels to the output.

Output only the extracted text content in the following format for an example:

[
{
question_number: 1,
ocr_text: 'This is the PV curve <diagram_1>',
diagrams: [
  {
    id: 'diagram_1',
    coordinates: 'n/a',
    diagram_class: 'graph or diagram'
  }
],
pages: [2]
}
]

Important Rules:
- The output must be a list of such question-answer objects.
- Each object must contain:
  - question_number in increasing order which is the question number of the content.
  - ocr_text: complete question and answer content, including <diagram_1> if any diagram exists.
  - diagrams: 
     - If diagram exists → write: id: 'diagram_1', coordinates: 'n/a', and appropriate diagram_class ('graph' or 'diagram').
     - If no diagram → set: id: 'n/a', coordinates: 'n/a', diagram_class: 'n/a'.
  - pages: The page number of the content ,Must always be shown as a list of integers in square brackets.

- Understand the context to group full question-answer blocks together.
- Maintain the output structure and avoid inserting extra commentary or descriptions.
"""

# === Streamlit UI ===
st.set_page_config(layout="wide")
st.title("Solution Improvement")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

# Initialize folder_path and images to ensure they are defined before usage
folder_path = ""
images = []

if uploaded_file:
    # === Setup Folder ===
    pdf_name = uploaded_file.name.replace(".pdf", "")
    folder_path = os.path.join("uploads", pdf_name)
    os.makedirs(folder_path, exist_ok=True)

    pdf_path = os.path.join(folder_path, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    # === Convert PDF to Images ===
    st.info("🔄 Converting PDF to images...")
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img_path = os.path.join(folder_path, f"page_{page_num + 1}.png")
        pix.save(img_path)
        images.append((page_num + 1, img_path))  # Ensure each entry is a tuple

    # Debugging: Print the images list to check its contents
    st.write("Images List:", images)

# === Process Images with Gemini ===
st.info("🤖 Sending images to Gemini for text + diagram extraction...")
results = []
question_number = 1

# Ensure that folder_path is defined before using it
if folder_path and images:
    json_path = os.path.join(folder_path, "output.json")
else:
    json_path = ""  # Define json_path even if the images are empty or no file is uploaded

# Check if the images list is not empty
if images:
    for page_num, img_path in images:
        try:
            image = Image.open(img_path)
            response = model.generate_content([PROMPT, image])

            # Raw Response from Gemini
            raw_response = response.text.strip()
            st.write(f"Raw Response from Gemini (Page {page_num}): {raw_response}")

            # Clean the response (strip unwanted characters like backticks)
            cleaned_response = raw_response.strip('```json').strip('```').strip()  # Remove triple backticks and any extra spaces

            # Attempt to parse the cleaned JSON
            try:
                parsed = json.loads(cleaned_response)
            except json.JSONDecodeError as json_error:
                st.warning(f"❌ Failed to parse JSON for Page {page_num}: {json_error}")
                continue

            # Add results
            for item in parsed:
                item["question_number"] = question_number
                question_number += 1
                results.append(item)

        except Exception as e:
            st.warning(f"❌ Failed to parse Page {page_num}: {e}")
else:
    st.warning("❌ No images to process!")

# === Save JSON ===
if json_path:  # Ensure json_path is defined and available
    with open(json_path, "w") as f:
        json.dump(results, f, indent=3)

# === Layout Display ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("📑 PDF Page Previews")
    for _, img_path in images:
        st.image(img_path, use_column_width=True)

with col2:
    st.subheader("🧠 Extracted JSON")
    st.json(results)

# Ensure json_path is defined before using it
if json_path:
    st.success(f"✅ JSON saved to: {json_path}")
else:
    st.warning("❌ Failed to save JSON: folder path not defined")
