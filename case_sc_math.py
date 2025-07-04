#this prompt is specifically for cbse science and maths question and answer part
import streamlit as st
import os
import fitz  # PyMuPDF
from PIL import Image
import json
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit.components.v1 as components
import base64
from io import BytesIO

# === Load API Key ===
load_dotenv()
model_name = "gemini-2.5-pro"
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
model = genai.GenerativeModel(model_name)

# === Prompt for Gemini ===
PROMPT = """
Carefully extract all text content from the PDF, ignoring any template, headers, headings of the page, footer, or decorative elements such as 'Date', 'Page', 'General instructions', 'Time Allowed', etc. Maintain the exact order and formatting as it appears in the PDF.
Preserve all mathematical equations, formulas, special characters, and explanations exactly as they appear in the PDF.
Do not add any headers, descriptions, or labels to the output.
For each question:
- If the question is broken into multiple sections (e.g., A, B, C), treat them as part of the same question and include all the text under the same `question_number`. For example, if a question has parts A, B, and C, it should be labeled as `question_number: 24_A`, `question_number: 24_B`, and `question_number: 24_C`.
- If options (e.g., A, B, C, D) are present as part of the question, do not separate them. Include them as part of the main question content in the `question_ocr_text`. For example, "A) Option 1, B) Option 2, C) Option 3".
- If the block "For visually impaired students" follows the question, treat this block as a separate entry with the same question number followed by 'v'. For example, if the original question number is 24, the block for visually impaired students should be labeled `24v`. This should be applied **only** if the "For visually impaired students" block is present; otherwise, it should not be included.
Output the extracted text content in the following JSON format:
[
  {
    "question_number": 23,
    "section_number": "A",
    "question_ocr_text": "The above figure shows the formation of an image by a lens shown by a thick line.<Image_1>",
    "pages": [2],
    "mark": 2
  },
  {
    "question_number": 24_A,
    "section_number": "A",
    "question_ocr_text": "The diagram below shows a special case of an eye defect. What is the defect that is shown in the figure? A) Myopia B) Hypermetropia C) Astigmatism D) Cataract",
    "pages": [2],
    "mark": 2
  },
  {
    "question_number": 24_B,
    "section_number": "B",
    "question_ocr_text": "State one cause for such a defect. Explain with reason if a concave lens can be used to correct the defect.",
    "pages": [2],
    "mark": 3
  },
  {
    "question_number": "24v",
    "section_number": "A",
    "question_ocr_text": "<Image_2> For visually impaired students: What type of lens always forms a virtual erect and diminished image? List two uses of such a lens.",
    "pages": [2],
    "mark": 2
  },
  {
    "question_number": 36_A,
    "section_number": "A",
    "question_ocr_text": "Attempt either option A or B. A) What is the fundamental difference between hypermetropia and myopia in terms of the optical experience of a person?",
    "pages": [5],
    "mark": 5
  },
  {
    "question_number": "36_A_i",
    "section_number": "B",
    "question_ocr_text": "What is the defect shown in the figure? (i) Potential Difference across R2.",
    "pages": [5],
    "mark": 6
  },
  {
    "question_number": "36_A_ii",
    "section_number": "B",
    "question_ocr_text": "Value of resistance R2 <Image_3>.",
    "pages": [5],
    "mark": "na"
  },
  {
    "question_number": "36_A_iii",
    "section_number": "B",
    "question_ocr_text": "Value of resistance R1.",
    "pages": [5],
    "mark": "na"
  }
]

The JSON format is now clearly defined:
question_number: The unique identifier for each question.
If a question has marks:
- Include the `mark` field with the relevant score.
- If no marks are provided for the question, set `mark` as "na".
section_number: The section in which the question belongs (e.g., "A", "B").
question_ocr_text: The extracted question text, along with any diagrams/Images or special content .
mark: The mark or score for the question (this was incomplete in your original prompt, so now it's included).
Pages : Page number of the question content
question_number_v : this is for the content of the quesiton under "For visually impaired students"
"""

st.set_page_config(layout="wide")
st.title("Solution Improvement")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
folder_path = ""
images = []

if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

