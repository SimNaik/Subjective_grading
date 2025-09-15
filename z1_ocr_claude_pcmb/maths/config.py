import os
from pathlib import Path

def get_dynamic_base_dir():
    """
    Dynamically determine the base directory for creating output folders.
    Prioritizes the current script/notebook location.
    """
    try:
        # For scripts
        base_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # Fallback for interactive environments like Jupyter
        base_dir = os.getcwd()
    
    return base_dir

def create_pdf_output_structure(pdf_name):
    """
    Create a nested output directory structure for a specific PDF.
    
    Args:
        pdf_name (str): Name of the PDF file (without extension)
    
    Returns:
        dict: Paths for different output types
    """
    # Base output directory
    base_output_dir = Path(get_dynamic_base_dir()) / "output"
    
    # PDF-specific output directory
    pdf_output_dir = base_output_dir / pdf_name

    # Subdirectories for different output types
    output_paths = {
        'base': str(pdf_output_dir),
        'json': str(pdf_output_dir / "json"),
        'cache': str(pdf_output_dir / "cache"),
        'images': str(pdf_output_dir / "images")
    }

    # Create all directories
    for path in output_paths.values():
        Path(path).mkdir(parents=True, exist_ok=True)

    return output_paths

# Base paths
BASE_DIR = Path(get_dynamic_base_dir())

# Global output configuration
OUTPUT_BASE_DIR = BASE_DIR / "output"
OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)

# Default paths (will be overridden dynamically)
pdf_dir = str(BASE_DIR / "pdfs")
image_dir = str(OUTPUT_BASE_DIR / "OUTPUT_JSON")
cache_dir = str(OUTPUT_BASE_DIR / "ocr_cache")
ocr_output_dir = str(OUTPUT_BASE_DIR / "ocr_files")
hw_solution_with_qb_meta_csv = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr/hw_df_with_solutions_and_questions.csv"

# Create default directories
for dir_path in [pdf_dir, image_dir, cache_dir, ocr_output_dir]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

# PDF download configuration
PDF_BASE_URL = "https://dvvwf08ea9qan.cloudfront.net/137/student/testSubject/pdf/"

# OCR Configuration
OCR_CONFIG = {
    "default_cache_dir": cache_dir,
    "default_prompt_version": "v13",
    "max_pdf_pages": 50,
    "confidence_threshold": 0.8,
    "image_resize_dim": 1536,
    "cache_enabled": True,
    "max_concurrent_requests": 4,
    "clean_html_content": False  # False = preserve rich HTML content, True = strip HTML tags
}

# Legacy constants for backward compatibility
IMAGE_RESIZE_DIM = OCR_CONFIG["image_resize_dim"]
RESIZED_IMAGE_PATTERN = "{pdf_name}_DIM_{dim}_PAGE_{page_num}.jpeg"

print(f"📁 Created base output directory: {OUTPUT_BASE_DIR}")
print(f"📁 Created default directories in: {OUTPUT_BASE_DIR}") 