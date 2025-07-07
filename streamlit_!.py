#to send image with 768 with prompt gemini pro 2.5 sending boxes in return 
import os
import json
from PIL import Image, ImageDraw
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import cv2
import streamlit as st
import matplotlib.pyplot as plt

# === Load API Key ===
load_dotenv()
model_name = "gemini-2.5-pro"
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
model = genai.GenerativeModel(model_name)

# === Prompt for Gemini ===
PROMPT = """
Return bounding boxes as JSON arrays on the line ""10. a) Pole: The centre of a spherical mirror is called the pole. It lies in front of a concave mirror."
[ymin, xmin, ymax, xmax] 
"""

# === Set the dimension value ===
dim = 768  # Define the dimension value

# === Resize Image Function ===
def resize_image(image, dim=dim):
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
    return original_size, (new_h, new_w), resized_image_pil

# === Load Image ===
def load_image(image_path):
    img = Image.open(image_path)
    return img

# === Draw Bounding Boxes on Image ===
def draw_bounding_boxes(image, coords):
    # Open image using PIL and ensure it's in RGBA mode for transparency
    image = image.convert("RGBA")
    
    # Create drawing context
    draw = ImageDraw.Draw(image)

    # Define a translucent highlight color (e.g., yellow with ~12% opacity)
    highlight_color = (190, 195, 0, 64)  # RGBA: Red, Green, Blue, Alpha (opacity: 0-255)
    
    for index, box in enumerate(coords):
        ymin, xmin, ymax, xmax = [coord / 1000 for coord in box]  # Normalize to 0-1 range

        # Calculate absolute pixel coordinates
        left = xmin * image.width
        top = ymin * image.height
        right = xmax * image.width
        bottom = ymax * image.height

        # Create a transparent overlay of the same size as the image
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))

        # Draw the translucent background only in the bounding box region on the overlay
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([left, top, right, bottom], fill=highlight_color)

        # Composite the original image with the overlay (keeping text visible)
        image = Image.alpha_composite(image, overlay)

    return image

# === Send to Gemini for OCR ===
def send_to_gemini(image):
    try:
        # Send request to Gemini
        response = model.generate_content([PROMPT] + [image])  # Batch processing
        raw_response = response.text.strip()

        # Print raw response for debugging
        print(f"Raw response from Gemini:\n{raw_response}")

        # Clean and parse JSON response
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

# === Streamlit App ===
def main():
    st.title("Gemini OCR and Bounding Box Visualizer")

    # File upload
    uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Load image
        image = Image.open(uploaded_file)

        # Resize image
        original_size, new_size, resized_image = resize_image(image)

        # Display the resized image
        st.image(resized_image, caption="Uploaded Image", use_column_width=True)

        # Send the image to Gemini for OCR
        st.write("Processing image with Gemini OCR...")
        results = send_to_gemini(resized_image)

        if results:
            # Show the raw OCR results (bounding boxes in JSON format)
            st.subheader("OCR Results (Bounding Boxes in JSON format)")
            st.json(results)

            # Extract bounding box coordinates from the result
            coords = []
            for item in results:
                box_2d = item.get("box_2d", [])
                if box_2d:
                    coords.append(box_2d)

            if coords:
                # Draw bounding boxes and display the image
                image_with_boxes = draw_bounding_boxes(image, coords)
                st.subheader("Image with Bounding Boxes")
                st.image(image_with_boxes, caption="Image with Bounding Boxes", use_column_width=True)
            else:
                st.write("❌ No bounding boxes found in the OCR result.")
        else:
            st.write("❌ No results from Gemini OCR.")

if __name__ == "__main__":
    main()
