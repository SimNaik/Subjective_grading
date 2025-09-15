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
physics_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr_claude_pcmb/maths"
parent_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading"
solution_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement"

# CORRECTED CSV PATH
hw_solution_with_qb_meta_csv = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr_claude_pcmb/hw_df_with_solutions_and_questions.csv"

# PDF DIRECTORY TO PROCESS
PDF_DIRECTORY = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr_claude_pcmb/maths/maths_Gemini/maths"

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

# === IMPORT GEMINI PREPROCESSING FUNCTIONS ===
try:
    # Import ALL the Gemini processing functions you love!
    from processors import ImageProcessor  # Your existing ImageProcessor
    from config import create_pdf_output_structure, IMAGE_RESIZE_DIM  # Your config
    from cache_utils import create_pdf_request_hash, load_cached_response, save_cached_response  # Your caching
    from results_manager import ResultsManager  # Your results manager
    print("✅ All Gemini preprocessing functions imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import Gemini functions: {e}")
    print("Please ensure processors.py, config.py, etc. are available")

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

# === CLAUDE API FUNCTIONS (ONLY THING THAT CHANGES) ===

def get_access_token():
    """Get Google Cloud access token using gcloud CLI"""
    try:
        result = subprocess.run(
            ['gcloud', 'auth', 'print-access-token'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get access token: {e}")
        return None

def convert_pil_image_to_base64(pil_image, max_size_mb=1.5):
    """Convert PIL Image to base64 (for Claude) with compression"""
    try:
        from PIL import Image
        import io
        
        # Convert to RGB if necessary
        if pil_image.mode in ('RGBA', 'LA', 'P'):
            pil_image = pil_image.convert('RGB')
        
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # Try different quality levels until under size limit
        for quality in [85, 70, 60, 50, 40]:
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            if buffer.tell() <= max_size_bytes:
                print(f"🔧 Compressed PIL image to quality {quality} ({buffer.tell()/1024/1024:.1f}MB)")
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # If still too large, resize
        print("🔧 Resizing PIL image...")
        width, height = pil_image.size
        scale_factor = 0.7  # Reduce by 30%
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        resized_image.save(buffer, format='JPEG', quality=70, optimize=True)
        
        print(f"✅ Resized to {new_width}x{new_height} ({buffer.tell()/1024/1024:.1f}MB)")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
    except Exception as e:
        print(f"❌ Failed to convert PIL image: {e}")
        return None

def create_claude_content_from_gemini_format(content_items):
    """Convert Gemini-style content (with PIL Images) to Claude format"""
    claude_content = []
    
    for item in content_items:
        if isinstance(item, str):
            # Text content - same as Gemini
            claude_content.append({
                "type": "text",
                "text": item
            })
        else:
            # Check if it's a PIL Image (Gemini format)
            try:
                from PIL import Image
                if isinstance(item, Image.Image):
                    # Convert PIL Image to base64 for Claude
                    base64_image = convert_pil_image_to_base64(item)
                    if base64_image:
                        claude_content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        })
            except ImportError:
                pass
    
    return claude_content

