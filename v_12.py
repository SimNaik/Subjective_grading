#this is the highlight the words/sentences on the page from gemini to highlight the word sent and look at the image 

import os
from PIL import Image, ImageDraw, ImageEnhance
import matplotlib.pyplot as plt
import numpy as np

def draw_bounding_boxes(image_path, coords):
    # Open image using PIL and ensure it's in RGBA mode for transparency
    image = Image.open(image_path).convert("RGBA")
    
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

    # Show image with bounding boxes using matplotlib
    plt.figure(figsize=(10, 10))
    plt.imshow(np.asarray(image))
    plt.axis('off')  # Hide axis
    plt.show()

# Example input
image_path = '/mnt/shared-storage/yolov11L_Image_training_set_400/Solution_Grading/check_4_i2/DIM_768_IMAGE_1.jpeg'  # Replace with your image path
coords = [
    [128, 216, 192, 946],  # Bounding box coordinates [ymin, xmin, ymax, xmax]
]

draw_bounding_boxes(image_path, coords)

#to send pythin code
import os
from PIL import Image, ImageDraw, ImageEnhance
import matplotlib.pyplot as plt
import numpy as np

def draw_bounding_boxes(image_path, coords):
    # Open image using PIL and ensure it's in RGBA mode for transparency
    image = Image.open(image_path).convert("RGBA")
    
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

    # Show image with bounding boxes using matplotlib
    plt.figure(figsize=(10, 10))
    plt.imshow(np.asarray(image))
    plt.axis('off')  # Hide axis
    plt.show()

def load_coords_from_json(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    coords = []
    for entry in data:
        bbox = entry['bbox']  # Access the bbox coordinates
        ymin, xmin, ymax, xmax = bbox  # Unpack the bounding box coordinates
        coords.append([ymin, xmin, ymax, xmax])  # Add the coordinates to the list
    return coords

# Update with your actual file paths
image_path = '/mnt/shared-storage/yolov11L_Image_training_set_400/Solution_Grading/check_4_i3/DIM_768_IMAGE_1.jpeg'  # Replace with your image path
json_file_path = '/mnt/shared-storage/yolov11L_Image_training_set_400/Solution_Grading/check_4_i3/768_output.json'  # Replace with your JSON file path

# Load bounding box coordinates from JSON
coords = load_coords_from_json(json_file_path)

# Draw bounding boxes on the image
draw_bounding_boxes(image_path, coords)

