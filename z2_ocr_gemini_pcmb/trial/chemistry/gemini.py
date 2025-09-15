import sys
import os
from typing import Optional, List, Union
from PIL import Image

# Add current directory first for local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Add parent directory to path to find ocr module
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(1, parent_dir)

import ocr.prompt_store as ps  # Only this comes from main ocr directory
from processors import ImageProcessor
from api_handler import send_to_gemini_with_cache
from ocr.results import ResultsManager
from ocr.utils.cache_utils import create_pdf_request_hash, load_cached_response
from ocr.client import get_model_name
from config import IMAGE_RESIZE_DIM

# Import the new function from config
from config import create_pdf_output_structure

def ocr_pdf(pdf_file_path: str, output_folder: str, cache_dir: Optional[str], 
           prompt_version: str ) -> Optional[dict]:
    """
    Converts PDF to images, then processes with Gemini OCR. 
    Checks cache before PDF processing to avoid expensive conversion.
    """
    # Get the appropriate prompt
    prompt = getattr(ps, prompt_version)
    model_name = get_model_name()
    pdf_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
    
    # Create dynamic output structure for this PDF
    pdf_output_paths = create_pdf_output_structure(pdf_name)
    
    # Use the dynamically created paths
    output_folder = pdf_output_paths['images']
    cache_dir = pdf_output_paths['cache']
    
    # Initialize processors
    image_processor = ImageProcessor(output_folder)
    results_manager = ResultsManager(pdf_output_paths['json'])
    
    # Check cache before processing PDF to images
    if cache_dir:
        print(f"Checking cache before PDF processing...")
        pdf_request_hash = create_pdf_request_hash(
            pdf_file_path=pdf_file_path,
            prompt_text=prompt,
            prompt_version=prompt_version,
            image_dimension=IMAGE_RESIZE_DIM,
            model_name=model_name,
            questions=None  # No questions for regular PDF OCR
        )
        
        cached_response = load_cached_response(cache_dir, pdf_request_hash)
        if cached_response:
            print("Using cached response - PDF processing skipped!")
            cached_results = cached_response.get('response_data')
            if cached_results:
                results_manager.save_pdf_results(cached_results)
            return cached_results
    
    # Cache miss - proceed with PDF processing
    print("Cache miss - processing PDF to images...")
    
    # Process PDF to images
    page_images = image_processor.process_pdf(pdf_file_path)
    
    # Build content list for API call
    content = [prompt]
    if page_images:
        content.extend(page_images)
    
    # Send to Gemini for OCR with metadata for caching
    print(f"Processing with Gemini (prompt: {prompt_version})...")
    results = send_to_gemini_with_cache(
        content=content,
        cache_dir=cache_dir,
        pdf_name=pdf_name,
        prompt_version=prompt_version,
        image_size=IMAGE_RESIZE_DIM
    )
    
    # Save results
    if results:
        results_manager.save_pdf_results(results)
        return results
    else:
        print("No results from Gemini OCR")
        return None


def ocr_with_questions(questions: List[str], pdf_file_path: str, output_folder: str, cache_dir: Optional[str], 
                      prompt_version: str) -> Optional[dict]:
    """
    Processes questions and solution images with special format:
    [prompt] + ["# Question set : "] + questions + [" # Hand written solutions : "] + images
    Questions can be text, images, or mixed content - handled as binary for caching.
    """
    # Get the appropriate prompt
    prompt = getattr(ps, prompt_version)
    model_name = get_model_name()
    pdf_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
    
    # Create dynamic output structure for this PDF
    pdf_output_paths = create_pdf_output_structure(pdf_name)
    
    # Use the dynamically created paths
    output_folder = pdf_output_paths['images']
    cache_dir = pdf_output_paths['cache']
    
    # Initialize processors
    image_processor = ImageProcessor(output_folder)
    results_manager = ResultsManager(pdf_output_paths['json'])
    
    # Check cache before processing PDF to images
    if cache_dir:
        print(f"Checking cache before PDF processing...")
        # Pass questions directly to hash function (can handle binary/mixed content)
        pdf_request_hash = create_pdf_request_hash(
            pdf_file_path=pdf_file_path,
            prompt_text=prompt,
            prompt_version=prompt_version,
            image_dimension=IMAGE_RESIZE_DIM,
            model_name=model_name,
            questions=questions  # Pass questions directly for binary hashing
        )
        
        cached_response = load_cached_response(cache_dir, pdf_request_hash)
        if cached_response:
            print("Using cached response - PDF processing skipped!")
            cached_results = cached_response.get('response_data')
            if cached_results:
                results_manager.save_question_results(cached_results)
            return cached_results
    
    # Cache miss - proceed with PDF processing
    print("Cache miss - processing PDF to images...")
    
    # Process images
    hand_written_solutions = image_processor.process_pdf(pdf_file_path=pdf_file_path)
    
    print(f"Processing {len(questions)} questions with {len(hand_written_solutions)} solution images")
    # Build content list for API call with questions
    content = [prompt]
    if questions:
        content.extend(["# Question set : "] + questions + [" # Hand written solutions : "])
    if hand_written_solutions:
        content.extend(hand_written_solutions)
    
    # Send to Gemini for OCR with questions and solutions
    print(f"Processing with Gemini (prompt: {prompt_version})...")
    results = send_to_gemini_with_cache(
        content=content,
        cache_dir=cache_dir,
        pdf_name=pdf_name,
        prompt_version=prompt_version,
        image_size=IMAGE_RESIZE_DIM,
        questions_count=len(questions)  # Pass questions count for metadata
    )
    
    # Save results
    if results:
        results_manager.save_question_results(results)
        return results
    else:
        print("No results from Gemini OCR")
        return None


if __name__ == "__main__":
    # Example usage
    pdf_file_path = "/Users/dhirajdaga/Documents/code/ds-prototypes/subjective_grading/data/subject_wise_coverage_samples/biology/04_10021039411060911141694339166.pdf"
    output_folder = "/Users/dhirajdaga/Documents/code/ds-prototypes/subjective_grading/data/ocr_files"
    cache_dir = "/Users/dhirajdaga/Documents/code/ds-prototypes/subjective_grading/data/ocr_cache"
    prompt_version = "v6"

    results = ocr_pdf(pdf_file_path, output_folder, cache_dir, prompt_version)
    
    if results:
        print("OCR processing completed successfully!")
        results_manager = ResultsManager(output_folder)
        summary = results_manager.get_summary(results)
        print(summary)
    else:
        print("OCR processing failed!")
        sys.exit(1) 