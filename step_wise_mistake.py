#!/usr/bin/env python3
"""
Faculty-Guided Step Processor v2 - Error Detection Mode
Automatically processes ALL questions in a PDF sequentially
"""

import os
import sys
import json
import shutil
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import prompt from prompt_store
from ocr.prompt_store import assessment_v24_error_boxes

# === Load API Key ===
load_dotenv()
model_name = "gemini-3-pro-image-preview"
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
model = genai.GenerativeModel(model_name)

# === Configuration ===
DIM = 1536
BASE_OUTPUT_FOLDER = "/Users/simrannaik/Desktop/subjective_grading/data/stepwise_images/step_wise_mistake"
SOURCE_FOLDER = "/Users/simrannaik/Desktop/subjective_grading/data/stepwise_images/source"

# === MAIN CONFIGURATION - Only set this value ===
PDF_NAME = "1002102834994041171692514014"  # PDF name (without .pdf extension)

# === Derived values ===
STUDENT_PDF_NAME = PDF_NAME

# === Load Data from Source ===
def get_all_questions_from_assessment(pdf_name):
    """Load assessment JSON and extract all unique question numbers"""
    try:
        assessment_path = Path(SOURCE_FOLDER) / f"{pdf_name}.pdf" / f"{pdf_name}_assessment_v22.json"
        
        if not assessment_path.exists():
            print(f"❌ Assessment file not found: {assessment_path}")
            return []
        
        print(f"📂 Loading assessment from: {assessment_path}")
        
        with open(assessment_path, 'r') as f:
            assessment_data = json.load(f)
        
        # Extract all unique question numbers
        question_numbers = []
        for item in assessment_data:
            metadata = item.get('metadata', {})
            question_no = metadata.get('question_no')
            pdf_name_check = metadata.get('pdf_name')
            
            if question_no and pdf_name_check == f"{pdf_name}.pdf":
                if question_no not in question_numbers:
                    question_numbers.append(question_no)
        
        question_numbers.sort()
        print(f"✅ Found {len(question_numbers)} questions: {question_numbers}")
        return question_numbers
        
    except Exception as e:
        print(f"❌ Error loading assessment: {e}")
        import traceback
        traceback.print_exc()
        return []

