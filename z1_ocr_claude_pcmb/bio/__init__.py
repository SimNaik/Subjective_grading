# Main OCR module providing unified interface
import os
import sys

# Add parent directory to access main ocr module
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(1, parent_dir)

# Import from local modules
from .gemini import ocr_pdf, ocr_with_questions
from .processors import process_images_to_resized_objects, ImageProcessor
from .api_handler import send_to_gemini_with_cache, send_simple_request
from . import config

# Import from main OCR module 
from ocr.client import get_model, get_model_name, GeminiClient
from ocr.results import ResultsManager
from ocr import prompt_store

# Utility functions from main OCR module
from ocr.utils.cache_utils import create_request_hash, create_pdf_request_hash, convert_questions_to_binary, load_cached_response, save_cached_response
from ocr.utils.image_utils import resize_image

__version__ = "2.0.0"

__all__ = [
    # Core workflow functions
    'ocr_pdf',
    'ocr_with_questions',
    
    # Main classes
    'GeminiClient',
    'ImageProcessor',
    'ResultsManager',
    
    # API functions
    'send_to_gemini_with_cache',
    'send_simple_request',
    
    # Utility functions
    'process_images_to_resized_objects',
    'get_model',
    'get_model_name',
    'create_request_hash',
    'create_pdf_request_hash',
    'convert_questions_to_binary',
    'load_cached_response',
    'save_cached_response',
    'resize_image',
    
    # Modules
    'prompt_store',
    'config',
]

# Quick access to commonly used prompts
from ocr.prompt_store import v1, v2, v3, v5, v6, v8, v9, v10, v11, v12, v13, v15 