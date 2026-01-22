#!/usr/bin/env python3
"""
Faculty-Guided Step Processor v2
Compares faculty and student images for the same question and returns step-wise bounding boxes
"""

import os
import json
import base64
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import google.generativeai as genai

# === Load API Key ===
load_dotenv()
model_name = "gemini-2.5-pro"
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
model = genai.GenerativeModel(model_name)

# === Configuration ===
DIM = 768
BASE_OUTPUT_FOLDER = "/Users/simrannaik/Desktop/subjective_grading/data/stepwise_image"

# === Image Paths ===
STUDENT_IMAGE_PATH = "/Users/simrannaik/Desktop/subjective_grading/data/iteration_2/cache/20009505879381101687674437.pdf/20009505879381101687674437_DIM_1536_PAGE_1.jpeg"
FACULTY_IMAGE_PATH = "/Users/simrannaik/Desktop/subjective_grading/data/iteration_2/cache/Sample Subjective Answers-Chemistry.pdf/ocr_files/Sample Subjective Answers-Chemistry_DIM_1536_PAGE_2.jpeg"

# === Question Configuration ===
STUDENT_QUESTION_NUMBER = "Q3"  # Which question to analyze in student image
FACULTY_QUESTION_NUMBER = "3063676.0"  # Which question to use as reference in faculty image

# === Extract Student PDF Name from Path ===
import re
pdf_name_match = re.search(r'/([^/]+)\.pdf/', STUDENT_IMAGE_PATH)
if pdf_name_match:
    STUDENT_PDF_NAME = pdf_name_match.group(1)
else:
    # Fallback: extract from filename
    STUDENT_PDF_NAME = os.path.basename(STUDENT_IMAGE_PATH).split('_')[0]

OUTPUT_FOLDER = f"{BASE_OUTPUT_FOLDER}/{STUDENT_PDF_NAME}"

# === Assessment Results Path ===
ASSESSMENT_RESULTS_PATH = "/Users/simrannaik/Desktop/subjective_grading/temp/assessment_results/assessment_results_assessment_v22_simran.json"

# === Dynamic Prompt Template ===
def create_prompt(student_q_num, faculty_q_num):
    return f"""### Faculty-Guided Student Answer Analysis

**Task**: Compare student and faculty solutions for the same question and find bounding boxes for each solution step.

**Instructions:**
1. **Faculty Image**: Look at question {faculty_q_num} in the first image (faculty solution)
2. **Student Image**: Look at question {student_q_num} in the second image (student's handwritten work)
3. **Analysis**: Break down the faculty solution into logical steps/parts based on the marking scheme
4. **Mapping**: For each faculty step, find the corresponding content in the student's answer
5. **Coordinates**: Return bounding box coordinates in format [ymin, xmin, ymax, xmax] 
6. **Flexibility**: The student may use different wording but express the same concepts or the student might have written the wrong answer but the context of the step is the same
7. **Missing Steps**: If a step is not found in student's work, return null for that step's coordinates

**Output Format:**
```json
{{
  "step_1_coordinates": [ymin, xmin, ymax, xmax],
  "step_2_coordinates": [ymin, xmin, ymax, xmax],
  "step_3_coordinates": [ymin, xmin, ymax, xmax],
  "step_4_coordinates": [ymin, xmin, ymax, xmax]
}}
```

**Note:** 
- The faculty image already contains step-wise marks and solution breakdown
- Use the existing faculty step structure as your reference guide
- Focus on identifying where each faculty step appears in the student's solution
- Look for conceptual matches, not exact text matching
- Map each pre-marked faculty step to corresponding areas in student's work"""

# === Image Processing Functions ===
def load_image(image_path):
    """Load image from file path"""
    return Image.open(image_path)

