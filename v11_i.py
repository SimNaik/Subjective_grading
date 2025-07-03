#this is basically to detect the line which is wrong
#this sends image which will beresized and output is json no streamlit no pdf
import os
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
Given an image:
Sentence Extraction: Extract a specific sentence from the image -  "Tangents drawn from the same".
Bounding Box Coordinates: For the sentence extracted, return the OCR-detected text along with the coordinates of the bounding box in the format [ymin, xmin, ymax, xmax] where:
ymin is the top vertical coordinate of the bounding box.
xmin is the left horizontal coordinate of the bounding box.
ymax is the bottom vertical coordinate of the bounding box.
xmax is the right horizontal coordinate of the bounding box.
Output: Return the result for that specific sentence only, including the sentence text and its bounding box coordinates in the following JSON format:
Example JSON Output for a single image (containing only the target sentence):
[
  {
    "image_name": "image_name.png",
    "text": "Tangents drawn from the same",
    "bbox": [120, 100, 150, 300]
  }
]
Notes for Image Processing:
Extract only the sentence that matches the given input.
Return only the OCR result for that specific sentence and its coordinates, not the entire image text.
If the sentence is not found in the image, return an empty list for that image (e.g., "image_name": "image_name.png", "text": []).
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

# === Load Image ===
def load_image(image_path):
    img = Image.open(image_path)
    return img

# === Load Base64 Image ===
def load_base64_images(folder_path, num_images):
    b64_list = []
    for i in range(num_images):
        img_filename_dim = f"DIM_{dim}_IMAGE_{i + 1}.jpeg"  # Use dim variable here
        img_path_dim = os.path.join(folder_path, img_filename_dim)

        if os.path.exists(img_path_dim):
            path = img_path_dim
        else:
            print(f"❌ Image {img_filename_dim} not found in {folder_path}")
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
        # Removing unwanted characters and trying different cleaning strategies
        cleaned = raw_response.strip('```json').strip('```').strip()

        # Check if cleaned response is valid JSON
        if cleaned.startswith("[") and cleaned.endswith("]"):
            try:
                # Attempt to parse the cleaned response as JSON
                parsed = json.loads(cleaned)
                return parsed
            except json.JSONDecodeError as e:
                print(f"❌ JSON decoding error: {e}")
                return None
        else:
            print(f"❌ Malformed JSON: {cleaned}")
            return None

    except Exception as e:
        print(f"❌ Failed to process images: {e}")
        return None

# === Main Process ===
def main(image_file_path, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Step 1: Load Image
    img = load_image(image_file_path)

    # Step 2: Resize Image
    original_size, new_size, resized_image = resize_image(img, dim=dim)
    
    # Save resized image
    img_filename_dim = f"DIM_{dim}_IMAGE_1.jpeg"
    resized_image.save(os.path.join(output_folder, img_filename_dim))

    # Step 3: Load base64 image
    images_b64 = load_base64_images(output_folder, 1)

    # Step 4: Send to Gemini for OCR
    results = send_to_gemini([resized_image])

    if results:
        output_json_filename = f"output.json"
        json_path = os.path.join(output_folder, output_json_filename)

        # Save the OCR results
        with open(json_path, "w") as f:
            json.dump(results, f, indent=3)

        print(f"OCR results saved to {json_path}")
    else:
        print("❌ No results from Gemini OCR")


image_file_path = "/mnt/shared-storage/yolov11L_Image_training_set_400/Solution_Grading/check_4_i/page_5.jpeg"  # Replace with your image file path
output_folder = "/mnt/shared-storage/yolov11L_Image_training_set_400/Solution_Grading/check_4_i"  # Replace with your output folder path
main(image_file_path, output_folder)
