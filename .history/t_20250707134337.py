import os
import json
from PIL import Image, ImageDraw
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import cv2
import streamlit as st
import re


# === Load API Key ===
load_dotenv()
model_name = "gemini-2.5-pro"
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
model = genai.GenerativeModel(model_name)

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
def draw_bounding_boxes(img, coords):
    # Open image using PIL and ensure it's in RGBA mode for transparency
    img = img.convert("RGBA")
    
    # Create drawing context
    draw = ImageDraw.Draw(img)

    # Define a stronger highlight color (e.g., yellow with full opacity)
    highlight_color = (190, 195, 0, 255)  # RGBA: Red, Green, Blue, Alpha (higher opacity)

    for box in coords:  # Assuming coords is a list of bounding boxes
        if isinstance(box, list) or isinstance(box, tuple):  # Ensure box is iterable
            if len(box) == 4:  # Ensure the box has 4 elements (ymin, xmin, ymax, xmax)
                # Directly use the coordinates without dividing by 1000 (since they are in pixels)
                ymin, xmin, ymax, xmax = box

                # Convert to absolute pixel values based on the image size (not necessary here)
                left = xmin  # Directly use xmin, as these values are in pixels
                top = ymin   # Directly use ymin
                right = xmax # Directly use xmax
                bottom = ymax # Directly use ymax

                # Create a transparent overlay of the same size as the image
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))

                # Draw the translucent background only in the bounding box region on the overlay
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle([left, top, right, bottom], fill=highlight_color)

                # Composite the original image with the overlay (keeping text visible)
                img = Image.alpha_composite(img, overlay)

    return img


# === Send to Gemini for OCR ===
def send_to_gemini(image, prompt):
    try:
        # Send request to Gemini with user prompt and image
        response = model.generate_content([prompt] + [image])  # Batch processing
        raw_response = response.text.strip()

        # Print raw response for debugging
        print(f"Raw response from Gemini:\n{raw_response}")

        # Clean the response to extract bounding box coordinates
        # Regular expression to extract the coordinates (e.g., [597, 366, 629, 580])
        match = re.search(r'\[\d+,\s*\d+,\s*\d+,\s*\d+\]', raw_response)

        if match:
            # Extract the bounding box as a string and convert to a list
            bounding_boxes = json.loads(match.group(0))
            print(f"Parsed bounding boxes: {bounding_boxes}")
            return bounding_boxes
        else:
            print("❌ No bounding boxes found in the response.")
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

        # Text input for user prompt
        user_input = st.text_area("Enter your prompt:", 
                                  """Return bounding boxes as JSON arrays on the line "" as [ymin, xmin, ymax, xmax]""")
        
        # Enter button to send data to Gemini
        if st.button('Send to Gemini'):
            if user_input:
                st.write("Processing image with Gemini OCR...")
                results = send_to_gemini(resized_image, user_input)

                if results:
                    # Show the raw OCR results (bounding boxes in JSON format)
                    st.subheader("OCR Results (Bounding Boxes in JSON format)")
                    st.json(results)

                    # Extract bounding box coordinates from the result
                    coords = []
                    if isinstance(results, list):
                        # If the results are already in a list format like [318, 267, 344, 426], process directly
                        coords = results  # Assuming a single bounding box is returned

                    if coords:
                        # Draw bounding boxes and display the image
                        image_with_boxes = draw_bounding_boxes(image, coords)
                        st.subheader("Image with Bounding Boxes")
                        st.image(image_with_boxes, caption="Image with Bounding Boxes", use_column_width=True)
                    else:
                        st.write("❌ No bounding boxes found in the OCR result.")
            else:
                st.write("❌ Please enter a valid prompt.")

if __name__ == "__main__":
    main()
