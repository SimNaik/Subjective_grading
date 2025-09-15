#!/usr/bin/env python3
"""
Token Usage Estimator for Claude Sonnet 4 OCR Processing
Estimates token usage for your PDF processing pipeline
"""

import os
import json
import glob
from pathlib import Path
import tiktoken

def estimate_text_tokens(text):
    """Estimate tokens for text using tiktoken (approximation for Claude)"""
    try:
        # Use OpenAI's tokenizer as approximation (Claude tokens are similar)
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(str(text)))
    except:
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(str(text)) // 4

def estimate_image_tokens(image_size_mb):
    """Estimate tokens for images (Claude Sonnet 4 vision)"""
    # Claude vision models typically use ~1000-2000 tokens per image
    # Larger images use more tokens
    if image_size_mb < 0.1:
        return 1000  # Small image
    elif image_size_mb < 0.5:
        return 1500  # Medium image  
    else:
        return 2000  # Large image

def analyze_existing_results(output_dir):
    """Analyze existing JSON outputs to understand actual token usage"""
    results = []
    
    json_pattern = os.path.join(output_dir, "**/json/output.json")
    json_files = glob.glob(json_pattern, recursive=True)
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            pdf_name = Path(json_file).parent.parent.name
            
            # Estimate tokens for this output
            total_text = json.dumps(data)
            estimated_tokens = estimate_text_tokens(total_text)
            
            results.append({
                'pdf_name': pdf_name,
                'questions_count': len(data) if isinstance(data, list) else 1,
                'output_tokens': estimated_tokens,
                'output_size_kb': len(total_text) / 1024
            })
            
        except Exception as e:
            print(f"Error analyzing {json_file}: {e}")
    
    return results

def estimate_pdf_processing_tokens(pdf_dir, questions_per_pdf=35, pages_per_pdf=15):
    """Estimate token usage for processing PDFs"""
    
    print(f"🔍 Analyzing PDFs in: {pdf_dir}")
    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found!")
        return
    
    print(f"📋 Found {len(pdf_files)} PDF files")
    
    # Estimate per PDF
    prompt_tokens = estimate_text_tokens("v13 prompt instructions (OCR)")  # ~500 tokens
    questions_tokens = questions_per_pdf * 50  # ~50 tokens per question
    separator_tokens = 10  # Small overhead
    images_tokens = pages_per_pdf * 1500  # ~1500 tokens per image
    
    input_tokens_per_pdf = prompt_tokens + questions_tokens + separator_tokens + images_tokens
    output_tokens_per_pdf = questions_per_pdf * 120  # ~120 tokens per question response
    total_tokens_per_pdf = input_tokens_per_pdf + output_tokens_per_pdf
    
    # Total for all PDFs
    total_input_tokens = input_tokens_per_pdf * len(pdf_files)
    total_output_tokens = output_tokens_per_pdf * len(pdf_files)
    total_tokens = total_input_tokens + total_output_tokens
    
    return {
        'pdf_count': len(pdf_files),
        'pdf_files': [os.path.basename(f) for f in pdf_files],
        'per_pdf': {
            'input_tokens': input_tokens_per_pdf,
            'output_tokens': output_tokens_per_pdf,
            'total_tokens': total_tokens_per_pdf,
            'estimated_questions': questions_per_pdf,
            'estimated_pages': pages_per_pdf
        },
        'total': {
            'input_tokens': total_input_tokens,
            'output_tokens': total_output_tokens,
            'total_tokens': total_tokens
        }
    }

def estimate_costs(tokens, model="claude-sonnet-4"):
    """Estimate costs based on token usage"""
    # Approximate pricing (check current Vertex AI pricing)
    pricing = {
        "claude-sonnet-4": {
            "input": 0.000015,   # $15 per 1M input tokens
            "output": 0.000075   # $75 per 1M output tokens
        }
    }
    
    if model in pricing:
        input_cost = (tokens['total']['input_tokens'] / 1000000) * pricing[model]['input']
        output_cost = (tokens['total']['output_tokens'] / 1000000) * pricing[model]['output']
        total_cost = input_cost + output_cost
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'pricing_model': model
        }
    
    return None

