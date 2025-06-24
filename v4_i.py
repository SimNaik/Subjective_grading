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
model_name = "gemini-2.5-flash"  # Model name
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

# === Streamlit UI ===
st.set_page_config(layout="wide")
st.title("Solution Improvement")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

# Initialize folder_path and images to ensure they are defined before usage
folder_path = ""
images = []

# Initialize current_page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

# Cache image loading to avoid reloading each time
@st.cache_data
def load_images(folder_path, num_pages):
    image_list = []
    for page_num in range(num_pages):
        img_path = os.path.join(folder_path, f"page_{page_num + 1}.png")
        image_list.append(img_path)
    return image_list

if uploaded_file:
    # === Setup Folder ===
    pdf_name = uploaded_file.name.replace(".pdf", "")  # Extract PDF name
    folder_name = f"{pdf_name}-{model_name}"  # Combine PDF name and model name
    folder_path = os.path.join("uploads", folder_name)  # Define folder path with model name
    os.makedirs(folder_path, exist_ok=True)  # Create the folder if it doesn't exist

    pdf_path = os.path.join(folder_path, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    # === Convert PDF to Images ===
    st.info("🔄 Converting PDF to images...")
    doc = fitz.open(pdf_path)

    # Save images and load them into the cache
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img_path = os.path.join(folder_path, f"page_{page_num + 1}.png")
        pix.save(img_path)

    # Cache the images
    images = load_images(folder_path, len(doc))  # Pre-load all images in the folder
    
# === After converting PDF to images ===
results = []

if uploaded_file:
    st.info("🤖 Sending images to Gemini for text + diagram extraction…")

    # Define json_path now that we know folder_path
    json_path = os.path.join(folder_path, "output.json") if folder_path else ""

    if images:
        try:
            # Batch‐send all page images
            image_objects = [Image.open(p) for p in images]
            response = model.generate_content([PROMPT] + image_objects)

            raw = response.text.strip()
            st.write(f"Raw Response from Gemini: {raw}")

            cleaned = raw.strip('```json').strip('```').strip()
            parsed = json.loads(cleaned)
            results.extend(parsed)
        except Exception as e:
            st.warning(f"❌ Failed to process the images: {e}")
    else:
        st.warning("❌ No images to process!")

    # Save JSON only if we got results
    if json_path and results:
        with open(json_path, "w") as f:
            json.dump(results, f, indent=3)


BOX_HEIGHT = 1000 # must match your JSON box height

col1, col2 = st.columns(2)

# ---------- Column 1 ----------
with col1:
    st.subheader("📑 PDF Page Preview")

    if not uploaded_file:
        st.info("📂 Please upload a PDF to see the preview here.")
    else:
        # They’ve uploaded—now check for images
        if images and st.session_state.current_page < len(images):
            # (your existing base64+components.html code goes here)
            pil_img = Image.open(images[st.session_state.current_page])
            buf = BytesIO()
            pil_img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            img_html = f"""
            <img
              src="data:image/png;base64,{b64}"
              style="
                height: {BOX_HEIGHT}px;
                width: 100%;
                object-fit: contain;
                display: block;
                margin: 0 auto;
              "
            />
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