def load_assessment_for_question(pdf_name, question_no):
    """Load assessment data for specific question from assessment JSON"""
    try:
        question_no_float = float(str(question_no).replace('Q', '').replace('q', ''))
        
        # Path to assessment JSON
        assessment_path = Path(SOURCE_FOLDER) / f"{pdf_name}.pdf" / f"{pdf_name}_assessment_v22.json"
        
        if not assessment_path.exists():
            print(f"❌ Assessment file not found: {assessment_path}")
            return None
        
        with open(assessment_path, 'r') as f:
            assessment_data = json.load(f)
        
        # Find matching question
        for item in assessment_data:
            metadata = item.get('metadata', {})
            if (metadata.get('pdf_name') == f"{pdf_name}.pdf" and 
                metadata.get('question_no') == question_no_float):
                print(f"✅ Found assessment for Question {question_no_float}")
                return item
        
        print(f"❌ No assessment found for Question {question_no_float}")
        return None
        
    except Exception as e:
        print(f"❌ Error loading assessment: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_student_faculty_data(pdf_name, question_no):
    """Load student and faculty solution from student_joined_ocr.json"""
    try:
        question_no_float = float(str(question_no).replace('Q', '').replace('q', ''))
        
        # Path to student_joined_ocr.json
        json_path = Path(SOURCE_FOLDER) / f"{pdf_name}.pdf" / "student_joined_ocr.json"
        
        if not json_path.exists():
            print(f"❌ File not found: {json_path}")
            return None, None
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Search by qn_pdf_name
        qn_pdf_name = f"{pdf_name}.pdf_{int(question_no_float)}"
        
        for item in data:
            if item.get('qn_pdf_name') == qn_pdf_name:
                faculty_solution = item.get('faculty_solution')
                student_solution = item.get('student_solution')
                
                # Parse string representations
                if isinstance(faculty_solution, str):
                    import ast
                    faculty_solution = ast.literal_eval(faculty_solution)
                
                if isinstance(student_solution, str):
                    import ast
                    student_solution = ast.literal_eval(student_solution)
                
                print(f"✅ Found data for {qn_pdf_name}")
                print(f"   📝 Question ID: {faculty_solution.get('Question ID', 'N/A')}")
                print(f"   📊 Total marks: {faculty_solution.get('total_marks', 'N/A')}")
                print(f"   📄 Student pages: {student_solution.get('pages', [])}")
                
                return faculty_solution, student_solution
        
        print(f"❌ No data found for {qn_pdf_name}")
        return None, None
        
    except Exception as e:
        print(f"❌ Error loading student/faculty data: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def get_student_image_paths(pdf_name, student_solution):
    """Get student image paths from student solution pages"""
    try:
        pages = student_solution.get('pages', [])
        if not pages:
            print("⚠️  No pages found in student solution")
            return []
        
        image_paths = []
        pdf_folder = Path(SOURCE_FOLDER) / f"{pdf_name}.pdf"
        
        for page_num in pages:
            image_path = pdf_folder / f"{pdf_name}_page_{page_num}.jpeg"
            if image_path.exists():
                image_paths.append(str(image_path))
                print(f"✅ Found student page {page_num}: {image_path.name}")
            else:
                print(f"⚠️  Student page {page_num} not found: {image_path}")
        
        return image_paths
        
    except Exception as e:
        print(f"❌ Error getting student image paths: {e}")
        return []

def copy_assessment_json(pdf_name, output_folder):
    """Copy assessment JSON from source to output folder"""
    try:
        source_json = Path(SOURCE_FOLDER) / f"{pdf_name}.pdf" / f"{pdf_name}_assessment_v22.json"
        dest_json = Path(output_folder) / f"{pdf_name}_assessment_v22.json"
        
        if source_json.exists():
            shutil.copy2(source_json, dest_json)
            print(f"📋 Copied assessment JSON to output folder")
            return str(dest_json)
        else:
            print(f"⚠️  Assessment JSON not found: {source_json}")
            return None
    except Exception as e:
        print(f"❌ Error copying assessment JSON: {e}")
        return None

def merge_error_coordinates_with_assessment(assessment_json_path, error_coords_dict, question_no):
    """Merge error coordinates into assessment JSON for specific question"""
    try:
        question_no_float = float(str(question_no).replace('Q', '').replace('q', ''))
        
        # Load assessment JSON
        with open(assessment_json_path, 'r') as f:
            assessment_data = json.load(f)
        
        # Find the matching question
        for item in assessment_data:
            metadata = item.get('metadata', {})
            if metadata.get('question_no') == question_no_float:
                feedback = item.get('feedback', {})
                solution_steps = feedback.get('solution', [])
                
                # Add error coordinates to each step
                for step_data in solution_steps:
                    for key in step_data.keys():
                        if key.startswith('step_') or key.startswith('text_'):
                            step_num = key.split('_')[1]
                            
                            # Find matching error coordinates (or set to null)
                            error_key = f"step_{step_num}_error_coordinates"
                            if error_key in error_coords_dict:
                                step_data["coordinates"] = error_coords_dict[error_key]
                                print(f"   ✅ Added error coordinates for step {step_num}")
                            else:
                                step_data["coordinates"] = None
                                print(f"   ⚠️  No error coordinates for step {step_num}, set to null")
                            break
                
                # Save only this question's data (not entire array)
                final_json_path = Path(assessment_json_path).parent / "final.json"
                with open(final_json_path, 'w') as f:
                    json.dump(item, f, indent=2)
                
                print(f"💾 Saved merged assessment: {final_json_path}")
                return str(final_json_path)
        
        # If we get here, question wasn't found
        print(f"   ❌ Question {question_no_float} not found in assessment")
        return None

        
    except Exception as e:
        print(f"❌ Error merging error coordinates: {e}")
        import traceback
        traceback.print_exc()
        return None

# === Dynamic Prompt Template ===
def create_prompt_with_json(student_q_num, faculty_solution, assessment_feedback, num_student_pages):
    """Create prompt using assessment_v24_error_boxes with JSON faculty solution and assessment feedback"""
    
    # Extract faculty solution details
    question_explanation = faculty_solution.get('Question Explanation', 'N/A')
    solution_steps = faculty_solution.get('Solution', [])
    total_marks = faculty_solution.get('total_marks', 0)
    qb_id = faculty_solution.get('Question ID', 'N/A')
    
    # Format faculty solution steps as text
    solution_text = f"**Question ID:** {qb_id}\n"
    solution_text += f"**Question:** {question_explanation}\n\n"
    solution_text += f"**Total Marks:** {total_marks}\n\n"
    solution_text += "**Faculty Solution Steps:**\n"
    for i, step in enumerate(solution_steps, 1):
        step_key = f"step_{i}"
        if step_key in step:
            step_text = step[step_key]
            step_marks = step.get('marks', 0)
            solution_text += f"  • Step {i} ({step_marks} marks): {step_text}\n"
    
    # Format assessment feedback
    feedback_text = "\n**Assessment Feedback (Identify Errors):**\n"
    if assessment_feedback:
        solution_feedback = assessment_feedback.get('solution', [])
        for step_data in solution_feedback:
            for key, value in step_data.items():
                if key.startswith('step_') or key.startswith('text_'):
                    marks_awarded = step_data.get('marks_awarded', 0)
                    total_marks_step = step_data.get('total_marks', 0)
                    feedback_text += f"\n{key}: {value}\n"
                    feedback_text += f"Marks: {marks_awarded}/{total_marks_step}\n"
                    break
    else:
        feedback_text += "No assessment feedback available.\n"
    
    # Create the prompt with faculty solution and assessment feedback
    prompt = f"""## Faculty Solution (JSON Format - No Images)
{solution_text}
{feedback_text}

---

{assessment_v24_error_boxes}"""
    
    return prompt

# === Image Processing Functions ===
def load_image(image_path):
    """Load image from file path"""
    return Image.open(image_path)

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

def send_to_gemini_with_json(faculty_solution, student_images, prompt):
    """Send faculty JSON and student images to Gemini API"""
    
    print(f"🔍 Debug: Sending to Gemini:")
    print(f"   📝 Prompt: {len(prompt)} characters")
    print(f"   📋 Faculty solution: JSON format (QB_ID: {faculty_solution.get('Question ID', 'N/A')})")
    print(f"   👨‍🎓 Student images: {len(student_images)} images")
    for i, img in enumerate(student_images):
        print(f"   📷 Student Page {i+1}: {img.size}")
    
    # Build content list: [prompt, student_img1, student_img2, ...]
    content = [prompt]
    content.extend(student_images)
    
    print(f"   📊 Total content items: {len(content)}")
    
    try:
        response = model.generate_content(content)
        response_text = response.text
        print(f"Raw response from Gemini: {response_text}")
        
        # Parse JSON response
        import json
        import re
        
        # Try to extract JSON object from markdown code blocks first
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                print(f"❌ No JSON object found in response")
                return None
        
        try:
            # Fix double curly braces that sometimes come from Gemini (only at start/end)
            json_str_cleaned = json_str.strip()
            if json_str_cleaned.startswith('{{') and json_str_cleaned.endswith('}}'):
                # Remove outer pair of braces
                json_str_cleaned = json_str_cleaned[1:-1]
            
            coordinates = json.loads(json_str_cleaned)
            print(f"Parsed result: {coordinates}")
            return coordinates
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"   Attempted to parse: {json_str[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return None

def draw_bounding_boxes(image, error_coords_dict):
    """Draw red bounding boxes for errors from dictionary format"""
    image = image.convert("RGBA")
    error_color = (255, 255, 0, 80)  # Yellow with transparency
    
    if not error_coords_dict:
        print(f"📦 No error boxes to draw")
        return image
    
    print(f"📦 Drawing {len(error_coords_dict)} error bounding boxes...")
    
    for step_key, error_data in error_coords_dict.items():
        if not error_data or not isinstance(error_data, dict):
            continue
        
        coords_list = error_data.get('coords', [])
        page = error_data.get('page', 1)
        
        # Check if coords_list contains multiple boxes (array of arrays) or single box (flat array)
        if coords_list and isinstance(coords_list[0], list):
            # Multiple boxes: [[x1,y1,x2,y2], [x3,y3,x4,y4], ...]
            boxes = coords_list
            print(f"   📦 {step_key} (Page {page}): {len(boxes)} error boxes")
        elif len(coords_list) == 4 and all(isinstance(c, (int, float)) for c in coords_list):
            # Single box: [x1,y1,x2,y2]
            boxes = [coords_list]
            print(f"   📦 {step_key} (Page {page}): 1 error box")
        else:
            print(f"   ❌ Invalid coords format for {step_key}")
            continue
        
        # Draw each box
        for i, coords in enumerate(boxes):
            if len(coords) != 4:
                print(f"      ❌ Invalid coords length for box {i+1}: {len(coords)}")
                continue
            
            # Auto-detect coordinate range and normalize to 0-1
            if all(coord <= 1.0 for coord in coords):
                # Already in 0-1 range
                ymin, xmin, ymax, xmax = coords
                print(f"      ℹ️  Detected 0-1 range, using as-is")
            else:
                # In 0-1000 range, normalize
                ymin, xmin, ymax, xmax = [coord / 1000 for coord in coords]
            left = xmin * image.width
            top = ymin * image.height
            right = xmax * image.width
            bottom = ymax * image.height
            
            print(f"      Box {i+1}: ({left:.1f}, {top:.1f}) to ({right:.1f}, {bottom:.1f})")
            
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([left, top, right, bottom], fill=error_color, outline=None)
            image = Image.alpha_composite(image, overlay)
    
    return image

# === Main Processing Function ===
def process_single_question(pdf_name, question_number):
    """Process a single question"""
    
    print(f"\n{'='*70}")
    print(f"📝 Processing Question {question_number}")
    print(f"{'='*70}")
    
    # Create output folder for this question
    output_folder = f"{BASE_OUTPUT_FOLDER}/{pdf_name}/question_{int(question_number)}"
    os.makedirs(output_folder, exist_ok=True)
    print(f"📁 Output folder: {output_folder}")
    
    # Copy assessment JSON
    print(f"\n📋 Step 1: Copying assessment JSON...")
    assessment_json_path = copy_assessment_json(pdf_name, output_folder)
    
    # Load assessment data
    print(f"\n📋 Step 2: Loading assessment data...")
    assessment_item = load_assessment_for_question(pdf_name, question_number)
    
    if not assessment_item:
        print(f"⚠️  Skipping Question {question_number} - No assessment data")
        return False
    
    assessment_feedback = assessment_item.get('feedback', {})
    
    # Load student and faculty solutions
    print(f"\n📋 Step 3: Loading student and faculty solutions...")
    faculty_solution, student_solution = load_student_faculty_data(pdf_name, question_number)
    
    if not faculty_solution or not student_solution:
        print(f"⚠️  Skipping Question {question_number} - No solution data")
        return False
    
    # Get student image paths
    print(f"\n📋 Step 4: Loading student images...")
    student_image_paths = get_student_image_paths(pdf_name, student_solution)
    
    if not student_image_paths:
        print(f"⚠️  Skipping Question {question_number} - No student images")
        return False
    
    # Load and resize student images
    student_images = []
    resized_student_images = []
    for i, student_path in enumerate(student_image_paths):
        print(f"📷 Loading student page {i+1}: {os.path.basename(student_path)}")
        student_img = load_image(student_path)
        print(f"📐 Student page {i+1} size: {student_img.size[0]}x{student_img.size[1]}")
        student_images.append(student_img)
        
        # Resize student image
        _, _, resized_student = resize_image(student_img)
        resized_student_images.append(resized_student)
        print(f"📐 Resized student page {i+1} to: {resized_student.size[0]}x{resized_student.size[1]}")
    
    # Create prompt
    print(f"\n📋 Step 5: Creating prompt with assessment feedback...")
    prompt = create_prompt_with_json(
        question_number, 
        faculty_solution, 
        assessment_feedback, 
        len(student_image_paths)
    )
    print(f"✨ Using prompt: assessment_v24_error_boxes from prompt_store")
    
    # Send to Gemini
    print(f"\n📋 Step 6: Sending to Gemini for error detection...")
    error_coords_dict = send_to_gemini_with_json(faculty_solution, resized_student_images, prompt)
    
    if error_coords_dict is None:
        print(f"⚠️  Skipping Question {question_number} - No response from Gemini")
        return False
    
    if not isinstance(error_coords_dict, dict):
        print(f"⚠️  Skipping Question {question_number} - Invalid response format")
        return False
    
    print(f"📊 Found {len(error_coords_dict)} error coordinates")
    
    # Merge error coordinates with assessment
    if assessment_json_path:
        print(f"\n📋 Step 7: Merging error coordinates with assessment...")
        merge_error_coordinates_with_assessment(assessment_json_path, error_coords_dict, question_number)
    
    # Group errors by page
    errors_by_page = {}
    for step_key, error_data in error_coords_dict.items():
        if not error_data:
            continue
        
        # Handle array of page-specific error coordinates: [{"page": 1, "coords": [...]}, {"page": 2, "coords": [...]}]
        if isinstance(error_data, list) and len(error_data) > 0 and isinstance(error_data[0], dict) and 'page' in error_data[0]:
            for coord_obj in error_data:
                page = coord_obj.get('page', 1)
                if page not in errors_by_page:
                    errors_by_page[page] = {}
                # Store each page's coordinates separately with a unique key
                page_key = f"{step_key}_page{page}"
                errors_by_page[page][page_key] = coord_obj
                print(f"   ✅ {step_key}: page {page}, coords {coord_obj.get('coords', [])}")
        
        # Handle single dictionary format: {"page": 1, "coords": [...]}
        elif isinstance(error_data, dict):
            page = error_data.get('page', 1)
            if page not in errors_by_page:
                errors_by_page[page] = {}
            errors_by_page[page][step_key] = error_data
    
    # Draw error boxes on images
    print(f"\n📋 Step 8: Drawing error boxes on images...")
    for i, resized_student in enumerate(resized_student_images):
        page_num = i + 1
        
        # Get errors for this page
        page_errors = errors_by_page.get(page_num, {})
        
        if page_errors:
            # Draw error boxes
            error_image = draw_bounding_boxes(resized_student.copy(), page_errors)
        
            # Convert to RGB and save
            final_error_image = error_image.convert("RGB")
            error_filename = f"{output_folder}/{pdf_name}_page{page_num}_errors.png"
            final_error_image.save(error_filename)
            print(f"💾 Saved error image (Page {page_num}): {error_filename}")
        else:
            print(f"   ℹ️  No errors on page {page_num}")
        
        # Save original
        original_filename = f"{output_folder}/{pdf_name}_student_page{page_num}_original.png"
        resized_student.save(original_filename)
        print(f"💾 Saved original (Page {page_num}): {original_filename}")
    
    # Save error boxes JSON
    error_json_filename = f"{output_folder}/error_boxes.json"
    with open(error_json_filename, 'w') as f:
        json.dump(error_coords_dict, f, indent=2)
    print(f"💾 Saved error boxes: {error_json_filename}")
    
    # Save faculty solution JSON for reference
    faculty_json_filename = f"{output_folder}/faculty_solution.json"
    with open(faculty_json_filename, 'w') as f:
        json.dump(faculty_solution, f, indent=2)
    print(f"💾 Saved faculty solution: {faculty_json_filename}")
    
    # Save assessment data
    assessment_json_filename = f"{output_folder}/assessment.json"
    with open(assessment_json_filename, 'w') as f:
        json.dump(assessment_item, f, indent=2)
    print(f"💾 Saved assessment: {assessment_json_filename}")
    
    print(f"\n✅ Question {question_number} completed!")
    return True

def process_all_questions():
    """Main function to process all questions in a PDF"""
    
    print("🎯 Faculty-Guided Step Processor v2 - Error Detection Mode")
    print("=" * 70)
    print(f"📁 PDF: {PDF_NAME}")
    print("=" * 70)
    
    # Get all questions from assessment
    print(f"\n📋 Loading all questions from assessment...")
    question_numbers = get_all_questions_from_assessment(STUDENT_PDF_NAME)
    
    if not question_numbers:
        print("❌ No questions found in assessment")
        return
    
    print(f"\n🚀 Processing {len(question_numbers)} questions sequentially...")
    
    # Process each question
    success_count = 0
    failed_count = 0
    
    for i, question_number in enumerate(question_numbers, 1):
        print(f"\n{'#'*70}")
        print(f"# Question {i}/{len(question_numbers)}: Q{int(question_number)}")
        print(f"{'#'*70}")
        
        success = process_single_question(STUDENT_PDF_NAME, question_number)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
    
    # Summary
    print(f"\n{'='*70}")
    print(f"🎉 Processing Complete!")
    print(f"={'='*70}")
    print(f"✅ Successfully processed: {success_count} questions")
    print(f"⚠️  Failed/Skipped: {failed_count} questions")
    print(f"📂 Output folder: {BASE_OUTPUT_FOLDER}/{STUDENT_PDF_NAME}/")
    print(f"{'='*70}")

if __name__ == "__main__":
    print("🚀 Starting Error Detection Processing...")
    print(f"📝 PDF: {PDF_NAME}")
    print(f"✨ Using assessment_v24_error_boxes from prompt_store")
    print()
    
    try:
        process_all_questions()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
