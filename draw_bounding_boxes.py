#here the box coords are taken from the data and drawn on the image from gemini
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import numpy as np

def draw_bounding_boxes(image_path, coords):
    # Open image using PIL
    image = Image.open(image_path)
    
    # Create drawing context
    draw = ImageDraw.Draw(image)

    # Normalize coordinates and draw bounding boxes
    colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF']
    
    for index, box in enumerate(coords):
        ymin, xmin, ymax, xmax = [coord / 1000 for coord in box]  # Normalize to 0-1 range
        width = (xmax - xmin) * image.width
        height = (ymax - ymin) * image.height

        # Draw the bounding box with a specific color
        color = colors[index % len(colors)]
        draw.rectangle([xmin * image.width, ymin * image.height, 
                        xmin * image.width + width, ymin * image.height + height], 
                       outline=color, width=5)

    # Show image with bounding boxes using matplotlib
    plt.figure(figsize=(10, 10))
    plt.imshow(np.asarray(image))
    plt.axis('off')  # Hide axis
    plt.show()

# Example input
image_path = '/mnt/shared-storage/yolov11L_Image_training_set_400/Solution_Grading/data/768/B01_1002115268961841141690701450_page_1.jpeg'  # Replace with your image path
coords = [
    [126,218,185,946],
    [471, 142, 508, 699],
    [419, 142, 483, 967],
    [110, 83, 189, 946],
    [495, 142, 560, 959],  # Example bounding box coordinates
]

draw_bounding_boxes(image_path, coords)
