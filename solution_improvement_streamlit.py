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
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

# === Prompt for Gemini ===
PROMPT = """
Carefully extract all text content from this image, maintaining the exact order and formatting as it appears.
Preserve all mathematical equations, formulas, and special characters exactly as they appear in the image.
Do not add any headers, descriptions, or labels to the output.

Output only the extracted text content in the following format:

[
{
question_number: 1,
ocr_text: 'This is the PV curve <diagram_1>',
diagrams: [
  {
    id: 'diagram_1',
    coordinates: 'n/a',
    diagram_class: 'graph'
  }
],
pages: [2, 3]
}
]

Important Rules:
- The output must be a list of such question-answer objects.
- Each object must contain:
  - `question_number` in increasing order.
  - `ocr_text`: complete question and answer content, including `<diagram_1>` if any diagram exists.
  - `diagrams`: 
     - If diagram exists → write: `id: 'diagram_1'`, `coordinates: 'n/a'`, and appropriate `diagram_class` ('graph' or 'diagram').
     - If no diagram → set: `id: 'n/a'`, `coordinates: 'n/a'`, `diagram_class: 'n/a'`.
  - `pages`: Must always be shown as a list of integers in square brackets, like `[2, 3]`. Ensure the square brackets appear on the same line.

- Understand the context to group full question-answer blocks together.
- Maintain the output structure and avoid inserting extra commentary or descriptions.
"""

# === Streamlit UI ===
st.set_page_config(layout="wide")
st.title("Solution Improvement")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

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
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img_path = os.path.join(folder_path, f"page_{page_num + 1}.png")
        pix.save(img_path)
        images.append((page_num + 1, img_path))

    # === Process Images with Gemini ===
    st.info("🤖 Sending images to Gemini for text + diagram extraction...")
    results = []
    question_number = 1

    for page_num, img_path in images:
        try:
            image = Image.open(img_path)
            response = model.generate_content([PROMPT, image])
            parsed = eval(response.text.strip())
            for item in parsed:
                item["question_number"] = question_number
                question_number += 1
                results.append(item)
        except Exception as e:
            st.warning(f"❌ Failed to parse Page {page_num}: {e}")

    # === Save JSON ===
    json_path = os.path.join(folder_path, "output.json")
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

    st.success(f"✅ JSON saved to: {json_path}")
