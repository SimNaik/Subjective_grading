#!/usr/bin/env python3
"""
Joined Student-Faculty OCR Generator
Creates student_joined_ocr.json files for each PDF folder in source
"""

import json
import pandas as pd
from pathlib import Path

# Paths
SOURCE_DIR = Path("/Users/simrannaik/Desktop/subjective_grading/data/stepwise_images/source")
CSV_FILE = Path("/Users/simrannaik/Desktop/subjective_grading/data/iteration_2/student_solutions_joined_with_faculty_solutions.csv")

def main():
    print("=" * 80)
    print("JOINED STUDENT-FACULTY OCR GENERATOR")
    print("=" * 80)
    
    # Load CSV
    print(f"\n📄 Loading CSV from: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE, low_memory=False)
    print(f"   ✅ Loaded {len(df)} rows")
    
    # Get all PDF folders from source
    pdf_folders = [f for f in SOURCE_DIR.iterdir() if f.is_dir()]
    print(f"\n📂 Found {len(pdf_folders)} PDF folders in source")
    
    # Process each PDF folder
    processed_count = 0
    no_data_count = 0
    
    print(f"\n🔄 Processing PDF folders...\n")
    
    for pdf_folder in sorted(pdf_folders):
        pdf_name = pdf_folder.name.replace('.pdf', '')
        
        # Find matching rows in CSV
        # Try both with and without .pdf extension
        matching_rows = df[df['pdf_name'].isin([pdf_name, f"{pdf_name}.pdf"])]
        
        if len(matching_rows) > 0:
            # Convert DataFrame to list of dictionaries
            rows_data = matching_rows.to_dict('records')
            
            # Create JSON file
            json_file = pdf_folder / "student_joined_ocr.json"
            
            with open(json_file, 'w') as f:
                json.dump(rows_data, f, indent=2)
            
            processed_count += 1
            print(f"✅ {processed_count}. {pdf_folder.name}")
            print(f"   📊 {len(rows_data)} row(s) saved to student_joined_ocr.json")
            
        else:
            no_data_count += 1
            if no_data_count <= 5:  # Show first 5
                print(f"⏭️  {pdf_folder.name}: No matching data in CSV")
    
    if no_data_count > 5:
        print(f"⏭️  ... and {no_data_count - 5} more folders skipped (no CSV data)")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Processed: {processed_count} folders")
    print(f"⏭️  Skipped: {no_data_count} folders (no CSV data)")
    print(f"📁 Output: student_joined_ocr.json files in each folder")
    print("=" * 80)

if __name__ == "__main__":
    main()
