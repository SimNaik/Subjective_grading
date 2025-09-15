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
import time  # Import time module for timing the process
import cv2
import numpy as np

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

# === Preprocess Image (Resize Function) ===
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

    return original_size, (new_h, new_w), resized_image_pil  # Return original size, new size, and the resized image

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

    resized_images = []  # List to store resized image paths

    # Save images directly in the main folder and resize them
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)

        # Save the images directly inside the main folder (no model subfolders for images)
        img_path = os.path.join(folder_path, f"page_{page_num + 1}.png")
        pix.save(img_path)  # Save image for both models (no need for model subfolders)

        # Open the image and resize it
        original_size, new_size, resized_image = resize_image(Image.open(img_path), dim=768)
        
        # Display the resize information in Streamlit
        st.write(f"**Original Image Size (Page {page_num + 1}):** {original_size[0]}x{original_size[1]}")
        st.write(f"**Resized Image Size (Page {page_num + 1}):** {new_size[0]}x{new_size[1]}")

        # Save resized images to the model folder (both model 1 and model 2)
        resized_img_path_1 = os.path.join(model_1_folder, f"resized_page_{page_num + 1}.jpeg")
        resized_img_path_2 = os.path.join(model_2_folder, f"resized_page_{page_num + 1}.jpeg")
        
        resized_image.save(resized_img_path_1)
        resized_image.save(resized_img_path_2)

        resized_images.append(resized_image)  # Add resized image to list

    # Load images into cache from the main folder
    images = load_images(folder_path, len(doc))
    images_b64_model_1 = load_base64_images(folder_path, len(doc))
    images_b64_model_2 = load_base64_images(folder_path, len(doc))

# === Model Processing (for both models) ===
results_1, results_2 = [], []

if uploaded_file:
    # Start timer for Model 1
    start_time_1 = time.time()
    st.info(f"🤖 Sending images to {model_1_name} for text + diagram extraction...")
    # Model 1 Processing
    json_path_1 = os.path.join(model_1_folder, f"{pdf_name}_{model_1_name}.json")
    model_1 = get_model(model_1_name)  # Get Model 1
    if resized_images:
        try:
            # Resize each image before sending to Gemini API
            resized_images_objs_1 = [resize_image(img, dim=768)[2] for img in resized_images]
            response_1 = model_1.generate_content([PROMPT] + resized_images_objs_1)
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

    # End timer for Model 1 and log the time
    end_time_1 = time.time()
    model_1_processing_time = end_time_1 - start_time_1

    # Start timer for Model 2
    start_time_2 = time.time()
    st.info(f"🤖 Sending images to {model_2_name} for text + diagram extraction...")
    # Model 2 Processing
    json_path_2 = os.path.join(model_2_folder, f"{pdf_name}_{model_2_name}.json")
    model_2 = get_model(model_2_name)  # Get Model 2

    if resized_images:
        try:
            # Resize each image before sending to Gemini API
            resized_images_objs_2 = [resize_image(img, dim=768)[2] for img in resized_images]
            response_2 = model_2.generate_content([PROMPT] + resized_images_objs_2)
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

    # End timer for Model 2 and log the time
    end_time_2 = time.time()
    model_2_processing_time = end_time_2 - start_time_2

    # Log the processing times to a text file
    timing_file_path = os.path.join(folder_path, "model_processing_times.txt")
    with open(timing_file_path, "w") as f:
        f.write(f"Model 1 ({model_1_name}) processing time: {model_1_processing_time:.2f} seconds\n")
        f.write(f"Model 2 ({model_2_name}) processing time: {model_2_processing_time:.2f} seconds\n")

    # Show processing times on Streamlit
    st.info(f"🕒 Model 1 processing time: {model_1_processing_time:.2f} seconds")
    st.info(f"🕒 Model 2 processing time: {model_2_processing_time:.2f} seconds")


# === Model Output Toggle Buttons ===
BOX_HEIGHT = 1000

col1, col2 = st.columns(2)

# ---------- Column 1 (PDF Preview and Navigation) ----------
# --- PDF Preview and Navigation ---
with col1:
    st.subheader("📑 PDF Page Preview")

    if not uploaded_file:
        st.info("📂 Please upload a PDF to see the preview here.")
    else:
        if images_b64_model_1:
            # Navigation buttons for pages
            nav1, nav2, nav3 = st.columns([1, 2, 1])
            with nav1:
                if st.button("⬅️ Previous", key="prev_btn") and st.session_state.current_page > 0:
                    st.session_state.current_page -= 1
            with nav2:
                st.markdown(f"**Page {st.session_state.current_page + 1} of {len(images_b64_model_1)}**")
            with nav3:
                if st.button("Next ➡️", key="next_btn") and st.session_state.current_page < len(images_b64_model_1) - 1:
                    st.session_state.current_page += 1

            # Set the path to the resized image for the current page
            resized_img_path_1 = os.path.join(model_1_folder, f"resized_page_{st.session_state.current_page + 1}.jpeg")

            # Display the resized image directly from the file path
            if os.path.exists(resized_img_path_1):
                st.image(resized_img_path_1, use_column_width=True, caption=f"Resized Image (Page {st.session_state.current_page + 1})")
            else:
                st.warning(f"❌ Resized image for page {st.session_state.current_page + 1} not found.")
        else:
            st.warning("❌ No images available")


# ---------- Column 2 (JSON Output Buttons) ----------
with col2:
    st.subheader("🧠 Extracted JSON")

    # Buttons to toggle between model 1 and model 2 output
    model_1_btn = st.button(f"Show {model_1_name} JSON", key="model_1_btn")
    model_2_btn = st.button(f"Show {model_2_name} JSON", key="model_2_btn")

    # Default: Show Model 1 JSON with heading
    if model_1_btn or not model_2_btn:
        st.markdown(f"### Showing JSON Output from **{model_1_name}**")
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

    # Show Model 2 JSON with heading when clicked
    if model_2_btn:
        st.markdown(f"### Showing JSON Output from **{model_2_name}**")
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