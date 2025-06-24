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

# === Streamlit UI ===
st.set_page_config(layout="wide")
st.title("Solution Improvement")

# === Load API Key ===
load_dotenv()

# Models list for dropdown selection
model_options = [
    "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite-preview-06-17",
    "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"
]

# Dropdown to select Model 1
selected_model_1 = st.selectbox("Select Model 1", model_options, key="model_1", index=None)

# Dropdown to select Model 2
selected_model_2 = st.selectbox("Select Model 2", model_options, key="model_2", index=None)

# Set model names dynamically based on dropdown selection
model_1_name = selected_model_1
model_2_name = selected_model_2

# Function to initialize model based on selected model name
def get_model(model_name):
    if model_name:
        genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
        return genai.GenerativeModel(model_name)
    else:
        raise ValueError("Model name is not defined")

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
    { id: 'diagram_1', coordinates: 'n/a', diagram_class: 'graph or diagram' }
  ],
  pages: [2]
}
]

Important Rules:
- The output must be a list of such question-answer objects.
- Each object must contain:
  - question_number in increasing order (preserve original numbering exactly).
  - ocr_text: full question-answer text, including <diagram_*> tags.
  - diagrams: id, coordinates, diagram_class ('graph','diagram', or 'n/a').
  - pages: list of integers.
- Ignore any struck-through text.
"""

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

@st.cache_data(show_spinner=False)
def load_base64_images(model_folder, num_pages):
    b64_list = []
    for i in range(num_pages):
        path = os.path.join(model_folder, f"page_{i+1}.png")
        with open(path, "rb") as f:
            b64_list.append(base64.b64encode(f.read()).decode())
    return b64_list

# === Handle upload & convert to images ===
if uploaded_file:
    pdf_name = uploaded_file.name.replace(".pdf", "")
    
    # Main folder named after the PDF
    folder_path = os.path.join("uploads", pdf_name)
    os.makedirs(folder_path, exist_ok=True)

    # Create subfolders for each model within the main folder (only for JSON and PDF)
    model_1_folder = os.path.join(folder_path, f"{pdf_name}_{model_1_name}")
    model_2_folder = os.path.join(folder_path, f"{pdf_name}_{model_2_name}")
    os.makedirs(model_1_folder, exist_ok=True)
    os.makedirs(model_2_folder, exist_ok=True)

    # Save the uploaded PDF in the main folder (no model subfolder)
    pdf_path = os.path.join(folder_path, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    # === Convert PDF to Images ===
    st.info("🔄 Converting PDF to images...")
    doc = fitz.open(pdf_path)

    # Save images directly in the main folder
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)

        # Save the images directly inside the main folder (no model subfolders for images)
        img_path = os.path.join(folder_path, f"page_{page_num + 1}.png")
        pix.save(img_path)  # Save image for both models (no need for model subfolders)

    # Load images into cache from the main folder
    images = load_images(folder_path, len(doc))
    images_b64_model_1 = load_base64_images(folder_path, len(doc))
    images_b64_model_2 = load_base64_images(folder_path, len(doc))

# === Model Processing (for both models) ===
results_1, results_2 = [], []

if uploaded_file:
    # Model 1 Processing
    st.info(f"🤖 Sending images to {model_1_name} for text + diagram extraction...")
    json_path_1 = os.path.join(model_1_folder, f"{pdf_name}_{model_1_name}.json")
    model_1 = get_model(model_1_name)  # Get Model 1
    if images:
        try:
            image_objects_1 = [Image.open(p) for p in images]
            response_1 = model_1.generate_content([PROMPT] + image_objects_1)
            raw_1 = response_1.text.strip()
            cleaned_1 = raw_1.strip('```json').strip('```').strip()
            parsed_1 = json.loads(cleaned_1)
            results_1.extend(parsed_1)
        except Exception as e:
            st.warning(f"❌ Failed to process Model 1 images: {e}")

    # Save Model 1 JSON output
    if json_path_1 and results_1:
        with open(json_path_1, "w") as f:
            json.dump(results_1, f, indent=3)

    # Model 2 Processing
    st.info(f"🤖 Sending images to {model_2_name} for text + diagram extraction...")
    json_path_2 = os.path.join(model_2_folder, f"{pdf_name}_{model_2_name}.json")
    model_2 = get_model(model_2_name)  # Get Model 2
    if images:
        try:
            image_objects_2 = [Image.open(p) for p in images]
            response_2 = model_2.generate_content([PROMPT] + image_objects_2)
            raw_2 = response_2.text.strip()
            cleaned_2 = raw_2.strip('```json').strip('```').strip()
            parsed_2 = json.loads(cleaned_2)
            results_2.extend(parsed_2)
        except Exception as e:
            st.warning(f"❌ Failed to process Model 2 images: {e}")

    # Save Model 2 JSON output
    if json_path_2 and results_2:
        with open(json_path_2, "w") as f:
            json.dump(results_2, f, indent=3)


# === Model Output Toggle Buttons ===
BOX_HEIGHT = 1000

col1, col2 = st.columns(2)

# ---------- Column 1 (PDF Preview and Navigation) ----------
with col1:
    st.subheader("📑 PDF Page Preview")

    if not uploaded_file:
        st.info("📂 Please upload a PDF to see the preview here.")
    else:
        if images_b64_model_1:
            nav1, nav2, nav3 = st.columns([1, 2, 1])
            with nav1:
                if st.button("⬅️ Previous", key="prev_btn") and st.session_state.current_page > 0:
                    st.session_state.current_page -= 1
            with nav2:
                st.markdown(f"**Page {st.session_state.current_page + 1} of {len(images_b64_model_1)}**")
            with nav3:
                if st.button("Next ➡️", key="next_btn") and st.session_state.current_page < len(images_b64_model_1) - 1:
                    st.session_state.current_page += 1

            b64 = images_b64_model_1[st.session_state.current_page]
            img_html = f"""
            <img src="data:image/png;base64,{b64}"
                 style="height:{BOX_HEIGHT}px; width:100%; object-fit:contain;" />
            """
            components.html(img_html, height=BOX_HEIGHT)

        else:
            st.warning("❌ No images available")

# ---------- Column 2 (JSON Output Buttons) ----------
with col2:
    st.subheader("🧠 Extracted JSON")

    # Buttons to toggle between model 1 and model 2 output
    model_1_btn = st.button(f"Show {model_1_name} JSON", key="model_1_btn")
    model_2_btn = st.button(f"Show {model_2_name} JSON", key="model_2_btn")

    # Default display: Model 1 JSON
    json_str_1 = json.dumps(results_1, indent=2)
    box_html_1 = f"""
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
      <pre style="margin:0;">{json_str_1}</pre>
    </div>
    """
    components.html(box_html_1, height=BOX_HEIGHT)

    # Show Model 2 JSON when clicked
    if model_2_btn:
        json_str_2 = json.dumps(results_2, indent=2)
        box_html_2 = f"""
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
          <pre style="margin:0;">{json_str_2}</pre>
        </div>
        """
        components.html(box_html_2, height=BOX_HEIGHT)

