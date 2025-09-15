import json
import time
import os
import sys
from typing import Optional, List
from PIL import Image

# Add current directory first for local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Add parent directory to path to find ocr module
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(1, parent_dir)

from ocr.client import get_model, get_model_name
from ocr.utils.cache_utils import (
    create_request_hash, load_cached_response, save_cached_response)

def get_dynamic_cache_dir(pdf_name: Optional[str] = None) -> str:
    """
    Dynamically determine the cache directory within the Physics directory.
    
    Args:
        pdf_name (Optional[str]): Name of the PDF to create a specific cache subdirectory.
    
    Returns:
        str: Path to the cache directory
    """
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create the base cache directory
    cache_base_dir = os.path.join(base_dir, 'output')
    os.makedirs(cache_base_dir, exist_ok=True)
    
    # If a PDF name is provided, create a subdirectory for it
    if pdf_name:
        pdf_cache_dir = os.path.join(cache_base_dir, pdf_name, 'cache')
        os.makedirs(pdf_cache_dir, exist_ok=True)
        return pdf_cache_dir
    
    # Default cache directory
    default_cache_dir = os.path.join(cache_base_dir, 'default_cache')
    os.makedirs(default_cache_dir, exist_ok=True)
    return default_cache_dir

def send_to_gemini_with_cache(content: List, cache_dir: Optional[str] = None,
                             pdf_name: str = None, prompt_version: str = None, 
                             image_size: int = None, questions_count: int = None) -> Optional[dict]:
    """
    Sends content to Gemini API with hash-based caching.
    Parses JSON response from model output.
    """
    # Dynamically determine cache directory if not provided
    if cache_dir is None:
        cache_dir = get_dynamic_cache_dir(pdf_name)
    
    # Get model and model name
    model = get_model()
    model_name = get_model_name()
    
    # Create request hash for caching (handles content separation internally)
    request_hash = create_request_hash(content, model_name)
    
    # Check for cached response if cache_dir is provided
    print(f"Checking for cached response in {cache_dir}...")
    cached_response = load_cached_response(cache_dir, request_hash)
    if cached_response:
        print(f"Using cached response (saved {cached_response.get('processing_time_seconds', 0):.2f}s)")
        return cached_response.get('response_data')
    
    # Make API call with timing
    start_time = time.time()
    try:
        print(f"Making API call to {model_name}...")
        response = model.generate_content(content)
        processing_time = time.time() - start_time
        
        # Process response
        raw = response.text.strip()
        cleaned = raw.strip('```json').strip('```').strip()
        parsed = json.loads(cleaned)
        
        print(f"API call completed in {processing_time:.2f}s")
        
        # Save to cache
        save_cached_response(
            cache_dir=cache_dir,
            request_hash=request_hash,
            response_data=parsed,
            processing_time=processing_time,
            pdf_name=pdf_name,
            prompt_version=prompt_version,
            image_size=image_size,
            questions_count=questions_count
        )
        
        return parsed
        
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"Failed to process content after {processing_time:.2f}s: {e}")
        return None

def send_simple_request(content: List) -> Optional[dict]:
    """Simple Gemini API call without caching."""
    model = get_model()
    model_name = get_model_name()
    
    try:
        print(f"Making simple API call to {model_name}...")
        response = model.generate_content(content)
        
        # Process response
        raw = response.text.strip()
        cleaned = raw.strip('```json').strip('```').strip()
        parsed = json.loads(cleaned)
        
        print(f"Simple API call completed")
        return parsed
        
    except Exception as e:
        print(f"Simple API call failed: {e}")
        return None 