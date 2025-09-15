import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Required paths for SubjectiveAssessment
pdf_dir = str(DATA_DIR / "pdfs")
image_dir = str(DATA_DIR / "images") 
cache_dir = str(DATA_DIR / "ocr_cache")
ocr_output_dir = str(DATA_DIR / "ocr_files")
hw_solution_with_qb_meta_csv = str(DATA_DIR / "class_10_pcmb_with_qb_meata.csv")

# PDF download configuration
PDF_BASE_URL = "https://dvvwf08ea9qan.cloudfront.net/137/student/testSubject/pdf/"

# OCR Configuration
OCR_CONFIG = {
    "default_cache_dir": cache_dir,
    "default_prompt_version": "v10",
    "max_pdf_pages": 50,
    "confidence_threshold": 0.8,
    "image_resize_dim": 1536,
    "cache_enabled": True,
    "max_concurrent_requests": 4,
    "clean_html_content": False  # False = preserve rich HTML content, True = strip HTML tags
}

# Create directories if they don't exist
for dir_path in [DATA_DIR, pdf_dir, image_dir, cache_dir, ocr_output_dir]:
    Path(dir_path).mkdir(parents=True, exist_ok=True) 