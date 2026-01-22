#!/usr/bin/env python3
"""
Answer Bounding Box Detection System
===================================

This system processes question-level solutions and detects bounding boxes for answers
on specific pages using the page number from the solution JSON.

It reads question solutions, extracts page numbers, finds corresponding page images,
and uses Gemini to detect bounding boxes for the specific answer number.
"""

import os
import json
import re
from pathlib import Path
from PIL import Image, ImageDraw
import google.generativeai as genai
from dotenv import load_dotenv
import cv2
import numpy as np

# Load environment variables
load_dotenv()

# Configure Gemini
model_name = "gemini-2.5-pro"
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
model = genai.GenerativeModel(model_name)

# Image processing settings
DIM = 768

def resize_image(image, dim=DIM):
    """Resize image while maintaining aspect ratio"""
    image1 = np.array(image.convert('RGB'))
    original_size = image1.shape
    image1 = image1.mean(axis=2)  # Convert to grayscale
    h, w = image1.shape
    if w > h:
        new_w = dim
        new_h = int(h * (dim / w))
    else:
        new_h = dim
        new_w = int(w * (dim / h))
    resized_image = cv2.resize(image1, (new_w, new_h), interpolation=cv2.INTER_AREA)
    resized_image_pil = Image.fromarray(resized_image)
    resized_image_pil = resized_image_pil.convert('RGB')
    return original_size, (new_h, new_w), resized_image_pil

# Removed extract_answer_number_from_solution() - no longer used
# Current implementation uses question filename (e.g., "6.json" -> answer_number = 6)

def get_bounding_boxes_for_answer(images, answer_number, page_numbers):
    """Get bounding boxes for a specific answer number across multiple pages"""
    
    prompt = f"""Return bounding boxes as JSON arrays on answer {answer_number} as [ymin, xmin, ymax, xmax]"""

    try:
        # Send prompt + all images together
        content = [prompt] + images
        response = model.generate_content(content)
        raw_response = response.text.strip()
        
        print(f"Raw Gemini response for answer {answer_number} on pages {page_numbers}:")
        print(raw_response)
        
        # Use regex to extract JSON arrays from mixed text/JSON responses
        json_pattern = r'\[\s*(?:\{[^}]*\}|\[[^\]]*\])\s*(?:,\s*(?:\{[^}]*\}|\[[^\]]*\])\s*)*\]'
        json_matches = re.findall(json_pattern, raw_response, re.DOTALL)
        
        if json_matches:
            try:
                # Try to parse the first JSON array found
                parsed = json.loads(json_matches[0])
                return parsed
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                return None
        else:
            print(f"❌ No JSON array found in response: {raw_response}")
            return None
            
    except Exception as e:
        print(f"❌ Error calling Gemini: {e}")
        return None

def draw_answer_bounding_boxes(image, coords, answer_number):
    """Draw bounding boxes on image for answer visualization"""
    # Open image using PIL and ensure it's in RGBA mode for transparency
    image = image.convert("RGBA")
    
    # Create drawing context
    draw = ImageDraw.Draw(image)

    # Define a translucent highlight color (yellow with ~12% opacity)
    highlight_color = (255, 255, 0, 114)  # RGBA: Yellow with transparency
    border_color = (255, 255, 0, 200)     # RGBA: Yellow border, more opaque
    
    for box in coords:
        # Ensure that the bounding box is in the form of [ymin, xmin, ymax, xmax]
        if len(box) == 4:
            ymin, xmin, ymax, xmax = [coord / 1000 for coord in box]  # Normalize to 0-1 range
            
            # Scale the coordinates to the resized image dimensions
            left = int(xmin * image.width)   # Convert to actual pixel position
            top = int(ymin * image.height)   # Convert to actual pixel position
            right = int(xmax * image.width)  # Convert to actual pixel position
            bottom = int(ymax * image.height) # Convert to actual pixel position

            # Create a transparent overlay of the same size as the image
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))

            # Draw the translucent background only in the bounding box region on the overlay
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([left, top, right, bottom], fill=highlight_color, outline=border_color, width=2)

            # Composite the original image with the overlay (keeping text visible)
            image = Image.alpha_composite(image, overlay)
            
            # No text labels - just yellow highlighting

    return image