def load_assessment_marks(pdf_name, question_no):
    """Load marks for each step from assessment results JSON"""
    try:
        with open(ASSESSMENT_RESULTS_PATH, 'r') as f:
            assessment_data = json.load(f)
        
        # Find matching assessment
        for item in assessment_data:
            metadata = item.get('metadata', {})
            if (metadata.get('pdf_name') == pdf_name and 
                metadata.get('question_no') == float(question_no)):
                
                # Extract marks for each step
                solution = item.get('feedback', {}).get('solution', [])
                step_marks = {}
                
                for step_data in solution:
                    # Each step_data contains step_X, marks_awarded, and total_marks keys
                    marks_awarded = step_data.get('marks_awarded', 0.0)
                    total_marks = step_data.get('total_marks', marks_awarded)  # Fallback to marks_awarded if total_marks not present
                    
                    # Find the step_X key in this object
                    for key, value in step_data.items():
                        if key.startswith('step_'):
                            step_num = key  # e.g., 'step_1'
                            # Convert to coordinates format for consistency
                            step_coords_key = f"{step_num}_coordinates"
                            # Store both awarded and total marks
                            step_marks[step_coords_key] = {
                                'awarded': marks_awarded,
                                'total': total_marks
                            }
                            print(f"   📊 Found {step_num} -> {step_coords_key}: {marks_awarded}/{total_marks} marks")
                            break  # Only one step_X per object
                
                return step_marks
        
        print(f"❌ No assessment found for {pdf_name}, Q{question_no} (looking for question_no: {float(question_no)})")
        return {}
        
    except Exception as e:
        print(f"❌ Error loading assessment marks: {e}")
        return {}

def resize_image(image, target_size=DIM):
    """Resize image maintaining aspect ratio"""
    original_size = image.size
    
    # Calculate new dimensions
    if image.width > image.height:
        new_width = target_size
        new_height = int((target_size * image.height) / image.width)
    else:
        new_height = target_size
        new_width = int((target_size * image.width) / image.height)
    
    new_size = (new_width, new_height)
    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    return original_size, new_size, resized_image

def send_to_gemini(faculty_image, student_image, prompt):
    """Send both images to Gemini with prompt (EXACT SAME LOGIC as Streamlit)"""
    try:
        # Send request to Gemini with user prompt and images (SAME AS STREAMLIT)
        response = model.generate_content([prompt] + [faculty_image, student_image])  # Batch processing
        raw_response = response.text.strip()

        # Print raw response for debugging (SAME AS STREAMLIT)
        print(f"Raw response from Gemini:\n{raw_response}")

        # Clean the raw response by removing any non-JSON content (SAME AS STREAMLIT)
        cleaned = raw_response.strip()
        cleaned = cleaned.strip('```json').strip('```').strip()  # Clean up surrounding backticks if present
        
        # Extract JSON from the response (look for arrays [...] or objects {...}) (SAME AS STREAMLIT)
        import re
        
        # Try to find JSON object first (for faculty-guided format) (SAME AS STREAMLIT)
        json_obj_match = re.search(r'\{.*?\}', cleaned, re.DOTALL)
        if json_obj_match:
            cleaned = json_obj_match.group(0)
        # Then try JSON array (for original format) (SAME AS STREAMLIT)
        elif re.search(r'\[\[.*?\]\]', cleaned, re.DOTALL):
            json_array_match = re.search(r'\[\[.*?\]\]', cleaned, re.DOTALL)
            cleaned = json_array_match.group(0)
        elif cleaned.startswith("[") and cleaned.endswith("]"):
            # Already clean JSON array (SAME AS STREAMLIT)
            pass
        elif cleaned.startswith("{") and cleaned.endswith("}"):
            # Already clean JSON object (SAME AS STREAMLIT)
            pass
        else:
            # Try to find any JSON-like structure (SAME AS STREAMLIT)
            lines = cleaned.split('\n')
            for line in lines:
                line = line.strip()
                if (line.startswith("[") and line.endswith("]")) or (line.startswith("{") and line.endswith("}")):
                    cleaned = line
                    break

        # Check if cleaned response is valid JSON (array or object) (SAME AS STREAMLIT)
        if (cleaned.startswith("[") and cleaned.endswith("]")) or (cleaned.startswith("{") and cleaned.endswith("}")):
            try:
                # Attempt to parse the cleaned response as JSON (SAME AS STREAMLIT)
                parsed = json.loads(cleaned)

                # Check the structure of the parsed result (just print it) (SAME AS STREAMLIT)
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

