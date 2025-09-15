git import sys
import os
import json
import time
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

# Import our utility modules
from ocr.utils.image_utils import resize_image
from ocr.utils.pdf_utils import pdf_to_images
from ocr.utils.cache_utils import (
    create_request_hash, load_cached_response, save_cached_response)
from ocr.config import IMAGE_RESIZE_DIM, RESIZED_IMAGE_PATTERN
import ocr.prompt_store as ps

# === Load API Key ===
load_dotenv()
model_name = "gemini-2.5-pro"
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))
model = genai.GenerativeModel(model_name)


def send_to_gemini_with_cache(prompt: str, resized_images_objs: list, cache_dir: Optional[str] = None) -> Optional[dict]:
    """
    Send request to Gemini with optional caching functionality.
    
    Args:
        prompt: The OCR prompt to use
        resized_images_objs: List of resized image objects
        cache_dir: Optional directory for caching responses
        
    Returns:
        dict or None: OCR results if successful, None otherwise
    """
    # Create request hash for caching (with debug output)
    #debug_hash_creation(prompt, model_name, resized_images_objs)
    request_hash = create_request_hash(prompt, model_name, resized_images_objs)
    
    # Check for cached response if cache_dir is provided
    if cache_dir:
        print(f"🔍 Checking for cached response in {cache_dir}...")
        cached_response = load_cached_response(cache_dir, request_hash)
        if cached_response:
            print(f"⚡ Using cached response (saved {cached_response.get('processing_time_seconds', 0):.2f}s)")
            return cached_response.get('response_data')
    
    # Make API call with timing
    start_time = time.time()
    try:
        print(f"🔄 Making API call to {model_name}...")
        response = model.generate_content([prompt] + resized_images_objs)
        processing_time = time.time() - start_time
        
        # Process response
        raw = response.text.strip()
        cleaned = raw.strip('```json').strip('```').strip()
        parsed = json.loads(cleaned)
        
        print(f"✅ API call completed in {processing_time:.2f}s")
        
        # Save to cache if cache_dir is provided
        if cache_dir:
            save_cached_response(cache_dir, request_hash, parsed, processing_time)
        
        return parsed
        
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ Failed to process images after {processing_time:.2f}s: {e}")
        return None


def ocr_pdf(pdf_file_path: str, output_folder: str, cache_dir: Optional[str] = None, 
           prompt_version: str = "v3") -> Optional[dict]:
    """
    Main OCR processing function with caching support.
    
    Args:
        pdf_file_path: Path to the PDF file to process
        output_folder: Directory to save processed images and results
        cache_dir: Optional directory for caching API responses
        prompt_version: Version of prompt to use (v1, v2, v3)
        
    Returns:
        dict or None: OCR results if successful, None otherwise
    """
    # Get the appropriate prompt
    prompt = getattr(ps, prompt_version, ps.v3)
    

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    print(f"📄 Processing PDF: {pdf_file_path}")
    
    # Step 1: Convert PDF to images
    print("🖼️  Converting PDF to images...")
    images, num_pages = pdf_to_images(pdf_file_path, output_folder)
    print(f"✅ Converted {num_pages} pages to images")

    # Step 2: Resize images
    print(f"🔄 Resizing images to {IMAGE_RESIZE_DIM}...")
    resized_images = []
    for page_num in range(len(images)):
        img_path = images[page_num]
        original_size, new_size, resized_image = resize_image(Image.open(img_path), dim=IMAGE_RESIZE_DIM)
        
        # Save resized image using configurable dimension in filename
        img_filename_dim = RESIZED_IMAGE_PATTERN.format(dim=IMAGE_RESIZE_DIM, page_num=page_num + 1)
        resized_image.save(os.path.join(output_folder, img_filename_dim))
        
        resized_images.append(resized_image)
    print(f"✅ Resized {len(resized_images)} images to {IMAGE_RESIZE_DIM}")

    # Step 3: Send to Gemini for OCR with caching
    print(f"🤖 Processing with {model_name} (prompt: {prompt_version})...")
    results = send_to_gemini_with_cache(prompt, resized_images, cache_dir)

    # Step 4: Save the OCR results
    if results:
        output_json_filename = "output.json"
        json_path = os.path.join(output_folder, output_json_filename)

        # Save the OCR results
        with open(json_path, "w") as f:
            json.dump(results, f, indent=3)

        print(f"💾 OCR results saved to {json_path}")
        return results
    else:
        print("❌ No results from Gemini OCR")
        return None


if __name__ == "__main__":

    pdf_file_path = "/Users/dhirajdaga/Documents/code/ds-prototypes/subjective_grading/data/subject_wise_coverage_samples/biology/04_10021039411060911141694339166.pdf"
    output_folder = "/Users/dhirajdaga/Documents/code/ds-prototypes/subjective_grading/data/ocr_files"

    cache_dir = "/Users/dhirajdaga/Documents/code/ds-prototypes/subjective_grading/data/ocr_cache"
    #prompt_version = "v3"
    prompt_version = "v6"

    results = ocr_pdf(pdf_file_path, output_folder, cache_dir, prompt_version)
    
    if results:
        print("🎉 OCR processing completed successfully!")
    else:
        print("💥 OCR processing failed!")
        sys.exit(1)