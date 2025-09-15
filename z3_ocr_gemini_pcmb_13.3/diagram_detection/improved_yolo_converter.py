import os
import json
from pathlib import Path
from PIL import Image

def get_image_dimensions(image_path):
    """Get the dimensions (width, height) of an image."""
    try:
        with Image.open(image_path) as img:
            return img.size  # returns (width, height)
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
        return None

def yolo_to_box_2d(yolo_line, image_width, image_height):
    """
    Convert YOLO format to box_2d format
    
    Args:
        yolo_line: string like "0 0.383978 0.526367 0.718232 0.453776"
        image_width: width of the image in pixels (dynamically retrieved)
        image_height: height of the image in pixels (dynamically retrieved)
    
    Returns:
        dict with class_id and box_2d coordinates
    """
    # Parse YOLO coordinates
    parts = yolo_line.strip().split()
    if len(parts) != 5:
        return None
    
    class_id = int(parts[0])
    center_x = float(parts[1])
    center_y = float(parts[2])
    width = float(parts[3])
    height = float(parts[4])
    
    # Convert to pixel coordinates
    x_min = int((center_x - width/2) * image_width)
    y_min = int((center_y - height/2) * image_height)
    x_max = int((center_x + width/2) * image_width)
    y_max = int((center_y + height/2) * image_height)
    
    return {
        "class_id": class_id,
        "box_2d": [x_min, y_min, x_max, y_max],
        "yolo_original": yolo_line.strip()
    }

def convert_yolo_txt_to_2d_json():
    # Define paths
    base_labelimg_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/labelimg"
    txt_folder = os.path.join(base_labelimg_folder, "txt")
    image_folder = os.path.join(base_labelimg_folder, "Images")  # Fixed: Capital "I" for Images
    output_folder = os.path.join(base_labelimg_folder, "2d")
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    print(f"📁 Created/using output folder: {output_folder}")
    
    # Check if required folders exist
    if not os.path.exists(txt_folder):
        print(f"❌ TXT folder not found: {txt_folder}")
        return
    
    if not os.path.exists(image_folder):
        print(f"❌ Images folder not found: {image_folder}")
        return
    
    # Get all .txt files
    txt_files = [f for f in os.listdir(txt_folder) if f.endswith('.txt')]
    
    if not txt_files:
        print(f"⚠️  No .txt files found in: {txt_folder}")
        return
    
    print(f"🔍 Found {len(txt_files)} .txt files to process")
    print(f"📂 Images folder: {image_folder}")
    print(f"📂 TXT folder: {txt_folder}")
    
    for txt_file in txt_files:
        print(f"\n🔄 Processing: {txt_file}")
        
        # Full path to txt file
        txt_path = os.path.join(txt_folder, txt_file)
        
        # Create corresponding JSON filename
        json_filename = txt_file.replace('.txt', '.json')
        json_path = os.path.join(output_folder, json_filename)
        
        # Construct corresponding image path based on txt file name
        # Remove .txt extension and add .jpeg
        image_filename = txt_file.replace('.txt', '.jpeg')
        image_path = os.path.join(image_folder, image_filename)
        
        print(f"  🔍 Looking for image: {image_filename}")
        
        # Check if corresponding image exists
        if not os.path.exists(image_path):
            print(f"  ❌ Image not found: {image_path}")
            print(f"     Skipping {txt_file}")
            continue
        
        # Get image dimensions dynamically
        image_dimensions = get_image_dimensions(image_path)
        if not image_dimensions:
            print(f"  ❌ Could not retrieve image dimensions for {image_path}")
            continue
        
        image_width, image_height = image_dimensions
        print(f"  📐 Image dimensions: {image_width}x{image_height}")
        
        try:
            # Read the txt file
            with open(txt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"  📄 Read {len(lines)} lines from TXT file")
            
            # Convert each line (each object) to 2D format
            converted_objects = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                
                converted = yolo_to_box_2d(line, image_width, image_height)
                if converted:
                    converted["object_id"] = line_num
                    converted_objects.append(converted)
                    print(f"    ✅ Line {line_num}: {line} → {converted['box_2d']}")
                else:
                    print(f"    ❌ Line {line_num}: Could not parse: {line}")
            
            if converted_objects:
                # Create JSON structure
                json_data = {
                    "filename": txt_file,
                    "image_filename": image_filename,
                    "image_path": image_path,
                    "image_dimensions": {
                        "width": image_width,
                        "height": image_height
                    },
                    "total_objects": len(converted_objects),
                    "objects": converted_objects
                }
                
                # Save to JSON file
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                
                print(f"  💾 Saved {len(converted_objects)} objects to: {json_filename}")
            else:
                print(f"  ⚠️  No valid objects found in: {txt_file}")
                
        except Exception as e:
            print(f"  ❌ Error processing {txt_file}: {e}")
    
    print(f"\n🎉 Conversion complete! Check output folder: {output_folder}")

def preview_txt_and_image_pairs():
    """Helper function to preview which txt files have corresponding images"""
    base_labelimg_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/labelimg"
    txt_folder = os.path.join(base_labelimg_folder, "txt")
    image_folder = os.path.join(base_labelimg_folder, "Images")
    
    if not os.path.exists(txt_folder):
        print(f"❌ TXT folder not found: {txt_folder}")
        return
    
    if not os.path.exists(image_folder):
        print(f"❌ Images folder not found: {image_folder}")
        return
    
    txt_files = [f for f in os.listdir(txt_folder) if f.endswith('.txt')]
    image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpeg')]
    
    print(f"📊 Found {len(txt_files)} TXT files and {len(image_files)} image files")
    print("\n🔍 Checking TXT-Image pairs:")
    
    for txt_file in sorted(txt_files):
        image_filename = txt_file.replace('.txt', '.jpeg')
        image_path = os.path.join(image_folder, image_filename)
        
        if os.path.exists(image_path):
            # Get image dimensions
            dimensions = get_image_dimensions(image_path)
            if dimensions:
                w, h = dimensions
                print(f"  ✅ {txt_file} → {image_filename} ({w}x{h})")
            else:
                print(f"  ⚠️  {txt_file} → {image_filename} (could not read dimensions)")
        else:
            print(f"  ❌ {txt_file} → {image_filename} (image not found)")

# Run the conversion
if __name__ == "__main__":
    # Preview txt-image pairs first
    print("🔍 PREVIEW: Checking TXT-Image pairs...")
    preview_txt_and_image_pairs()
    
    print("\n" + "="*60)
    print("🚀 STARTING CONVERSION...")
    
    # Run the conversion process
    convert_yolo_txt_to_2d_json()

