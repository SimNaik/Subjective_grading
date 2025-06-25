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
import numpy as np
import cv2

# === Load API Key ===
load_dotenv()
model_name = "gemini-2.5-pro"
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
model = genai.GenerativeModel(model_name)

# === Prompt for Gemini ===
PROMPT = """
Carefully extract all text content from the PDF (Ignore any template, header or headings of the page, footer, or decorative elements such as 'Date', 'Page'.), maintaining the exact order and formatting as it appears.
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
  - question_number in increasing order which is the question number of the content,Question numbers may appear in various formats—such as compound forms like 11. (1), 11. (2), or simple forms like 7, 8, 9. Always preserve the original numbering exactly as it appears in the document..
  - ocr_text: complete question (including the question number present) and answer content, including <diagram_1> if any diagram exists.
  - diagrams: 
     - If diagram exists → write: id: 'diagram_1', coordinates: 'n/a', and appropriate diagram_class ('graph' or 'diagram').
     - If no diagram → set: id: 'n/a', coordinates: 'n/a', diagram_class: 'n/a'.
  - pages: The page number of the content ,Must always be shown as a list of integers in square brackets.

- Understand the context to group full question-answer blocks together.
- Maintain the output structure and avoid inserting extra commentary or descriptions.
- Any text that is struck through (strikethrough formatting) must be completely ignored and excluded from the output.
"""

# === Resize Image Function ===
def resize_image(image, dim=768, save_path=None):
    # Convert image to array if not already in array format
    image1 = np.array(image.convert('RGB'))  # Ensure the image is in RGB mode
    
    # Save the original size of the image
    original_size = image1.shape  # (height, width, channels)
    
    # Convert image to grayscale (for simplicity, keep this part)
    image1 = image1.mean(axis=2)  # Convert image to grayscale
    
    h, w = image1.shape
    if w > h:
        new_w = dim
        new_h = int(h * (dim / w))
    else:
        new_h = dim
        new_w = int(w * (dim / h))
    
    # Resize the image
    resized_image = cv2.resize(image1, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Convert back to Image format and ensure it is in 'RGB' mode before saving
    resized_image_pil = Image.fromarray(resized_image)
    resized_image_pil = resized_image_pil.convert('RGB')  # Convert to RGB before saving
    
    # Save resized image to the given path
    if save_path:
        resized_image_pil.save(save_path)

    return original_size, (new_h, new_w), resized_image_pil

# Streamlit Configuration
st.set_page_config(layout="wide")
st.title("Solution Improvement")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
folder_path = ""
images = []

if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

@st.cache_data
def load_images(folder_path, num_pages):
    return [os.path.join(folder_path, f"page_{i+1}.jpeg") for i in range(num_pages)]

@st.cache_data(show_spinner=False)
def load_base64_images(folder_path, num_pages):
    b64_list = []
    for i in range(num_pages):
        path = os.path.join(folder_path, f"page_{i+1}.jpeg")
        with open(path, "rb") as f:
            b64_list.append(base64.b64encode(f.read()).decode())
    return b64_list

# === Handle upload & convert to images ===
if uploaded_file:
    pdf_name = uploaded_file.name.replace(".pdf", "")
    folder_name = f"{pdf_name}-{model_name}"
    folder_path = os.path.join("Gemini_ocr_output", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    pdf_path = os.path.join(folder_path, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    st.info("🔄 Converting PDF to images...")
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img_path = os.path.join(folder_path, f"page_{page_num+1}.jpeg")
        pix.save(img_path)

        # Resize the image before saving
        image_pil = Image.open(img_path)  # Open the image from the file path
        original_size, new_size, resized_image = resize_image(image_pil, dim=768, save_path=img_path)

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
            for image in image_objects:
                # Resize the image
                _, _, resized_image = resize_image(image, dim=768, save_path=None)  # Not saving again here
                response = model.generate_content([PROMPT, resized_image])  # Assuming model accepts single image + prompt
                raw = response.text.strip()
                st.write(f"Raw Response from Gemini: {raw}")
                cleaned = raw.strip('```json').strip('```').strip()
                parsed = json.loads(cleaned)
                results.append(parsed)
        except Exception as e:
            st.warning(f"❌ Failed to process images: {e}")
    else:
        st.warning("❌ No images to process!")

    if json_path and results:
        with open(json_path, "w") as f:
            json.dump(results, f, indent=3)

# Display Resized Image in Streamlit
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
            <img src="data:image/jpeg;base64,{b64}"
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
