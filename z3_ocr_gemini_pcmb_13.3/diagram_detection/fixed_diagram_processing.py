import os
import json
import numpy as np
from PIL import Image, ImageDraw
import cv2
import re

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

def process_json_and_draw_boxes():
    # Define paths
    json_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/json"
    images_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/labelimg/Images"
    output_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/images_gemini"
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all JSON files
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    
    print(f"Found {len(json_files)} JSON files to process")
    
    for json_file in json_files:
        print(f"\nProcessing: {json_file}")
        
        # Derive corresponding image filename
        # Replace .json with .jpeg
        image_filename = json_file.replace('.json', '.jpeg')
        
        # Full paths
        json_path = os.path.join(json_folder, json_file)
        image_path = os.path.join(images_folder, image_filename)
        
        # Check if corresponding image exists
        if not os.path.exists(image_path):
            print(f"  ❌ Image not found: {image_path}")
            continue
        
        try:
            # Read JSON file
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            print(f"  📊 Loaded JSON with {len(json_data)} items")
            
            # Extract all bounding box coordinates from diagrams
            all_coords = []
            diagram_count = 0
            
            for item in json_data:
                if 'diagrams' in item and item['diagrams']:
                    for diagram in item['diagrams']:
                        if 'box_2d' in diagram:
                            coords = diagram['box_2d']
                            if len(coords) == 4:
                                all_coords.append(coords)
                                diagram_count += 1
                                print(f"    📦 Found diagram: {coords}")
            
            print(f"  🎯 Total diagrams found: {diagram_count}")
            
            if all_coords:
                # Load the image directly (no resizing needed)
                original_image = load_image(image_path)
                
                print(f"  🖼️  Image size: {original_image.size}")
                
                # Draw bounding boxes directly on the 1536 image
                image_with_boxes = draw_bounding_boxes(original_image, all_coords)
                
                # Convert back to RGB for saving
                image_with_boxes = image_with_boxes.convert("RGB")
                
                # Save the image with bounding boxes
                output_filename = image_filename  # Keep the same name
                output_path = os.path.join(output_folder, output_filename)
                
                image_with_boxes.save(output_path)
                print(f"  💾 Saved image with bounding boxes: {output_path}")
                
            else:
                print(f"  ⚠️  No diagrams with bounding boxes found")
                
        except json.JSONDecodeError as e:
            print(f"  ❌ Error parsing JSON: {e}")
        except Exception as e:
            print(f"  ❌ Error processing: {e}")
    
    print(f"\n🎉 Processing complete! Check output folder: {output_folder}")

def list_json_files_with_diagrams():
    """Helper function to see what JSON files have diagrams"""
    json_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/json"
    
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    
    print(f"📁 Analyzing {len(json_files)} JSON files:")
    
    for json_file in sorted(json_files):
        json_path = os.path.join(json_folder, json_file)
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            diagram_count = 0
            for item in json_data:
                if 'diagrams' in item and item['diagrams']:
                    diagram_count += len([d for d in item['diagrams'] if 'box_2d' in d])
            
            if diagram_count > 0:
                print(f"  📊 {json_file} → {diagram_count} diagrams")
            else:
                print(f"  📄 {json_file} → No diagrams")
                
        except Exception as e:
            print(f"  ❌ {json_file} → Error: {e}")

# Run the main function
if __name__ == "__main__":
    # Uncomment to see which files have diagrams first
    # list_json_files_with_diagrams()
    
    # Process all JSON files and create images with bounding boxes
    process_json_and_draw_boxes()