# === Draw Bounding Boxes with Marks (Enhanced from Streamlit) ===
def draw_bounding_boxes_with_marks(image, step_coords, step_marks):
    """Draw translucent yellow bounding boxes with marks boxes on the right"""
    # Open image using PIL and ensure it's in RGBA mode for transparency
    image = image.convert("RGBA")
    
    # Create drawing context
    draw = ImageDraw.Draw(image)

    # Define colors
    highlight_color = (190, 195, 0, 64)  # Yellow highlight (same as Streamlit)
    marks_box_color = (255, 255, 255, 200)  # White marks box
    marks_border_color = (0, 0, 0, 255)  # Black border
    text_color = (0, 0, 0, 255)  # Black text
    
    # Try to load a font (fallback to default if not available)
    try:
        font = ImageFont.truetype("Arial.ttf", 16)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        except:
            font = ImageFont.load_default()
    
    print(f"📦 Drawing {len(step_coords)} bounding boxes with marks...")
    
    for step_name, coords in step_coords.items():
        if coords is None:
            continue
            
        ymin, xmin, ymax, xmax = [coord / 1000 for coord in coords]  # Normalize (same as Streamlit)

        # Calculate absolute pixel coordinates
        left = xmin * image.width
        top = ymin * image.height
        right = xmax * image.width
        bottom = ymax * image.height

        print(f"   📦 {step_name}: ({left:.1f}, {top:.1f}) to ({right:.1f}, {bottom:.1f})")

        # Draw the main bounding box
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([left, top, right, bottom], fill=highlight_color)
        image = Image.alpha_composite(image, overlay)

        # Draw marks box on the right side
        marks_data = step_marks.get(step_name, {'awarded': 0.0, 'total': 0.0})
        if isinstance(marks_data, dict):
            awarded = marks_data.get('awarded', 0.0)
            total = marks_data.get('total', 0.0)
            
            # Add + or - sign based on performance, except for 0
            if awarded == 0.0:
                marks_text = "0"
                box_color = (255, 182, 193, 200)  # Light pink for zero marks
            elif awarded >= total:
                marks_text = f"+ {awarded}"
                box_color = (144, 238, 144, 200)  # Light green for full marks
            else:
                marks_text = f"- {awarded}"
                box_color = (255, 182, 193, 200)  # Light pink for partial marks
        else:
            # Backward compatibility for old format
            marks_text = f"{marks_data}"
            box_color = marks_box_color  # Default white
        
        # Calculate marks box position (to the right of the bounding box)
        marks_box_size = 40
        marks_box_left = right + 10  # 10px gap from bounding box
        marks_box_top = top
        marks_box_right = marks_box_left + marks_box_size
        marks_box_bottom = marks_box_top + marks_box_size
        
        # Ensure marks box doesn't go outside image
        if marks_box_right > image.width:
            marks_box_left = left - marks_box_size - 10  # Put on left side instead
            marks_box_right = marks_box_left + marks_box_size
        
        # Draw marks box
        marks_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        marks_draw = ImageDraw.Draw(marks_overlay)
        
        # Colored background box (green for +, pink for -, white for default)
        final_box_color = box_color if 'box_color' in locals() else marks_box_color
        marks_draw.rectangle([marks_box_left, marks_box_top, marks_box_right, marks_box_bottom], 
                           fill=final_box_color, outline=marks_border_color, width=2)
        
        # Add marks text
        text_bbox = marks_draw.textbbox((0, 0), marks_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = marks_box_left + (marks_box_size - text_width) // 2
        text_y = marks_box_top + (marks_box_size - text_height) // 2
        
        marks_draw.text((text_x, text_y), marks_text, fill=text_color, font=font)
        
        # Composite marks box
        image = Image.alpha_composite(image, marks_overlay)
        
        print(f"   📊 Added marks box: {marks_text}")

    return image

# === Backward compatibility function ===
def draw_bounding_boxes(image, coords):
    """Backward compatibility - convert coords list to step_coords dict"""
    step_coords = {}
    for i, coord in enumerate(coords):
        step_coords[f"step_{i+1}_coordinates"] = coord
    return draw_bounding_boxes_with_marks(image, step_coords, {})

# === Main Processing Function ===
def process_faculty_guided_steps():
    """Main function to process student image with faculty guidance"""
    
    print("🎯 Faculty-Guided Step Processor v2")
    print("=" * 50)
    
    # Create output folder
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"📁 Output folder: {OUTPUT_FOLDER}")
    
    # Load and resize images
    print(f"📷 Loading faculty image: {os.path.basename(FACULTY_IMAGE_PATH)}")
    faculty_image = load_image(FACULTY_IMAGE_PATH)
    print(f"📐 Faculty size: {faculty_image.size[0]}x{faculty_image.size[1]}")
    
    print(f"📷 Loading student image: {os.path.basename(STUDENT_IMAGE_PATH)}")
    student_image = load_image(STUDENT_IMAGE_PATH)
    print(f"📐 Student size: {student_image.size[0]}x{student_image.size[1]}")
    
    # Resize images
    _, _, resized_faculty = resize_image(faculty_image)
    _, _, resized_student = resize_image(student_image)
    print(f"📐 Resized faculty to: {resized_faculty.size[0]}x{resized_faculty.size[1]}")
    print(f"📐 Resized student to: {resized_student.size[0]}x{resized_student.size[1]}")
    
    # Create prompt
    prompt = create_prompt(STUDENT_QUESTION_NUMBER, FACULTY_QUESTION_NUMBER)
    print(f"📝 Analyzing {FACULTY_QUESTION_NUMBER} (faculty) vs {STUDENT_QUESTION_NUMBER} (student)")
    
    # Send to Gemini
    coordinates_data = send_to_gemini(resized_faculty, resized_student, prompt)
    
    if not coordinates_data:
        print("❌ Failed to get coordinates from Gemini")
        return
    
    # Parse coordinates (SAME LOGIC as Streamlit)
    step_coords = {}
    
    for key, value in coordinates_data.items():
        if key.endswith('_coordinates'):
            if isinstance(value, list) and len(value) == 4:
                coords = value
                # Store coordinates as-is (let draw_bounding_boxes handle normalization like Streamlit)
                step_coords[key] = coords
                print(f"   📊 {key}: {coords}")
            elif isinstance(value, dict) and len(value) == 4:
                # Handle indexed format
                coord_array = [value.get(i, 0) for i in range(4)]
                # Store coordinates as-is (let draw_bounding_boxes handle normalization like Streamlit)
                step_coords[key] = coord_array
                print(f"   📊 {key}: {coord_array}")
            else:
                step_coords[key] = None
    
    print(f"📊 Found coordinates for {len([v for v in step_coords.values() if v is not None])} steps")
    
    # Load assessment marks for this PDF and question
    print(f"📋 Loading assessment marks for {STUDENT_PDF_NAME}, Q{STUDENT_QUESTION_NUMBER.replace('Q', '')}")
    step_marks = load_assessment_marks(f"{STUDENT_PDF_NAME}.pdf", STUDENT_QUESTION_NUMBER.replace('Q', ''))
    
    # Save individual step images with marks
    for step_name, coordinates in step_coords.items():
        if coordinates is not None:
            # Create single step dict for this step
            single_step = {step_name: coordinates}
            single_marks = {step_name: step_marks.get(step_name, {'awarded': 0.0, 'total': 0.0})}
            
            # Create image with just this step and its marks
            step_image = draw_bounding_boxes_with_marks(resized_student.copy(), single_step, single_marks)
            
            # Convert to RGB and save
            final_step_image = step_image.convert("RGB")
            step_filename = f"{OUTPUT_FOLDER}/{step_name}_bbox_with_marks.png"
            final_step_image.save(step_filename)
            print(f"💾 Saved {step_name}: {step_filename}")
    
    # Create combined image with all steps and marks
    combined_image = draw_bounding_boxes_with_marks(resized_student.copy(), step_coords, step_marks)
    final_combined_image = combined_image.convert("RGB")
    combined_filename = f"{OUTPUT_FOLDER}/all_steps_combined_with_marks.png"
    try:
        final_combined_image.save(combined_filename)
        print(f"💾 Saved combined image with marks: {combined_filename}")
        print(f"📁 File exists after save: {os.path.exists(combined_filename)}")
    except Exception as e:
        print(f"❌ Error saving combined image: {e}")
    
    # Save original resized images for reference
    faculty_filename = f"{OUTPUT_FOLDER}/faculty_original.png"
    resized_faculty.save(faculty_filename)
    print(f"💾 Saved faculty original: {faculty_filename}")
    
    student_filename = f"{OUTPUT_FOLDER}/student_original.png"
    resized_student.save(student_filename)
    print(f"💾 Saved student original: {student_filename}")
    
    # Save coordinates JSON
    coords_filename = f"{OUTPUT_FOLDER}/coordinates.json"
    with open(coords_filename, 'w') as f:
        json.dump(step_coords, f, indent=2)
    print(f"💾 Saved coordinates: {coords_filename}")
    
    print(f"\n🎉 Processing complete!")
    print(f"📂 Check the '{OUTPUT_FOLDER}' folder for all generated images")
    print(f"🎨 All steps highlighted with same translucent yellow color")

if __name__ == "__main__":
    print("🚀 Starting Faculty-Guided Step Processing v2...")
    print(f"📝 Prompt: Compare {FACULTY_QUESTION_NUMBER} (faculty) vs {STUDENT_QUESTION_NUMBER} (student)")
    print(f"📷 Faculty image: {os.path.basename(FACULTY_IMAGE_PATH)}")
    print(f"📷 Student image: {os.path.basename(STUDENT_IMAGE_PATH)}")
    print(f"📁 Output folder: {OUTPUT_FOLDER}")
    print()
    
    try:
        process_faculty_guided_steps()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
