#here i am using one model and resized the image to 7689 also 
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
import time  # Importing time module

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
"""

# === Set the dimension value ===
dim = 768  # Define the dimension value

# === Resize Image Function ===
def resize_image(image, dim=dim, save_path=None):
    image1 = np.array(image.convert('RGB'))  # Ensure the image is in RGB mode
    original_size = image1.shape  # (height, width, channels)
    image1 = image1.mean(axis=2)  # Convert image to grayscale
    h, w = image1.shape
    if w > h:
        new_w = dim
        new_h = int(h * (dim / w))
    else:
        new_h = dim
        new_w = int(w * (dim / h))
    resized_image = cv2.resize(image1, (new_w, new_h), interpolation=cv2.INTER_AREA)
    resized_image_pil = Image.fromarray(resized_image)
    resized_image_pil = resized_image_pil.convert('RGB')  # Convert to RGB before saving
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

# === load_base64_images function ===
@st.cache_data(show_spinner=False)
def load_base64_images(folder_path, num_pages):
    b64_list = []
    for i in range(num_pages):
        # Correct naming conventions for both types of images
        img_filename_dim = f"DIM_{dim}_PAGE_{i + 1}.jpeg"  # Use dim variable here
        img_filename_default = f"page_{i + 1}.jpeg"  # Old naming convention

        # Check for both image filenames
        img_path_dim = os.path.join(folder_path, img_filename_dim)
        img_path_default = os.path.join(folder_path, img_filename_default)

        # Check for existence of either file
        if os.path.exists(img_path_dim):
            path = img_path_dim
        elif os.path.exists(img_path_default):
            path = img_path_default
        else:
            st.warning(f"❌ Image {img_filename_dim} or {img_filename_default} not found in {folder_path}")
            continue  # Skip to next page if neither image is found

        # Load the base64-encoded image
        with open(path, "rb") as f:
            b64_list.append(base64.b64encode(f.read()).decode())
    
    return b64_list


# === Handle upload & convert to images ===
if uploaded_file:
    # Get the PDF file name and set the folder path
    pdf_name = uploaded_file.name.replace(".pdf", "")
    folder_name = f"{pdf_name}-{model_name}"
    folder_path = os.path.join("Gemini_ocr_output", folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Save the uploaded PDF file to the folder
    pdf_path = os.path.join(folder_path, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    st.info("🔄 Converting PDF to images...")
    doc = fitz.open(pdf_path)

    resized_images = []  # List to store resized image objects

    # Save images directly in the same folder and resize them
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)

        # Naming conventions
        img_filename_dim = f"DIM_{dim}_PAGE_{page_num + 1}.jpeg"
        img_filename_default = f"page_{page_num + 1}.jpeg"

        # Paths for both images
        img_path_dim = os.path.join(folder_path, img_filename_dim)
        img_path_default = os.path.join(folder_path, img_filename_default)

        # Save the original image with the default name
        pix.save(img_path_default)

        # Now that the original image is saved, open it and resize it
        original_size, new_size, resized_image = resize_image(Image.open(img_path_default), dim=dim)

        # Save the resized image
        resized_image.save(img_path_dim)

        # Display the resize information in Streamlit
        st.write(f"**Original Image Size (Page {page_num + 1}):** {original_size[0]}x{original_size[1]}")
        st.write(f"**Resized Image Size (Page {page_num + 1}):** {new_size[0]}x{new_size[1]}")

        resized_images.append(resized_image)  # Add resized image to list

    # Update load_base64_images to use the correct naming convention
    images_b64 = load_base64_images(folder_path, len(doc))
else:
    images_b64 = []


# === Batch send to Gemini ===
results = []
if uploaded_file:
    st.info("🤖 Sending images to Gemini …")
    output_json_filename = f"{pdf_name}-{model_name}_output.json"
    json_path = os.path.join(folder_path, output_json_filename)
    
    # Start time tracking for total OCR process
    start_time = time.time()
    
    # Send images in batch (all resized images at once)
    if resized_images:
        try:
            # Resize all images before sending them to Gemini (resize step already done above)
            resized_images_objs = resized_images  # List of resized images
            
            # Send all images in a batch to Gemini
            response = model.generate_content([PROMPT] + resized_images_objs)  # Batch processing
            
            # Capture time after batch processing
            end_time = time.time()
            total_processing_time = end_time - start_time
            st.write(f"Raw Response from Gemini: {response.text}")

            # Process the response
            raw = response.text.strip()
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

    # End time tracking for total OCR process
    st.info(f"Total processing time: {total_processing_time:.2f} seconds")

    # Save the timings in a text file
    time_log_path = os.path.join(folder_path, f"{model_name}_timing.txt")
    with open(time_log_path, "w") as log_file:
        log_file.write(f"Total time taken for OCR: {total_processing_time:.2f} seconds\n")

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
            # Navigation buttons for pages
            nav1, nav2, nav3 = st.columns([1, 2, 1])
            with nav1:
                if st.button("⬅️ Previous", key="prev_btn") and st.session_state.current_page > 0:
                    st.session_state.current_page -= 1
            with nav2:
                st.markdown(f"**Page {st.session_state.current_page + 1} of {len(images_b64)}**")
            with nav3:
                if st.button("Next ➡️", key="next_btn") and st.session_state.current_page < len(images_b64) - 1:
                    st.session_state.current_page += 1

            # Set the path to the resized image for the current page
            resized_img_path_1 = os.path.join(folder_path, f"DIM_{dim}_PAGE_{st.session_state.current_page + 1}.jpeg")

            # Display the resized image directly from the file path
            if os.path.exists(resized_img_path_1):
                st.image(resized_img_path_1, use_column_width=True, caption=f"Resized Image (Page {st.session_state.current_page + 1})")
            else:
                st.warning(f"❌ Resized image for page {st.session_state.current_page + 1} not found.")
        else:
            st.warning("❌ No images available")

# ---------- Column 2 (JSON Output) ----------
with col2:
    st.subheader("🧠 Extracted JSON")

    # Display extracted JSON data for the batch processed images
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
