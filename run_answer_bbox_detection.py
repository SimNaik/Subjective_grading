#!/usr/bin/env python3
"""
Answer Bounding Box Detection Runner
===================================

This script runs the answer bounding box detection system that:
1. Reads question-level solutions from JSON files
2. Extracts page numbers and answer numbers
3. Finds corresponding page images in cache
4. Uses Gemini to detect bounding boxes for specific answers
5. Only processes pages where page_number == answer_number

Usage:
    python run_answer_bbox_detection.py --test     # Test single question
    python run_answer_bbox_detection.py --full     # Process all questions
    python run_answer_bbox_detection.py --question 1306848  # Process specific question
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ocr.answer_bbox_detector import (
    process_question_solution_with_pdf, 
    process_all_question_solutions,
    find_all_question_solutions,
    find_page_image
)

def test_single_question():
    """Test processing a single question solution"""
    
    cache_dir = "/Users/simrannaik/Desktop/subjective_grading/data/iteration_2/cache"
    output_dir = "/Users/simrannaik/Desktop/subjective_grading/data/answer_bbox_test"
    
    # Find all question solution files
    all_solution_files = find_all_question_solutions(cache_dir)
    
    if not all_solution_files:
        print("❌ No solution files found for testing")
        return False
    
    # Use the first solution file for testing
    test_info = all_solution_files[0]
    test_file = test_info['solution_file']
    pdf_name = test_info['pdf_name']
    question_number = test_info['question_number']
    
    print(f"🧪 Testing with: {pdf_name}/question_{question_number}")
    
    # Process the test file
    result = process_question_solution_with_pdf(test_file, pdf_name, cache_dir, output_dir)
    
    if result:
        print(f"✅ Test successful! Processed {len(result)} pages")
        return True
    else:
        print("❌ Test failed")
        return False

def process_specific_question(pdf_name, question_number):
    """Process a specific question by PDF name and question number"""
    
    cache_dir = "/Users/simrannaik/Desktop/subjective_grading/data/iteration_2/cache"
    output_dir = "/Users/simrannaik/Desktop/subjective_grading/data/answer_bbox_results"
    
    # Find the specific question file
    pdf_dir = Path(cache_dir) / pdf_name
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        return False
    
    question_file = pdf_dir / "question_level_solutions" / f"{question_number}.json"
    
    if not question_file.exists():
        print(f"❌ Question file not found: {question_file}")
        return False
    
    print(f"🎯 Processing question: {pdf_name}/question_{question_number}")
    
    # Process the specific question
    result = process_question_solution_with_pdf(question_file, pdf_name, cache_dir, output_dir)
    
    if result:
        print(f"✅ Successfully processed {pdf_name}/question_{question_number}")
        return True
    else:
        print(f"❌ Failed to process {pdf_name}/question_{question_number}")
        return False

def run_full_pipeline():
    """Run the full answer bounding box detection pipeline"""
    
    cache_dir = "/Users/simrannaik/Desktop/subjective_grading/data/iteration_2/cache"
    output_dir = "/Users/simrannaik/Desktop/subjective_grading/data/answer_bbox_results"
    
    print("🚀 Running full answer bounding box detection pipeline")
    
    # Process all questions from cache directory
    results = process_all_question_solutions(cache_dir, output_dir)
    
    if results:
        print(f"✅ Pipeline completed! Processed {len(results)} questions")
        return True
    else:
        print("❌ Pipeline failed")
        return False

def analyze_solutions():
    """Analyze solution files to understand the data"""
    
    cache_dir = "/Users/simrannaik/Desktop/subjective_grading/data/iteration_2/cache"
    
    # Find all question solution files
    all_solution_files = find_all_question_solutions(cache_dir)
    
    print(f"📊 Analyzing {len(all_solution_files)} solution files...")
    
    page_answer_matches = 0
    total_with_pages = 0
    answer_patterns = {}
    pdf_question_counts = {}
    
    # Analyze first 20 files
    for i, solution_info in enumerate(all_solution_files[:20]):
        try:
            solution_file = solution_info['solution_file']
            pdf_name = solution_info['pdf_name']
            question_number = solution_info['question_number']
            
            # Count questions per PDF
            pdf_question_counts[pdf_name] = pdf_question_counts.get(pdf_name, 0) + 1
            
            import json
            with open(solution_file, 'r') as f:
                data = json.load(f)
            
            solution_text = data.get("Solution", "")
            pages = data.get("pages", [])
            question_id = data.get("Question ID", question_number)
            
            if pages:
                total_with_pages += 1
                # Use question number from filename as answer number
                answer_num = int(question_number)
                
                answer_patterns[answer_num] = answer_patterns.get(answer_num, 0) + 1
                
                # Show answer and page information
                page_answer_matches += 1
                print(f"📄 {pdf_name}/Q{question_number}: Answer {answer_num}, Pages {pages}")
        
        except Exception as e:
            print(f"❌ Error analyzing {solution_file}: {e}")
    
    print(f"\n📈 Analysis Results:")
    print(f"   Total solution files found: {len(all_solution_files)}")
    print(f"   Total files with pages: {total_with_pages}")
    print(f"   Files processed: {page_answer_matches}")
    print(f"   Answer number distribution: {answer_patterns}")
    print(f"   Questions per PDF (sample): {dict(list(pdf_question_counts.items())[:5])}")

def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(description="Run answer bounding box detection")
    parser.add_argument("--test", action="store_true", help="Test with single question")
    parser.add_argument("--full", action="store_true", help="Process all questions")
    parser.add_argument("--question", type=str, help="Process specific question (format: pdf_name/question_number or just question_number)")
    parser.add_argument("--analyze", action="store_true", help="Analyze solution files")
    
    args = parser.parse_args()
    
    # Validate API key
    from dotenv import load_dotenv
    load_dotenv()
    if not os.getenv("GOOGLE_GEMINI_API"):
        print("❌ Error: GOOGLE_GEMINI_API not found in .env file")
        return False
    
    if args.test:
        print("🧪 Running single question test...")
        success = test_single_question()
    elif args.full:
        print("🚀 Running full pipeline...")
        success = run_full_pipeline()
    elif args.question:
        # Parse question argument as "pdf_name/question_number" or just "question_number"
        if '/' in args.question:
            pdf_name, question_number = args.question.split('/', 1)
            if not pdf_name.endswith('.pdf'):
                pdf_name += '.pdf'
        else:
            # If only question number provided, find it in any PDF
            cache_dir = "/Users/simrannaik/Desktop/subjective_grading/data/iteration_2/cache"
            all_solutions = find_all_question_solutions(cache_dir)
            matching_solutions = [s for s in all_solutions if s['question_number'] == args.question]
            
            if not matching_solutions:
                print(f"❌ Question {args.question} not found in any PDF")
                success = False
            elif len(matching_solutions) == 1:
                pdf_name = matching_solutions[0]['pdf_name']
                question_number = args.question
            else:
                print(f"❌ Question {args.question} found in multiple PDFs:")
                for sol in matching_solutions:
                    print(f"   - {sol['pdf_name']}")
                print("Please specify as: pdf_name/question_number")
                success = False
        
        if 'pdf_name' in locals() and 'question_number' in locals():
            print(f"🎯 Processing specific question: {pdf_name}/{question_number}")
            success = process_specific_question(pdf_name, question_number)
        else:
            success = False
    elif args.analyze:
        print("📊 Analyzing solution files...")
        analyze_solutions()
        success = True
    else:
        print("Please specify an option:")
        print("  --test      Test with single question")
        print("  --full      Process all questions")
        print("  --question  Process specific question ID")
        print("  --analyze   Analyze solution files")
        success = False
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
