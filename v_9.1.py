#here i am sending one image to gemnin after resizing it, not sending pdf
import os
from PIL import Image
import json
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import numpy as np
import cv2

# === Load API Key ===
load_dotenv()
model_name = "gemini-2.5-pro"
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
model = genai.GenerativeModel(model_name)

# === Prompt for Gemini ===
PROMPT = """
Return bounding boxes as JSON arrays [ymin, xmin, ymax, xmax] on all texts
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

# === Load Image and Convert to Base64 ===
def load_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# === Send Image to Gemini ===
def send_to_gemini(resized_image_b64):
    try:
        # Send request to Gemini
        response = model.generate_content([PROMPT, resized_image_b64])  # Batch processing
        raw_response = response.text.strip()
        
        # Print raw response for debugging
        print(f"Raw response from Gemini:\n{raw_response}")

        # Clean and parse JSON response
        cleaned = raw_response.strip('```json').strip('```').strip()
        parsed = json.loads(cleaned)
        return parsed
    except Exception as e:
        print(f"❌ Failed to process image: {e}")
        return None

# === Main Process ===
def main(image_file_path, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Step 1: Load and Resize the Image
    image = Image.open(image_file_path)
    original_size, new_size, resized_image = resize_image(image, dim=dim)
    
    # Save resized image
    img_filename_dim = f"DIM_{dim}_image.jpeg"
    resized_image.save(os.path.join(output_folder, img_filename_dim))
    
    # Step 2: Convert Image to Base64
    resized_image_b64 = load_base64_image(os.path.join(output_folder, img_filename_dim))

    # Step 3: Send Image to Gemini for OCR
    results = send_to_gemini(resized_image_b64)

    if results:
        output_json_filename = f"output.json"
        json_path = os.path.join(output_folder, output_json_filename)

        # Save the OCR results
        with open(json_path, "w") as f:
            json.dump(results, f, indent=3)

        print(f"OCR results saved to {json_path}")
    else:
        print("❌ No results from Gemini OCR")

# Running the process with a given image file and output folder
image_file_path = "/mnt/shared-storage/yolov11L_Image_training_set_400/Solution_Grading/data/1536/M01_10021165141080491171694788750_page_2.jpeg"  # Replace with your image file path
output_folder = "/mnt/shared-storage/yolov11L_Image_training_set_400/Solution_Grading/check"  # Replace with your output folder path
main(image_file_path, output_folder)