def main():
    # Configuration
    PDF_DIR = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr_claude_pcmb/maths/maths_Gemini/maths"
    OUTPUT_DIR = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr_claude_pcmb/maths/output"
    
    print("🔢 CLAUDE SONNET 4 TOKEN USAGE ESTIMATOR")
    print("=" * 60)
    
    # Analyze existing results first
    print("\n📊 ANALYZING EXISTING RESULTS...")
    existing_results = analyze_existing_results(OUTPUT_DIR)
    
    if existing_results:
        print(f"✅ Found {len(existing_results)} processed PDFs")
        for result in existing_results:
            print(f"  📄 {result['pdf_name']}: {result['questions_count']} questions → {result['output_tokens']:,} tokens")
        
        avg_output_tokens = sum(r['output_tokens'] for r in existing_results) / len(existing_results)
        avg_questions = sum(r['questions_count'] for r in existing_results) / len(existing_results)
        print(f"\n📈 Average: {avg_questions:.1f} questions → {avg_output_tokens:,.0f} output tokens")
        
        # Use actual data for estimation
        questions_per_pdf = int(avg_questions)
        output_tokens_per_question = int(avg_output_tokens / avg_questions)
    else:
        print("⚠️  No existing results found, using estimates")
        questions_per_pdf = 35
        output_tokens_per_question = 120
    
    # Estimate for all PDFs
    print(f"\n🎯 ESTIMATING TOKEN USAGE FOR ALL PDFs...")
    estimation = estimate_pdf_processing_tokens(PDF_DIR, questions_per_pdf)
    
    if estimation:
        print(f"\n📋 ESTIMATION RESULTS:")
        print(f"{'='*60}")
        print(f"📁 PDF files to process: {estimation['pdf_count']}")
        print(f"\n📄 PER PDF ESTIMATE:")
        print(f"  Input tokens:  {estimation['per_pdf']['input_tokens']:,}")
        print(f"  Output tokens: {estimation['per_pdf']['output_tokens']:,}")
        print(f"  Total tokens:  {estimation['per_pdf']['total_tokens']:,}")
        print(f"  Questions:     {estimation['per_pdf']['estimated_questions']}")
        print(f"  Pages:         {estimation['per_pdf']['estimated_pages']}")
        
        print(f"\n🎯 TOTAL FOR ALL {estimation['pdf_count']} PDFs:")
        print(f"  Input tokens:  {estimation['total']['input_tokens']:,}")
        print(f"  Output tokens: {estimation['total']['output_tokens']:,}")
        print(f"  Total tokens:  {estimation['total']['total_tokens']:,}")
        
        # Cost estimation
        costs = estimate_costs(estimation)
        if costs:
            print(f"\n💰 ESTIMATED COSTS:")
            print(f"  Input cost:  ${costs['input_cost']:.3f}")
            print(f"  Output cost: ${costs['output_cost']:.3f}")
            print(f"  Total cost:  ${costs['total_cost']:.3f}")
        
        # Max tokens recommendation
        max_tokens_needed = estimation['per_pdf']['output_tokens']
        recommended_max_tokens = int(max_tokens_needed * 1.3)  # 30% buffer
        
        print(f"\n🔧 CONFIGURATION RECOMMENDATIONS:")
        print(f"  Current max_tokens: 8,192")
        print(f"  Estimated need:     {max_tokens_needed:,}")
        print(f"  Recommended:        {recommended_max_tokens:,}")
        
        if recommended_max_tokens > 8192:
            print(f"  ⚠️  Consider increasing max_tokens to {recommended_max_tokens:,}")
        else:
            print(f"  ✅ Current max_tokens (8,192) is sufficient")
        
        print(f"\n📂 PDF FILES TO PROCESS:")
        for i, pdf_file in enumerate(estimation['pdf_files'], 1):
            print(f"  {i:2d}. {pdf_file}")

if __name__ == "__main__":
    main()
