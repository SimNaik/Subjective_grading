import streamlit as st
import os
import fitz  # PyMuPDF
from PIL import Image
import json
import google.generativeai as genai
from dotenv import load_dotenv

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

# === Process Images with Gemini (Send All in One Batch) ===
st.info("🤖 Sending images to Gemini for text + diagram extraction...")
results = []

# Ensure that folder_path is defined before using it
if folder_path and images:
    json_path = os.path.join(folder_path, "output.json")
else:
    json_path = ""  # Define json_path even if the images are empty or no file is uploaded

# Ensure that all images are collected together in a list and sent as one request
if images:
    try:
        # Load all images at once and send to Gemini API
        image_objects = [Image.open(img_path) for img_path in images]

        # Combine the images and the prompt into a list to send as a batch
        response = model.generate_content([PROMPT] + image_objects)

        # Raw Response from Gemini
        raw_response = response.text.strip()
        st.write(f"Raw Response from Gemini: {raw_response}")

        # Clean the response (strip unwanted characters like backticks)
        cleaned_response = raw_response.strip('```json').strip('```').strip()  # Remove triple backticks and any extra spaces

        # Attempt to parse the cleaned JSON
        try:
            parsed = json.loads(cleaned_response)
            results.extend(parsed)  # Append the parsed JSON data to the results list
        except json.JSONDecodeError as json_error:
            st.warning(f"❌ Failed to parse JSON: {json_error}")

    except Exception as e:
        st.warning(f"❌ Failed to process the images: {e}")

else:
    st.warning("❌ No images to process!")

# === Save JSON ===
if json_path:  # Ensure json_path is defined and available
    with open(json_path, "w") as f:
        json.dump(results, f, indent=3)

# Column Layout
col1, col2 = st.columns([3, 7])

# Column 1: PDF Navigation and Preview
with col1:
    st.subheader("📑 PDF Page Preview")
    if images and st.session_state.current_page < len(images):
        st.image(images[st.session_state.current_page], use_column_width=True)

        # Navigation Buttons
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if st.button("⬅️ Previous") and st.session_state.current_page > 0:
                st.session_state.current_page -= 1
        with nav_col2:
            st.write(f"Page {st.session_state.current_page + 1} of {len(images)}")
        with nav_col3:
            if st.button("Next ➡️") and st.session_state.current_page < len(images) - 1:
                st.session_state.current_page += 1
    else:
        st.warning("❌ No images available")

# Column 2: JSON Display
with col2:
    st.subheader("🧠 Extracted JSON")
    
    # Add custom CSS to make JSON scrollable
    st.markdown("""
        <style>
        .scrollable-json {
            overflow-y: auto;        /* Enables vertical scrolling */
            max-height: 300px;       /* Limits the height, making it scrollable */
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Wrap the JSON output inside a scrollable div
    st.markdown('<div class="scrollable-json">', unsafe_allow_html=True)
    
    # Use st.json() to render the JSON data
    st.json(results)
    
    # Close the scrollable div tag
    st.markdown('</div>', unsafe_allow_html=True)

st.success(f"✅ JSON saved to: {json_path}")
