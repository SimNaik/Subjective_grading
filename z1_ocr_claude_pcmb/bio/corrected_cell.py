# 🚀 CLAUDE WITH GEMINI PREPROCESSING - BEST OF BOTH WORLDS (CORRECTED)
import sys, os, time, json, shutil, pandas as pd
from dotenv import load_dotenv
import glob
import hashlib
import base64
import requests
from typing import List, Optional, Dict, Any
import subprocess
import re

print("🚀 CLAUDE SONNET 4 WITH GEMINI PREPROCESSING - CORRECTED VERSION!")
print("=" * 70)

# === SETUP ===
physics_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr_claude_pcmb/Bio"
parent_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading"
solution_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement"

# CORRECTED CSV PATH
hw_solution_with_qb_meta_csv = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr_claude_pcmb/hw_df_with_solutions_and_questions.csv"

# PDF DIRECTORY TO PROCESS
PDF_DIRECTORY = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr_claude_pcmb/Bio/bio_Gemini/bio"

# Claude Vertex AI Configuration
CLAUDE_CONFIG = {
    "endpoint": "us-east5-aiplatform.googleapis.com",
    "location_id": "us-east5", 
    "project_id": "llm-sandbox-426711",
    "model_id": "claude-sonnet-4",
    "method": "rawPredict"
}

load_dotenv(os.path.join(solution_dir, ".env"))
sys.path.insert(0, physics_dir)
sys.path.insert(1, parent_dir)

class MockST:
    def __init__(self): self.secrets = {'GOOGLE_GEMINI_API': os.getenv('GOOGLE_GEMINI_API', '')}
    def error(self, m): print(f'❌ {m}')
    def info(self, m): print(f'ℹ️  {m}')
    def warning(self, m): print(f'⚠️  {m}')
    def success(self, m): print(f'✅ {m}')
sys.modules['streamlit'] = MockST()

# === IMPORT GEMINI PREPROCESSING FUNCTIONS FROM OCR DIRECTORY ===
try:
    # Add OCR directory to path for imports
    ocr_dir = os.path.join(parent_dir, 'ocr')
    sys.path.insert(0, ocr_dir)
    
    # Import from the proper OCR modules
    from processors import ImageProcessor  # From ocr/processors.py
    from config import create_pdf_output_structure, IMAGE_RESIZE_DIM  # From ocr/config.py
    from utils.cache_utils import create_pdf_request_hash, load_cached_response, save_cached_response  # From ocr/utils/cache_utils.py
    from results import ResultsManager  # From ocr/results.py
    print("✅ All Gemini preprocessing functions imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import Gemini functions: {e}")
    print("Please ensure processors.py, config.py, etc. are available in the ocr directory")

# === SETUP PROMPT STORE ===
print("📝 Loading prompt store...")
ocr_dir = os.path.join(parent_dir, 'ocr')
sys.path.insert(0, ocr_dir)

try:
    import prompt_store as ps
    print("✅ Prompt store imported successfully")
    if hasattr(ps, 'v13'):
        print("✅ v13 prompt found in prompt store")
    else:
        print("❌ v13 prompt not found in prompt store")
        sys.exit(1)
except ImportError as e:
    print(f"❌ CRITICAL: Failed to import prompt store from {ocr_dir}")
    sys.exit(1)