def find_page_image(pdf_name, page_number, cache_dir):
    """Find the page image file for a specific PDF and page number"""
    cache_dir = Path(cache_dir)
    pdf_dir = cache_dir / pdf_name
    
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        return None
    
    # Look for page image with pattern: {pdf_name}_page_{page_number}.jpeg
    pdf_base_name = pdf_name.replace('.pdf', '')
    page_image_pattern = f"{pdf_base_name}_page_{page_number}.jpeg"
    page_image_path = pdf_dir / page_image_pattern
    
    if page_image_path.exists():
        return page_image_path
    
    # Alternative patterns to try
    alternative_patterns = [
        f"{pdf_base_name}_PAGE_{page_number}.jpeg",
        f"{pdf_base_name}_Page_{page_number}.jpeg",
        f"page_{page_number}.jpeg",
        f"PAGE_{page_number}.jpeg"
    ]
    
    for pattern in alternative_patterns:
        alt_path = pdf_dir / pattern
        if alt_path.exists():
            return alt_path
    
    print(f"❌ Page image not found for {pdf_name}, page {page_number}")
    print(f"   Looked for: {page_image_pattern}")
    return None

def process_question_solution_with_pdf(solution_file_path, pdf_name, cache_dir, output_dir):
    """Process a single question solution file with known PDF context"""
    
    try:
        # Ensure output directory exists
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load solution JSON
        with open(solution_file_path, 'r') as f:
            solution_data = json.load(f)
        
        question_id = solution_data.get("Question ID")
        solution_text = solution_data.get("Solution", "")
        pages = solution_data.get("pages", [])
        question_number = Path(solution_file_path).stem
        
        if not pages:
            print(f"❌ No pages found for question {question_number} in {pdf_name}")
            return None
        
        # Use question number from filename as the answer number
        answer_number = int(question_number)
        
        print(f"📄 Processing {pdf_name}/Question {question_number}: Answer {answer_number}, Pages {pages}")
        
        results = []
        
        # Collect all page images first
        page_images = []
        page_image_paths = []
        valid_pages = []
        
        for page_number in pages:
            page_image_path = find_page_image(pdf_name, page_number, cache_dir)
            if page_image_path:
                print(f"✅ Found page image: {page_image_path}")
                image = Image.open(page_image_path)
                original_size, new_size, resized_image = resize_image(image)
                page_images.append(resized_image)
                page_image_paths.append(page_image_path)
                valid_pages.append(page_number)
            else:
                print(f"❌ Could not find page image for {pdf_name}, page {page_number}")
        
        if page_images:
            print(f"📄 Processing {len(page_images)} pages for answer {answer_number}")
            
            # Process each page individually to get page-specific coordinates
            page_results = []
            
            for i, (page_image, page_number, page_image_path) in enumerate(zip(page_images, valid_pages, page_image_paths)):
                print(f"📄 Processing page {page_number} for answer {answer_number}")
                
                # Send single page to Gemini
                bboxes = get_bounding_boxes_for_answer([page_image], answer_number, [page_number])
                
                if bboxes:
                    # Extract coordinates for this specific page
                    coords = []
                    for bbox in bboxes:
                        if isinstance(bbox, dict) and "box_2d" in bbox:
                            coords.append(bbox["box_2d"])
                        elif isinstance(bbox, list) and len(bbox) == 4:
                            coords.append(bbox)
                    
                    # Create result entry for this page
                    page_result = {
                        "question_id": question_id or question_number,
                        "question_number": question_number,
                        "pdf_name": pdf_name,
                        "page_number": page_number,
                        "answer_number": answer_number,
                        "page_image_path": str(page_image_path),
                        "original_size": original_size,
                        "resized_size": new_size,
                        "bounding_boxes": bboxes,
                        "solution_text": solution_text[:200] + "..." if len(solution_text) > 200 else solution_text
                    }
                    page_results.append(page_result)
                    
                    # Create annotated image for this specific page with its coordinates
                    if coords and output_dir:
                        pdf_output_dir = Path(output_dir) / pdf_name.replace('.pdf', '')
                        pdf_output_dir.mkdir(exist_ok=True)
                        
                        annotated_image = draw_answer_bounding_boxes(page_image, coords, answer_number)
                        
                        annotated_filename = f"question_{question_number}_answer_{answer_number}_page_{page_number}_annotated.jpg"
                        annotated_path = pdf_output_dir / annotated_filename
                        annotated_image.convert("RGB").save(annotated_path)
                        print(f"🎨 Saved annotated image: {annotated_path}")
                else:
                    print(f"❌ No bounding boxes found for answer {answer_number} on page {page_number}")
                    
                    # Save failed detection info with images and question files
                    if output_dir:
                        failed_dir = Path(output_dir).parent / "failed_bbox_results"
                        failed_dir.mkdir(exist_ok=True)
                        
                        failed_pdf_dir = failed_dir / pdf_name.replace('.pdf', '')
                        failed_pdf_dir.mkdir(exist_ok=True)
                        
                        # Copy the page image for manual review
                        if page_image_path and Path(page_image_path).exists():
                            failed_image_name = f"question_{question_number}_answer_{answer_number}_page_{page_number}_failed.jpeg"
                            failed_image_path = failed_pdf_dir / failed_image_name
                            
                            import shutil
                            shutil.copy2(page_image_path, failed_image_path)
                            print(f"📷 Copied failed image: {failed_image_path}")
                        
                        # Copy the question JSON file for reference
                        question_json_source = Path(cache_dir) / pdf_name / "question_level_solutions" / f"{question_number}.json"
                        if question_json_source.exists():
                            question_json_name = f"question_{question_number}_solution.json"
                            question_json_dest = failed_pdf_dir / question_json_name
                            shutil.copy2(question_json_source, question_json_dest)
                            print(f"📄 Copied question JSON: {question_json_dest}")
                        
                        # Save failure metadata
                        failed_info = {
                            "question_id": question_id or question_number,
                            "question_number": question_number,
                            "pdf_name": pdf_name,
                            "page_number": page_number,
                            "answer_number": answer_number,
                            "page_image_path": str(page_image_path),
                            "failed_image_copy": f"question_{question_number}_answer_{answer_number}_page_{page_number}_failed.jpeg",
                            "question_json_copy": f"question_{question_number}_solution.json",
                            "failure_reason": "No bounding boxes detected by Gemini",
                            "solution_text": solution_text[:200] + "..." if len(solution_text) > 200 else solution_text,
                            "manual_review_files": {
                                "image": f"question_{question_number}_answer_{answer_number}_page_{page_number}_failed.jpeg",
                                "question_json": f"question_{question_number}_solution.json",
                                "failure_metadata": f"question_{question_number}_answer_{answer_number}_page_{page_number}_failed.json"
                            }
                        }
                        
                        failed_filename = f"question_{question_number}_answer_{answer_number}_page_{page_number}_failed.json"
                        failed_path = failed_pdf_dir / failed_filename
                        
                        with open(failed_path, 'w') as f:
                            json.dump(failed_info, f, indent=2)
                        
                        print(f"📝 Saved failure metadata: {failed_path}")
            
            # Combine all page results
            if page_results:
                # Create combined result
                combined_result = {
                    "question_id": question_id or question_number,
                    "question_number": question_number,
                    "pdf_name": pdf_name,
                    "pages_processed": valid_pages,
                    "answer_number": answer_number,
                    "page_results": page_results,
                    "total_pages": len(page_results),
                    "solution_text": solution_text[:200] + "..." if len(solution_text) > 200 else solution_text
                }
                results.append(combined_result)
            else:
                print(f"❌ No bounding boxes found for answer {answer_number} across any pages")
        else:
            print(f"❌ No valid page images found for question {question_number}")
        
        # Save results if any found
        if results:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            
            # Create PDF-specific output directory
            pdf_output_dir = output_dir / pdf_name.replace('.pdf', '')
            pdf_output_dir.mkdir(exist_ok=True)
            
            output_file = pdf_output_dir / f"question_{question_number}_answer_bboxes.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"✅ Saved results for {pdf_name}/question_{question_number}: {len(results)} pages processed")
            return results
        else:
            print(f"❌ No results generated for {pdf_name}/question_{question_number}")
            return None
            
    except Exception as e:
        print(f"❌ Error processing {solution_file_path}: {e}")
        return None