def robust_json_parser(raw_text):
    """
    Robust JSON parser with multiple fallback strategies
    """
    cleaned = raw_text.strip('```json').strip('```').strip()
    
    # Strategy 1: Direct JSON parsing
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"⚠️  Direct JSON parsing failed: {e}")
    
    # Strategy 2: Fix common JSON issues
    try:
        # Fix common formatting issues
        fixed_json = cleaned
        
        # Remove any BOM or weird characters at the start
        if fixed_json.startswith('\ufeff'):
            fixed_json = fixed_json[1:]
        
        # Fix unescaped quotes in strings
        lines = fixed_json.split('\n')
        fixed_lines = []
        
        for line in lines:
            # If line has uneven quotes, try to fix
            quote_count = line.count('"')
            if quote_count % 2 != 0 and not line.strip().endswith(','):
                # Try to add missing quote at the end of the line
                line = line.rstrip() + '"'
            fixed_lines.append(line)
        
        fixed_json = '\n'.join(fixed_lines)
        
        # Try parsing the fixed JSON
        return json.loads(fixed_json)
    except json.JSONDecodeError as e2:
        print(f"⚠️  JSON fix attempt failed: {e2}")
    
    # Strategy 3: Extract JSON from response if it's embedded
    try:
        # Look for JSON array or object patterns
        json_pattern = r'(\[.*\]|\{.*\})'
        matches = re.search(json_pattern, cleaned, re.DOTALL)
        if matches:
            potential_json = matches.group(1)
            return json.loads(potential_json)
        else:
            print("❌ No JSON pattern found in response")
    except json.JSONDecodeError as e3:
        print(f"⚠️  JSON extraction failed: {e3}")
    
    # Strategy 4: Try to repair truncated JSON
    try:
        # If JSON is truncated, try to close it
        fixed_json = cleaned
        
        # Handle truncated string values
        # If the JSON ends with incomplete string, close it properly
        if not fixed_json.rstrip().endswith((']', '}', '"')):
            # Find the last opening quote
            last_quote_pos = fixed_json.rfind('"')
            if last_quote_pos != -1:
                # Check if this quote is opening a string value (not closing)
                quotes_before = fixed_json[:last_quote_pos].count('"')
                if quotes_before % 2 == 1:  # Odd number means we have an opening quote
                    fixed_json += '"'  # Close the string
        
        # Count open braces/brackets
        open_braces = fixed_json.count('{') - fixed_json.count('}')
        open_brackets = fixed_json.count('[') - fixed_json.count(']')
        
        # Add missing closing characters
        fixed_json += '}' * open_braces
        fixed_json += ']' * open_brackets
        
        parsed = json.loads(fixed_json)
        print(f"✅ Successfully repaired truncated JSON - recovered {len(parsed)} questions")
        return parsed
    except json.JSONDecodeError as e4:
        print(f"⚠️  JSON repair failed: {e4}")
        
    # Strategy 5: Extract valid portion of JSON array
    try:
        # Try to extract complete questions from partial JSON
        print("🔧 Attempting to extract valid questions from truncated response...")
        
        # Find the last complete question object
        import re
        
        # Split by question objects and take only complete ones
        question_pattern = r'\{\s*"question_number":\s*\d+,.*?\}'
        questions = re.findall(question_pattern, cleaned, re.DOTALL)
        
        if questions:
            # Reconstruct valid JSON array
            valid_json = '[' + ','.join(questions) + ']'
            parsed = json.loads(valid_json)
            print(f"✅ Extracted {len(parsed)} complete questions from truncated response")
            return parsed
        else:
            print("❌ Could not extract any complete questions")
    except json.JSONDecodeError as e5:
        print(f"⚠️  Question extraction failed: {e5}")
    except Exception as e6:
        print(f"⚠️  Unexpected error in question extraction: {e6}")
    
    print(f"❌ All JSON parsing strategies failed")
    print(f"📄 FULL RAW RESPONSE (for debugging):")
    print("=" * 80)
    print(raw_text)
    print("=" * 80)
    return None

