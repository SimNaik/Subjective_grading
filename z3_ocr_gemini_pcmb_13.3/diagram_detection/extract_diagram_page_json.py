import os
import json
import re
from pathlib import Path

def extract_page_specific_json():
    # Define paths
    images_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/labelimg/Images"
    json_source_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr_gemini_pcmb/trial/Physics/output"
    output_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/json"
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all JPEG files from images folder
    image_files = [f for f in os.listdir(images_folder) if f.endswith(('.jpeg', '.jpg'))]
    
    print(f"Found {len(image_files)} image files to process")
    
    for image_file in image_files:
        print(f"\nProcessing: {image_file}")
        
        # Extract ID and page number from filename
        # Pattern: 01_10021165141080491171694788750_DIM_1536_PAGE_1.jpeg
        match = re.match(r'(.+)_DIM_\d+_PAGE_(\d+)\.jpe?g', image_file)
        
        if not match:
            print(f"  ❌ Could not parse filename: {image_file}")
            continue
        
        file_id = match.group(1)
        page_number = int(match.group(2))
        
        print(f"  📄 ID: {file_id}")
        print(f"  📖 Page: {page_number}")
        
        # Look for corresponding folder in json_source_folder
        id_folder_path = os.path.join(json_source_folder, file_id)
        
        if not os.path.exists(id_folder_path):
            print(f"  ❌ Folder not found: {id_folder_path}")
            continue
        
        # Path to the JSON file
        json_file_path = os.path.join(id_folder_path, "json", "output_with_questions.json")
        
        if not os.path.exists(json_file_path):
            print(f"  ❌ JSON file not found: {json_file_path}")
            continue
        
        try:
            # Read the JSON file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            print(f"  📊 Loaded {len(json_data)} items from JSON")
            
            # Filter items where diagrams list contains a diagram with matching page_number
            filtered_data = []
            for item in json_data:
                if 'diagrams' in item and item['diagrams']:  # Check if diagrams exist and not empty
                    for diagram in item['diagrams']:
                        if 'page_number' in diagram and diagram['page_number'] == page_number:
                            filtered_data.append(item)
                            break  # Found a matching diagram, no need to check other diagrams in this item
            
            print(f"  ✅ Found {len(filtered_data)} items with diagrams on page {page_number}")
            
            if filtered_data:
                # Create output filename (same as image but with .json extension)
                output_filename = re.sub(r'\.jpe?g$', '.json', image_file)
                output_path = os.path.join(output_folder, output_filename)
                
                # Save filtered data
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(filtered_data, f, indent=2, ensure_ascii=False)
                
                print(f"  💾 Saved to: {output_path}")
            else:
                print(f"  ⚠️  No diagrams found for page {page_number}")
                
        except json.JSONDecodeError as e:
            print(f"  ❌ Error parsing JSON: {e}")
        except Exception as e:
            print(f"  ❌ Error processing file: {e}")
    
    print(f"\n🎉 Processing complete! Check the output folder: {output_folder}")

def list_available_images():
    """Helper function to see what images are available for processing"""
    images_folder = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/diagram_detection/labelimg/Images"
    
    if not os.path.exists(images_folder):
        print(f"❌ Images folder not found: {images_folder}")
        return
    
    image_files = [f for f in os.listdir(images_folder) if f.endswith(('.jpeg', '.jpg'))]
    
    print(f"📁 Found {len(image_files)} JPEG files:")
    for img in sorted(image_files):
        # Extract info from filename
        match = re.match(r'(.+)_DIM_\d+_PAGE_(\d+)\.jpe?g', img)
        if match:
            file_id = match.group(1)
            page_number = match.group(2)
            print(f"  📄 {img} → ID: {file_id}, Page: {page_number}")
        else:
            print(f"  ❓ {img} → Could not parse")

# Run the main function
if __name__ == "__main__":
    # Uncomment the line below to see available images first
    # list_available_images()
    
    # Run the extraction process
    extract_page_specific_json()