def process_question_solution(solution_file_path, cache_dir, output_dir):
    """Legacy function for backward compatibility"""
    # Extract PDF name from the solution file path
    path_parts = Path(solution_file_path).parts
    pdf_name = None
    
    for part in path_parts:
        if part.endswith('.pdf'):
            pdf_name = part
            break
    
    if not pdf_name:
        print(f"❌ Could not determine PDF name from path: {solution_file_path}")
        return None
    
    return process_question_solution_with_pdf(solution_file_path, pdf_name, cache_dir, output_dir)

def find_all_question_solutions(cache_dir):
    """Find all question solution files across all PDF folders in cache"""
    
    cache_dir = Path(cache_dir)
    if not cache_dir.exists():
        print(f"❌ Cache directory not found: {cache_dir}")
        return []
    
    all_solution_files = []
    
    # Look through each PDF folder in cache
    for pdf_dir in cache_dir.iterdir():
        if pdf_dir.is_dir() and pdf_dir.name.endswith('.pdf'):
            # Look for question_level_solutions subfolder
            solutions_subdir = pdf_dir / "question_level_solutions"
            
            if solutions_subdir.exists():
                # Find all JSON files (question numbers)
                json_files = list(solutions_subdir.glob("*.json"))
                
                for json_file in json_files:
                    # Store both the file path and the PDF it belongs to
                    all_solution_files.append({
                        'solution_file': json_file,
                        'pdf_name': pdf_dir.name,
                        'pdf_dir': pdf_dir,
                        'question_number': json_file.stem
                    })
                
                if json_files:
                    print(f"📁 Found {len(json_files)} questions in {pdf_dir.name}")
    
    print(f"🔍 Total question solutions found: {len(all_solution_files)}")
    return all_solution_files

