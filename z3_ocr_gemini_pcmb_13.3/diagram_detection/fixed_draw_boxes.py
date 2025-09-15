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

    # Define a translucent highlight color (e.g., yellow with ~45% opacity)
    highlight_color = (190, 195, 0, 114)  # RGBA: Red, Green, Blue, Alpha (opacity: 0-255)
    
    for box in coords:
        # FIXED: Coordinates are in format [ymin, xmin, ymax, xmax] and already pixels
        if len(box) == 4:
            ymin, xmin, ymax, xmax = box  # No division needed - already pixels!
            
            # Ensure coordinates are within image bounds
            left = max(0, min(int(xmin), image.width))
            top = max(0, min(int(ymin), image.height))
            right = max(0, min(int(xmax), image.width))
            bottom = max(0, min(int(ymax), image.height))
            
            print(f"    🎯 Drawing box: [{left}, {top}, {right}, {bottom}]")

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
    output_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/images_ai_fixed"
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all JSON files
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    
    print(f"Found {len(json_files)} JSON files to process")
    
    for json_file in json_files:
        print(f"\n🔄 Processing: {json_file}")
        
        # Extract page number from JSON filename
        page_match = re.search(r'PAGE_(\d+)', json_file)
        if not page_match:
            print(f"  ❌ Could not extract page number from: {json_file}")
            continue
        
        target_page = int(page_match.group(1))
        print(f"  📖 Target page: {target_page}")
        
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
            
            # Extract bounding box coordinates ONLY for diagrams matching target page
            all_coords = []
            diagram_count = 0
            skipped_count = 0
            
            for item in json_data:
                if 'diagrams' in item and item['diagrams']:
                    for diagram in item['diagrams']:
                        if 'box_2d' in diagram:
                            # Check if this diagram belongs to the target page
                            diagram_page = diagram.get('page_number')
                            if diagram_page == target_page:
                                coords = diagram['box_2d']
                                if len(coords) == 4:
                                    all_coords.append(coords)
                                    diagram_count += 1
                                    print(f"    ✅ Added diagram from page {diagram_page}: {coords}")
                            else:
                                skipped_count += 1
                                print(f"    ⏭️  Skipped diagram from page {diagram_page} (target: {target_page})")
            
            print(f"  🎯 Diagrams added: {diagram_count}")
            print(f"  ⏭️  Diagrams skipped: {skipped_count}")
            
            if all_coords:
                # Load the image directly (no resizing needed)
                original_image = load_image(image_path)
                
                print(f"  🖼️  Image size: {original_image.size}")
                
                # Draw bounding boxes only for matching page diagrams
                image_with_boxes = draw_bounding_boxes(original_image, all_coords)
                
                # Convert back to RGB for saving
                image_with_boxes = image_with_boxes.convert("RGB")
                
                # Save the image with bounding boxes
                output_filename = image_filename  # Keep the same name
                output_path = os.path.join(output_folder, output_filename)
                
                image_with_boxes.save(output_path)
                print(f"  💾 Saved image with {len(all_coords)} bounding boxes: {output_path}")
                
            else:
                print(f"  ⚠️  No diagrams found for page {target_page}")
                
        except json.JSONDecodeError as e:
            print(f"  ❌ Error parsing JSON: {e}")
        except Exception as e:
            print(f"  ❌ Error processing: {e}")
    
    print(f"\n🎉 Processing complete! Check output folder: {output_folder}")

def process_manual_labeled_coords():
    """Process manually labeled coordinates from 2d folder"""
    # Define paths
    json_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/labelimg/2d"
    images_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/labelimg/Images"
    output_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/images_manual_labeled"
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all JSON files
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    
    print(f"Found {len(json_files)} manual labeled JSON files to process")
    
    for json_file in json_files:
        print(f"\n🔄 Processing: {json_file}")
        
        # Derive corresponding image filename
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
            
            print(f"  📊 Processing {json_data.get('total_objects', 0)} objects")
            
            # Extract bounding box coordinates
            all_coords = []
            
            for obj in json_data.get('objects', []):
                if 'box_2d' in obj:
                    coords = obj['box_2d']
                    if len(coords) == 4:
                        all_coords.append(coords)
                        print(f"    ✅ Added manual box: {coords}")
            
            if all_coords:
                # Load the image directly
                original_image = load_image(image_path)
                
                print(f"  🖼️  Image size: {original_image.size}")
                
                # Draw bounding boxes
                image_with_boxes = draw_bounding_boxes(original_image, all_coords)
                
                # Convert back to RGB for saving
                image_with_boxes = image_with_boxes.convert("RGB")
                
                # Save the image with bounding boxes
                output_filename = f"manual_{image_filename}"
                output_path = os.path.join(output_folder, output_filename)
                
                image_with_boxes.save(output_path)
                print(f"  💾 Saved image with {len(all_coords)} bounding boxes: {output_path}")
                
            else:
                print(f"  ⚠️  No objects found")
                
        except json.JSONDecodeError as e:
            print(f"  ❌ Error parsing JSON: {e}")
        except Exception as e:
            print(f"  ❌ Error processing: {e}")
    
    print(f"\n🎉 Manual labeling processing complete! Check output folder: {output_folder}")

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
            page_breakdown = {}
            
            for item in json_data:
                if 'diagrams' in item and item['diagrams']:
                    for diagram in item['diagrams']:
                        if 'box_2d' in diagram:
                            page_num = diagram.get('page_number', 'unknown')
                            page_breakdown[page_num] = page_breakdown.get(page_num, 0) + 1
                            diagram_count += 1
            
            if diagram_count > 0:
                breakdown_str = ", ".join([f"page {k}: {v}" for k, v in sorted(page_breakdown.items())])
                print(f"  📊 {json_file} → {diagram_count} diagrams ({breakdown_str})")
            else:
                print(f"  📄 {json_file} → No diagrams")
                
        except Exception as e:
            print(f"  ❌ {json_file} → Error: {e}")

# Run the main function
if __name__ == "__main__":
    print("🔍 ANALYSIS: Checking available JSON files...")
    list_json_files_with_diagrams()
    
    print("\n" + "="*60)
    print("🚀 PROCESSING AI-DETECTED COORDINATES...")
    process_json_and_draw_boxes()
    
    print("\n" + "="*60)  
    print("🚀 PROCESSING MANUAL-LABELED COORDINATES...")
    process_manual_labeled_coords()
