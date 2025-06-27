#this is a one model py file no streamlite where image is resized sent in batches to pro using prompt3
import os
import fitz  # PyMuPDF for PDF processing
from PIL import Image
import json
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import time
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

# === Load PDF, Convert Pages to Images ===
def pdf_to_images(pdf_path, output_folder):
    doc = fitz.open(pdf_path)
    images = []
    num_pages = doc.page_count
    for i in range(num_pages):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=300)
        img_path_default = os.path.join(output_folder, f"page_{i + 1}.jpeg")
        pix.save(img_path_default)
        images.append(img_path_default)
    return images, num_pages

# === Load Base64 Images ===
def load_base64_images(folder_path, num_pages):
    b64_list = []
    for i in range(num_pages):
        img_filename_dim = f"DIM_{dim}_PAGE_{i + 1}.jpeg"  # Use dim variable here
        img_filename_default = f"page_{i + 1}.jpeg"  # Old naming convention

        img_path_dim = os.path.join(folder_path, img_filename_dim)
        img_path_default = os.path.join(folder_path, img_filename_default)

        if os.path.exists(img_path_dim):
            path = img_path_dim
        elif os.path.exists(img_path_default):
            path = img_path_default
        else:
            print(f"❌ Image {img_filename_dim} or {img_filename_default} not found in {folder_path}")
            continue

        with open(path, "rb") as f:
            b64_list.append(base64.b64encode(f.read()).decode())
    return b64_list

# === Batch send to Gemini ===
def send_to_gemini(resized_images_objs):
    try:
        response = model.generate_content([PROMPT] + resized_images_objs)  # Batch processing
        raw = response.text.strip()
        cleaned = raw.strip('```json').strip('```').strip()
        parsed = json.loads(cleaned)
        return parsed
    except Exception as e:
        print(f"❌ Failed to process images: {e}")
        return None

# === Main Process ===
def main(pdf_file_path, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Step 1: Convert PDF to images
    images, num_pages = pdf_to_images(pdf_file_path, output_folder)

    # Step 2: Resize images
    resized_images = []
    for page_num in range(len(images)):
        img_path = images[page_num]
        original_size, new_size, resized_image = resize_image(Image.open(img_path), dim=dim)
        
        # Save resized image
        img_filename_dim = f"DIM_{dim}_PAGE_{page_num + 1}.jpeg"
        resized_image.save(os.path.join(output_folder, img_filename_dim))
        
        resized_images.append(resized_image)

    # Step 3: Load base64 images
    images_b64 = load_base64_images(output_folder, len(images))

    # Step 4: Send to Gemini for OCR
    results = send_to_gemini(resized_images)

    if results:
        output_json_filename = f"output.json"
        json_path = os.path.join(output_folder, output_json_filename)

        # Save the OCR results
        with open(json_path, "w") as f:
            json.dump(results, f, indent=3)

        print(f"OCR results saved to {json_path}")
    else:
        print("❌ No results from Gemini OCR")

# Running the process with a given PDF file and output folder
pdf_file_path = "/Users/simrannaik/Desktop/solution_improvement/01_1002115268961841141690701450.pdf"  # Replace with your PDF file path
output_folder = "/Users/simrannaik/Desktop/solution_improvement/Z"  # Replace with your output folder path
main(pdf_file_path, output_folder)