def send_to_claude_with_gemini_preprocessing(content: List, cache_dir: Optional[str] = None,
                                           pdf_name: str = None, prompt_version: str = None, 
                                           image_size: int = None, questions_count: int = None) -> Optional[dict]:
    """
    Send Gemini-preprocessed content to Claude API
    This replaces send_to_gemini_with_cache() but keeps the same interface!
    """
    
    # Use same caching logic as Gemini
    model_name = "claude-sonnet-4"
    request_hash = create_pdf_request_hash(
        pdf_file_path=pdf_name,
        prompt_text=content[0] if content else "",
        prompt_version=prompt_version,
        image_dimension=image_size or IMAGE_RESIZE_DIM,
        model_name=model_name,
        questions=None
    )
    
    # Check cache (same as Gemini)
    if cache_dir:
        cached_response = load_cached_response(cache_dir, request_hash)
        if cached_response:
            print(f"✅ Using cached response (saved {cached_response.get('processing_time_seconds', 0):.2f}s)")
            return cached_response.get('response_data')
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        print("❌ Failed to get access token")
        return None
    
    # Convert Gemini-style content to Claude format
    claude_content = create_claude_content_from_gemini_format(content)
    
    # Check total size
    total_size = sum(len(json.dumps(item).encode()) for item in claude_content) / (1024 * 1024)
    print(f"📊 Request size: {total_size:.1f}MB")
    
    if total_size > 25:
        print("⚠️  Request approaching 30MB limit!")
    
    # Prepare Claude request
    request_payload = {
        "anthropic_version": "vertex-2023-10-16",
        "stream": False,
        "max_tokens": 20000,  # ← Increased to handle longer responses
        "temperature": 0.1,
        "top_p": 0.95,
        "top_k": 40,
        "messages": [
            {
                "role": "user",
                "content": claude_content
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    url = f"https://{CLAUDE_CONFIG['endpoint']}/v1/projects/{CLAUDE_CONFIG['project_id']}/locations/{CLAUDE_CONFIG['location_id']}/publishers/anthropic/models/{CLAUDE_CONFIG['model_id']}:{CLAUDE_CONFIG['method']}"
    
    # Make API call (same timing as Gemini)
    start_time = time.time()
    try:
        print(f"🤖 Making API call to Claude Sonnet 4...")
        response = requests.post(url, headers=headers, json=request_payload, timeout=180)
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            response_data = response.json()
            
            if 'content' in response_data and len(response_data['content']) > 0:
                raw_text = response_data['content'][0]['text']
                
                # Use robust JSON parser - FIXED!
                parsed = robust_json_parser(raw_text)
                
                if parsed:
                    print(f"✅ API call completed in {processing_time:.2f}s")
                    
                    # Save to cache (same as Gemini)
                    if cache_dir:
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
                else:
                    return None
            else:
                print("❌ No content in Claude response")
                return None
        else:
            print(f"❌ Claude API error ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ Failed to process content with Claude after {processing_time:.2f}s: {e}")
        return None

# === USE ALL YOUR EXISTING GEMINI FUNCTIONS ===

# Import HTML cleaner (same as before)
try:
    from html_text_cleaner import clean_html_to_text as extract_text_from_html
    print("✅ HTML cleaner imported successfully")
except ImportError as e:
    def extract_text_from_html(html_text):
        import re
        if not html_text:
            return html_text
        clean = re.sub(r'<[^>]+>', '', html_text)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

# Keep ALL your existing helper functions exactly as they are
def remove_prefix(filename):
    """Remove numeric prefix like 01_, 02_, etc. from filename"""
    if '_' in filename:
        parts = filename.split('_', 1)
        if parts[0].isdigit():
            return parts[1]
    return filename

def extract_pdf_name_from_url(url):
    """Extract PDF name from UPLOADED_ANS URL"""
    if pd.isna(url) or not isinstance(url, str):
        return None
    filename = url.split('/')[-1]
    if filename.endswith('.pdf'):
        filename = filename[:-4]
    return filename

def clean_escaped_html(text):
    """Clean both regular HTML and escaped HTML tags"""
    if not text:
        return text
    text = text.replace('\\/', '/')
    cleaned = extract_text_from_html(text)
    return cleaned

def extract_question_from_json_content(json_content):
    """Extract and clean question text from JSON content"""
    try:
        data = json.loads(json_content)
        if isinstance(data, list) and len(data) > 0:
            question_data = data[0]
        else:
            question_data = data
        
        question_text = None
        if 'questionStem' in question_data and 'text' in question_data['questionStem']:
            question_text = question_data['questionStem']['text']
        
        if question_text:
            if question_text.startswith('"') and question_text.endswith('"'):
                question_text = question_text[1:-1]
            cleaned_text = clean_escaped_html(question_text)
            return cleaned_text
        
        return None
    except Exception as e:
        print(f"❌ Error extracting question: {e}")
        return None

def load_questions_for_pdf_with_json_parsing(pdf_name, csv_path):
    """Load questions from CSV, parse JSON content, and clean HTML"""
    try:
        if not hasattr(load_questions_for_pdf_with_json_parsing, 'cached_df'):
            print(f"📊 Loading CSV: {csv_path}")
            load_questions_for_pdf_with_json_parsing.cached_df = pd.read_csv(csv_path, low_memory=False)
            print(f"✅ CSV loaded: {len(load_questions_for_pdf_with_json_parsing.cached_df)} rows")
            
            load_questions_for_pdf_with_json_parsing.cached_df['pdf_name_extracted'] = \
                load_questions_for_pdf_with_json_parsing.cached_df['UPLOADED_ANS'].apply(extract_pdf_name_from_url)
        
        df = load_questions_for_pdf_with_json_parsing.cached_df
        base_pdf_name = remove_prefix(pdf_name.replace('.pdf', ''))
        pdf_df = df[df['pdf_name_extracted'].str.contains(base_pdf_name, na=False)]
        
        if len(pdf_df) == 0:
            print(f"⚠️  No questions found for PDF: {base_pdf_name}")
            return []
        
        print(f"✅ Found {len(pdf_df)} rows for PDF: {base_pdf_name}")
        
        questions = []
        for idx, row in pdf_df.iterrows():
            raw_content = None
            if pd.notna(row.get('content')):
                raw_content = str(row['content'])
            elif pd.notna(row.get('textsolutions')):
                raw_content = str(row['textsolutions'])
            
            if raw_content:
                cleaned_question = extract_question_from_json_content(raw_content)
                if cleaned_question and cleaned_question.strip():
                    questions.append(cleaned_question)
        
        print(f"📝 Extracted {len(questions)} cleaned questions for {pdf_name}")
        return questions
        
    except Exception as e:
        print(f"❌ Error loading questions for {pdf_name}: {e}")
        return []

def get_model_name():
    return "claude-sonnet-4"

# === CLAUDE OCR FUNCTIONS (USING GEMINI PREPROCESSING) ===

def ocr_pdf_claude_with_gemini_preprocessing(pdf_file_path: str, output_folder: str, cache_dir: Optional[str], 
                                           prompt_version: str) -> Optional[dict]:
    """
    EXACT same interface as Gemini ocr_pdf, but sends to Claude at the end!
    """
    # Get prompt (same as Gemini)
    prompt = getattr(ps, prompt_version)
    model_name = get_model_name()
    pdf_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
    
    # Create output structure (same as Gemini)
    pdf_output_paths = create_pdf_output_structure(pdf_name)
    output_folder = pdf_output_paths['images']
    cache_dir = pdf_output_paths['cache']
    
    # Initialize processors (SAME as Gemini - your existing ImageProcessor!)
    image_processor = ImageProcessor(output_folder)
    results_manager = ResultsManager(pdf_output_paths['json'])
    
    # Process PDF to images (SAME as Gemini - returns PIL Images!)
    page_images = image_processor.process_pdf(pdf_file_path)
    
    # Build content list (SAME as Gemini format!)
    content = [prompt]
    if page_images:
        content.extend(page_images)  # PIL Images, same as Gemini!
    
    # Send to Claude with Gemini preprocessing (ONLY this line changes!)
    print(f"🤖 Processing with Claude Sonnet 4 using Gemini preprocessing (prompt: {prompt_version})...")
    results = send_to_claude_with_gemini_preprocessing(
        content=content,
        cache_dir=cache_dir,
        pdf_name=pdf_name,
        prompt_version=prompt_version,
        image_size=IMAGE_RESIZE_DIM
    )
    
    # Save results (same as Gemini)
    if results:
        results_manager.save_pdf_results(results)
        return results
    else:
        print("❌ No results from Claude OCR")
        return None

def ocr_with_questions_claude_with_gemini_preprocessing(questions: List[str], pdf_file_path: str, output_folder: str, 
                                                      cache_dir: Optional[str], prompt_version: str) -> Optional[dict]:
    """
    EXACT same interface as Gemini ocr_with_questions, but sends to Claude!
    """
    # Get prompt (same as Gemini)
    prompt = getattr(ps, prompt_version)
    pdf_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
    
    # Create output structure (same as Gemini)
    pdf_output_paths = create_pdf_output_structure(pdf_name)
    output_folder = pdf_output_paths['images']
    cache_dir = pdf_output_paths['cache']
    
    # Initialize processors (SAME as Gemini!)
    image_processor = ImageProcessor(output_folder)
    results_manager = ResultsManager(pdf_output_paths['json'])
    
    # Process images (SAME as Gemini - returns PIL Images!)
    hand_written_solutions = image_processor.process_pdf(pdf_file_path=pdf_file_path)
    
    print(f"🤖 Processing {len(questions)} questions with {len(hand_written_solutions)} solution images")
    
    # Build content list (SAME format as Gemini!)
    content = [prompt]
    if questions:
        content.extend(["# Question set : "] + questions + [" # Hand written solutions : "])
    if hand_written_solutions:
        content.extend(hand_written_solutions)  # PIL Images, same as Gemini!
    
    # Send to Claude with Gemini preprocessing (ONLY this changes!)
    print(f"🤖 Processing with Claude Sonnet 4 using Gemini preprocessing (prompt: {prompt_version})...")
    results = send_to_claude_with_gemini_preprocessing(
        content=content,
        cache_dir=cache_dir,
        pdf_name=pdf_name,
        prompt_version=prompt_version,
        image_size=IMAGE_RESIZE_DIM,
        questions_count=len(questions)
    )
    
    # Save results (same as Gemini)
    if results:
        results_manager.save_question_results(results)
        return results
    else:
        print("❌ No results from Claude OCR")
        return None

# === MAIN PROCESSING FUNCTIONS (ALMOST IDENTICAL TO GEMINI) ===

def process_single_pdf_with_questions(pdf_path, pdf_name):
    """Process a single PDF - SAME interface as Gemini version"""
    
    print(f"\n{'='*60}")
    print(f"🔧 Processing PDF: {pdf_name}")
    print(f"📄 Full path: {pdf_path}")
    
    # Load questions (same as Gemini)
    questions = load_questions_for_pdf_with_json_parsing(pdf_name, hw_solution_with_qb_meta_csv)
    
    if not questions:
        print("⚠️  No questions found, falling back to basic OCR")
        result = ocr_pdf_claude_with_gemini_preprocessing(pdf_path, physics_dir, None, "v13")
    else:
        print(f"🎯 Processing with {len(questions)} cleaned questions")
        print(f"📝 Question preview: {questions[0][:80]}..." if questions else "")
            
        # Use Claude with Gemini preprocessing
        result = ocr_with_questions_claude_with_gemini_preprocessing(
            questions=questions,
            pdf_file_path=pdf_path,
            output_folder=physics_dir,
            cache_dir=None,
            prompt_version="v13"
        )
    
    # Rest is IDENTICAL to Gemini processing...
    if result:
        pdf_base_name = pdf_name.replace('.pdf', '')
        for search_pattern in [
            f"{physics_dir}/output/{pdf_base_name}/json/output.json",
            f"{physics_dir}/output/output.json",
            f"{physics_dir}/output/OUTPUT_JSON/output.json"
        ]:
            if os.path.exists(search_pattern):
                target_dir = f"{physics_dir}/output/batch_results/{pdf_base_name}"
                os.makedirs(target_dir, exist_ok=True)
                target_path = f"{target_dir}/output.json"
                
                shutil.copy2(search_pattern, target_path)
                print(f"📄 Output saved to: {target_path}")
                
                with open(target_path, 'r') as f:
                    data = json.load(f)
                    print(f"✅ Success: {len(data)} questions processed for {pdf_name}")
                    
                    clean_count = 0
                    for item in data:
                        if 'question_text' in item:
                            if not any(tag in item['question_text'] for tag in ['</', '<div', '<strong', '<\/div', '<\/strong']):
                                clean_count += 1
                    
                    print(f"🧹 {clean_count}/{len(data)} questions are fully cleaned")
                    
                return True
        
        print(f"⚠️  Output file not found for {pdf_name}")
        return False
    else:
        print(f"❌ OCR processing failed for {pdf_name}")
        return False

def process_pdf_directory(pdf_directory):
    """Process all PDF files - SAME as Gemini version"""
    
    print(f"\n🎯 STARTING BATCH PDF PROCESSING WITH CLAUDE + GEMINI PREPROCESSING...")
    print(f"📁 Directory: {pdf_directory}")
    
    pdf_pattern = os.path.join(pdf_directory, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_directory}")
        return
    
    print(f"📋 Found {len(pdf_files)} PDF files to process")
    
    successful = 0
    failed = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        pdf_name = os.path.basename(pdf_path)
        print(f"\n🔄 Processing {i}/{len(pdf_files)}: {pdf_name}")
        
        try:
            success = process_single_pdf_with_questions(pdf_path, pdf_name)
            if success:
                successful += 1
                print(f"✅ Successfully processed {pdf_name}")
            else:
                failed += 1
                print(f"❌ Failed to process {pdf_name}")
        except Exception as e:
            failed += 1
            print(f"❌ Error processing {pdf_name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"🏁 BATCH PROCESSING COMPLETE WITH CLAUDE + GEMINI PREPROCESSING!")
    print(f"📊 Results:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Total files: {len(pdf_files)}")
    print(f"   📍 Results saved in: {physics_dir}/output/batch_results/")

# === EXECUTION ===
if __name__ == "__main__":
    print(f"📊 CSV: {os.path.basename(hw_solution_with_qb_meta_csv)}")
    print(f"🤖 Model: Claude Sonnet 4 with Gemini Preprocessing")
    print(f"🔗 Endpoint: {CLAUDE_CONFIG['endpoint']}")
    
    # Verify authentication
    token = get_access_token()
    if token:
        print("✅ Google Cloud authentication successful")
    else:
        print("❌ Google Cloud authentication failed")
        exit(1)
    
    # Process entire PDF directory
    process_pdf_directory(PDF_DIRECTORY)
    
    print(f"\n🏁 ALL PROCESSING COMPLETE WITH CLAUDE + GEMINI PREPROCESSING!")
