#images_for gemini model to generate coords
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os

# Set your API key here
api_key = ""

# Create a GenAI client with the API key
client = genai.Client(api_key=api_key)

# Open the image
image_path = '/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/01_1002115268961841141690701450/page_1.png'
image = Image.open(image_path)

# Define your text input
text_input = ''

# Send request to the GenAI model
response = client.models.generate_content(
    model="gemini-2.0-flash-preview-image-generation",
    contents=[text_input, image],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)

# Process the response
for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)  # Print the text response
    elif part.inline_data is not None:
        # Load the image data from the response
        generated_image = Image.open(BytesIO(part.inline_data.data))

        # Save the generated image to a file
        output_image_path = '/path/to/save/generated_image.png'  # Specify your desired file path here
        generated_image.save(output_image_path)  # Save the image

        # Show the generated image
        generated_image.show()  # Optionally display the image

        # Print the output path
        print(f"Image saved at: {output_image_path}")


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
Return bounding boxes as JSON arrays on all texts [ymin, xmin, ymax, xmax]

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
        # Send request to Gemini
        response = model.generate_content([PROMPT] + resized_images_objs)  # Batch processing
        raw_response = response.text.strip()

        # Print raw response for debugging
        print(f"Raw response from Gemini:\n{raw_response}")

        # Clean and parse JSON response
        cleaned = raw_response.strip('```json').strip('```').strip()

        # Check if there are multiple instances of invalid characters
        if cleaned.startswith("[") and cleaned.endswith("]"):
            # Try parsing JSON
            parsed = json.loads(cleaned)
            return parsed
        else:
            print(f"❌ Malformed JSON: {cleaned}")
            return None
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
        output_json_filename = f"outpukt.json"
        json_path = os.path.join(output_folder, output_json_filename)

        # Save the OCR results
        with open(json_path, "w") as f:
            json.dump(results, f, indent=3)

        print(f"OCR results saved to {json_path}")
    else:
        print("❌ No results from Gemini OCR")

# Running the process with a given PDF file and output folder
pdf_file_path = "/mnt/shared-storage/yolov11L_Image_training_set_400/Solution_Grading/pdf/C01_10021008481039611101693742355.pdf"  # Replace with your PDF file path
output_folder = "/mnt/shared-storage/yolov11L_Image_training_set_400/Solution_Grading/pdf"  # Replace with your output folder path
main(pdf_file_path, output_folder)