def process_all_question_solutions(cache_dir, output_dir):
    """Process all question solution files from cache directory"""
    
    # Find all question solution files
    all_solution_files = find_all_question_solutions(cache_dir)
    
    if not all_solution_files:
        print(f"❌ No question solution files found in cache")
        return {}
    
    print(f"🚀 Processing {len(all_solution_files)} question solutions")
    
    all_results = {}
    successful = 0
    failed = 0
    
    for i, solution_info in enumerate(all_solution_files, 1):
        solution_file = solution_info['solution_file']
        pdf_name = solution_info['pdf_name']
        question_number = solution_info['question_number']
        
        print(f"\n[{i}/{len(all_solution_files)}] Processing: {pdf_name}/question_{question_number}")
        
        # Process the question solution with known PDF context
        result = process_question_solution_with_pdf(
            solution_file, pdf_name, cache_dir, output_dir
        )
        
        if result:
            result_key = f"{pdf_name}_{question_number}"
            all_results[result_key] = result
            successful += 1
        else:
            failed += 1
    
    # Save summary
    output_dir = Path(output_dir)
    failed_dir = output_dir.parent / "failed_bbox_results"
    
    # Count failed files
    failed_files_count = 0
    if failed_dir.exists():
        failed_files_count = len(list(failed_dir.glob("**/*.json")))
    
    summary = {
        "total_questions_processed": len(all_solution_files),
        "successful": successful,
        "failed": failed,
        "failed_detections_count": failed_files_count,
        "results_by_pdf_question": {key: len(results) for key, results in all_results.items()}
    }
    
    summary_file = output_dir / "answer_bbox_detection_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n🎉 Processing completed!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"🚫 Failed detections: {failed_files_count}")
    print(f"📊 Summary saved to: {summary_file}")
    
    if failed_files_count > 0:
        print(f"📁 Failed detection details saved to: {failed_dir}")
    
    return all_results

def main():
    """Main function"""
    
    # Configuration
    CACHE_DIR = "/Users/simrannaik/Desktop/subjective_grading/data/iteration_2/cache"
    OUTPUT_DIR = "/Users/simrannaik/Desktop/subjective_grading/data/answer_bbox_results"
    
    print("🎯 Answer Bounding Box Detection System")
    print("=" * 50)
    print(f"📁 Cache Dir: {CACHE_DIR}")
    print(f"💾 Output Dir: {OUTPUT_DIR}")
    print("=" * 50)
    
    # Validate API key
    if not os.getenv("GOOGLE_GEMINI_API"):
        print("❌ Error: GOOGLE_GEMINI_API not found in .env file")
        return False
    
    # Process all solutions from cache directory
    results = process_all_question_solutions(CACHE_DIR, OUTPUT_DIR)
    
    return len(results) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)