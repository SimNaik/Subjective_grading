#!/usr/bin/env python3
"""
Assessment OCR Data Organizer
Copies PDF folders from cache_2 and adds corresponding assessment data
"""

import json
import shutil
from pathlib import Path

# Paths
CACHE_2_DIR = Path("/Users/simrannaik/Desktop/subjective_grading/data/iteration_2/cache_2")
ASSESSMENT_FILE = Path("/Users/simrannaik/Desktop/subjective_grading/temp/assessment_results/assessment_results_assessment_v22_simran.json")
OUTPUT_DIR = Path("/Users/simrannaik/Desktop/subjective_grading/data/stepwise_images/source")

def main():
    print("=" * 80)
    print("ASSESSMENT OCR DATA ORGANIZER")
    print("=" * 80)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    
    # Load assessment results
    print(f"\n📄 Loading assessment results from: {ASSESSMENT_FILE}")
    with open(ASSESSMENT_FILE, 'r') as f:
        assessment_data = json.load(f)
    
    print(f"   ✅ Loaded {len(assessment_data)} assessment records")
    
    # Group assessments by pdf_name
    assessments_by_pdf = {}
    for item in assessment_data:
        metadata = item.get('metadata', {})
        pdf_name = metadata.get('pdf_name', '')
        
        if pdf_name:
            # Normalize pdf_name (remove .pdf extension for matching)
            pdf_name_normalized = pdf_name.replace('.pdf', '')
            
            if pdf_name_normalized not in assessments_by_pdf:
                assessments_by_pdf[pdf_name_normalized] = []
            
            assessments_by_pdf[pdf_name_normalized].append(item)
    
    print(f"   📊 Found assessments for {len(assessments_by_pdf)} unique PDFs")
    
    # Get all PDF folders from cache_2 (excluding Sample*)
    pdf_folders = [f for f in CACHE_2_DIR.iterdir() 
                   if f.is_dir() and not f.name.startswith("Sample")]
    
    print(f"\n📂 Found {len(pdf_folders)} PDF folders in cache_2")
    
    # Process each PDF folder
    processed_count = 0
    skipped_count = 0
    
    print(f"\n🔄 Processing PDF folders...\n")
    
    for pdf_folder in sorted(pdf_folders):
        pdf_name = pdf_folder.name.replace('.pdf', '')
        
        # Check if this PDF has assessment data
        if pdf_name in assessments_by_pdf:
            assessments = assessments_by_pdf[pdf_name]
            
            # Create destination folder
            dest_folder = OUTPUT_DIR / pdf_folder.name
            
            # Copy the entire PDF folder
            if dest_folder.exists():
                shutil.rmtree(dest_folder)  # Remove if exists
            
            shutil.copytree(pdf_folder, dest_folder)
            
            # Create assessment JSON file
            assessment_json_name = f"{pdf_name}_assessment_v22.json"
            assessment_json_path = dest_folder / assessment_json_name
            
            # Save assessments to JSON
            with open(assessment_json_path, 'w') as f:
                json.dump(assessments, f, indent=2)
            
            processed_count += 1
            print(f"✅ {processed_count}. {pdf_folder.name}")
            print(f"   📊 {len(assessments)} assessment(s) saved to {assessment_json_name}")
            
        else:
            skipped_count += 1
            if skipped_count <= 5:  # Show first 5 skipped
                print(f"⏭️  {pdf_folder.name}: No assessment data found")
    
    if skipped_count > 5:
        print(f"⏭️  ... and {skipped_count - 5} more PDFs skipped (no assessment data)")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Processed: {processed_count} PDFs")
    print(f"⏭️  Skipped: {skipped_count} PDFs (no assessment data)")
    print(f"📁 Output: {OUTPUT_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()
