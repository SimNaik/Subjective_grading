import os
import json
from PIL import Image, ImageDraw
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import cv2
import streamlit as st

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
def draw_bounding_boxes(image, coords):
    # Open image using PIL and ensure it's in RGBA mode for transparency
    image = image.convert("RGBA")
    
    # Create drawing context
    draw = ImageDraw.Draw(image)

    # Define a translucent highlight color (e.g., yellow with ~12% opacity)
    highlight_color = (190, 195, 0, 114)  # RGBA: Red, Green, Blue, Alpha (opacity: 0-255)
    
    for box in coords:
        # Ensure that the bounding box is in the form of [ymin, xmin, ymax, xmax]
        if len(box) == 4:
            ymin, xmin, ymax, xmax = [coord / 1000 for coord in box]  # Normalize to 0-1 range

            
            # Scale the coordinates to the resized image dimensions
            left = int(xmin * image.width)  # Convert to actual pixel position
            top = int(ymin * image.height)  # Convert to actual pixel position
            right = int(xmax * image.width)  # Convert to actual pixel position
            bottom = int(ymax * image.height)  # Convert to actual pixel position

            # Create a transparent overlay of the same size as the image
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))

            # Draw the translucent background only in the bounding box region on the overlay
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([left, top, right, bottom], fill=highlight_color)

            # Composite the original image with the overlay (keeping text visible)
            image = Image.alpha_composite(image, overlay)

    return image


# === Send to Gemini for OCR ===
def send_to_gemini(image, prompt):
    try:
        # Send request to Gemini with user prompt and image
        response = model.generate_content([prompt] + [image])  # Batch processing
        raw_response = response.text.strip()

        # Print raw response for debugging
        print(f"Raw response from Gemini:\n{raw_response}")

        # Clean the raw response by removing any non-JSON content (e.g., text like 'Hence')
        cleaned = raw_response.strip().lstrip("Hence").strip()  # Strip "Hence" and any leading whitespace
        cleaned = cleaned.strip('```json').strip('```').strip()  # Clean up surrounding backticks if present

        # Check if cleaned response is valid JSON
        if cleaned.startswith("[") and cleaned.endswith("]"):
            try:
                # Attempt to parse the cleaned response as JSON
                parsed = json.loads(cleaned)

                # Check the structure of the parsed result (just print it)
                print(f"Parsed result: {parsed}")

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

                # --- Handle Results --- 
                if results:
                    # Show the raw OCR results (bounding boxes in JSON format)
                    st.subheader("OCR Results (Bounding Boxes in JSON format)")
                    st.json(results)

                    coords = []

                    # Handle case where the result is either a dictionary with "box_2d" or a list of coordinates
                    if isinstance(results, list):
                        # If the result is a list, check if it's a list of bounding boxes or a single bounding box
                        if all(isinstance(item, list) for item in results):
                            # Handle case where it's a list of bounding boxes, each item being a list like [ymin, xmin, ymax, xmax]
                            coords = results
                        else:
                            # Handle single bounding box case, e.g., [600, 376, 626, 465]
                            coords = [results]  # Wrap it in another list to make it a list of bounding boxes
                    elif isinstance(results, dict):
                        # Handle the case where it's a dictionary with "box_2d" key
                        box_2d = results.get("box_2d", [])
                        if box_2d:
                            coords.append(box_2d)

                    if coords:
                        # Draw bounding boxes and display the image
                        image_with_boxes = draw_bounding_boxes(resized_image, coords)

                        # Ensure the image is in RGB mode for Streamlit compatibility
                        image_with_boxes = image_with_boxes.convert("RGB")
                        
                        # Display the image with bounding boxes
                        st.subheader("Image with Bounding Boxes")
                        st.image(image_with_boxes, caption="Image with Bounding Boxes", use_column_width=True)
                    else:
                        st.write("❌ No bounding boxes found in the OCR result.")
                else:
                    st.write("❌ Failed to retrieve bounding boxes.")
            else:
                st.write("❌ Please enter a valid prompt.")

if __name__ == "__main__":
    main()
