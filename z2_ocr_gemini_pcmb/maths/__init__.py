# Main OCR module providing unified interface
from .gemini import ocr_pdf, ocr_with_questions
from .client import get_model, get_model_name, GeminiClient
from .processors import process_images_to_resized_objects, ImageProcessor
from .api_handler import send_to_gemini_with_cache, send_simple_request
from .results import ResultsManager
from . import prompt_store
from . import config

# Utility functions
from .utils.cache_utils import create_request_hash, create_pdf_request_hash, convert_questions_to_binary, load_cached_response, save_cached_response
from .utils.image_utils import resize_image

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
from .prompt_store import v1, v2, v3, v5, v6, v8, v9, v10, v11, v12 