@st.cache_data
def load_images(folder_path, num_pages):
    return [os.path.join(folder_path, f"page_{i+1}.png") for i in range(num_pages)]

@st.cache_data(show_spinner=False)
def load_base64_images(folder_path, num_pages):
    b64_list = []
    for i in range(num_pages):
        path = os.path.join(folder_path, f"page_{i+1}.png")
        with open(path, "rb") as f:
            b64_list.append(base64.b64encode(f.read()).decode())
    return b64_list

# === Handle upload & convert to images ===
if uploaded_file:
    pdf_name = uploaded_file.name.replace(".pdf", "")
    folder_name = f"{pdf_name}-{model_name}"
    folder_path = os.path.join("uploads", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    pdf_path = os.path.join(folder_path, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    st.info("🔄 Converting PDF to images...")
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img_path = os.path.join(folder_path, f"page_{page_num+1}.png")
        pix.save(img_path)

    images = load_images(folder_path, len(doc))
    images_b64 = load_base64_images(folder_path, len(doc))
else:
    images_b64 = []

# === Batch send to Gemini ===
results = []
if uploaded_file:
    st.info("🤖 Sending images to Gemini …")
    json_path = os.path.join(folder_path, "output.json") if folder_path else ""
    if images:
        try:
            image_objects = [Image.open(p) for p in images]
            response = model.generate_content([PROMPT] + image_objects)
            raw = response.text.strip()
            st.write(f"Raw Response from Gemini: {raw}")
            cleaned = raw.strip('```json').strip('```').strip()
            parsed = json.loads(cleaned)
            results.extend(parsed)
        except Exception as e:
            st.warning(f"❌ Failed to process images: {e}")
    else:
        st.warning("❌ No images to process!")

    if json_path and results:
        with open(json_path, "w") as f:
            json.dump(results, f, indent=3)

BOX_HEIGHT = 1000  # fixed height for the image display

col1, col2 = st.columns(2)

# ---------- Column 1 (with nav buttons and dropdown) ----------
with col1:
    st.subheader("📑 PDF Page Preview")

    if not uploaded_file:
        st.info("📂 Please upload a PDF to see the preview here.")
    else:
        if images_b64:
            # ── Navigation Row ───────────────────────────
            nav1, nav2, nav3 = st.columns([1, 2, 1])

            # Previous Button
            with nav1:
                if st.button("⬅️ Previous", key="prev_btn") and st.session_state.current_page > 0:
                    st.session_state.current_page -= 1  # Update current page

            # Page Selection Dropdown
            with nav2:
                # Dropdown for selecting a page, setting current page as default
                selected_page = st.selectbox(
                    "Select Page", 
                    range(1, len(images_b64) + 1),  # range of pages 1 to N
                    index=st.session_state.current_page,  # default to the current page
                    key="page_dropdown"
                )
                # Update current page based on the dropdown selection
                if selected_page != (st.session_state.current_page + 1):
                    st.session_state.current_page = selected_page - 1  # convert to 0-index

            # Next Button
            with nav3:
                if st.button("Next ➡️", key="next_btn") and st.session_state.current_page < len(images_b64) - 1:
                    st.session_state.current_page += 1  # Update current page
            # ─────────────────────────────────────────────

            # Now render the image for the (possibly) updated page
            b64 = images_b64[st.session_state.current_page]
            img_html = f"""
            <img src="data:image/png;base64,{b64}"
                 style="height:{BOX_HEIGHT}px; width:100%; object-fit:contain;" />
            """
            components.html(img_html, height=BOX_HEIGHT)

        else:
            st.warning("❌ No images available")

# ---------- Column 2 (unchanged) ----------
with col2:
    st.subheader("🧠 Extracted JSON")
    json_str = json.dumps(results, indent=2)
    box_html = f"""
    <div style="
        height: {BOX_HEIGHT}px;
        width: 100%;
        overflow-y: auto;
        border: 1px solid #ddd;
        padding: 10px;
        box-sizing: border-box;
        font-family: monospace;
        white-space: pre-wrap;
    ">
      <pre style="margin:0;">{json_str}</pre>
    </div>
    """
    components.html(box_html, height=BOX_HEIGHT)
