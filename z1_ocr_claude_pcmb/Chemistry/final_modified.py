import json
import pandas as pd
import os
from datetime import datetime

def convert_json_to_csv(json_file_path, output_csv_path):
    """
    Convert final_table_ordered.json to CSV with specified columns
    """
    
    print(f"🔄 Reading JSON file: {json_file_path}")
    
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        return False
    
    try:
        # Read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract the merged_data array
        if 'merged_data' in data:
            records = data['merged_data']
            total_files = data.get('total_files', len(records))
            print(f"📊 Found {total_files} records in JSON")
        else:
            # If it's a direct array
            records = data
            total_files = len(records)
            print(f"📊 Found {total_files} records in JSON")
        
        # Prepare CSV data
        csv_data = []
        
        print("🔄 Converting records to CSV format...")
        
        for i, record in enumerate(records, 1):
            # Extract page numbers (join array to string)
            ocr_pages = record.get('ocr_pages', [])
            if isinstance(ocr_pages, list):
                page_numbers = ', '.join(map(str, ocr_pages)) if ocr_pages else 'N/A'
            else:
                page_numbers = str(ocr_pages)
            
            # Base directory for images
            images_base_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr/chemistry/Chemistry_Gemini/chem/images/"
            
            # Generate full image path based on folder_id and page number
            folder_id = record.get('folder_id', '')
            if folder_id and ocr_pages:
                # Use first page number for the image
                first_page = ocr_pages[0] if isinstance(ocr_pages, list) and ocr_pages else ocr_pages
                image_filename = f"{folder_id}_page_{first_page}.png"
                student_image = os.path.join(images_base_dir, image_filename)
                
                # Check if file exists, if not use fallback
                if not os.path.exists(student_image):
                    print(f"⚠️  Image not found: {student_image}")
                    student_image = os.path.join(images_base_dir, "placeholder.png")  # fallback
            else:
                student_image = os.path.join(images_base_dir, "placeholder.png")  # Default fallback image
            
            # Create CSV row
            csv_row = {
                'pdf_source': record.get('folder_id', ''),
                'Human_text': record.get('human_text', ''),
                'ocr_text': record.get('ocr_text', ''),
                'type_of_error': record.get('type_of_error', ''),
                'discrepancy_analysis': record.get('discrepancy_analysis', ''),
                'Feedback': '',  # Empty column for feedback
                'student_image': student_image,
                'page_number': page_numbers,
                'question_number': record.get('question_number', ''),
                'has_errors': record.get('has_errors', False)
            }
            
            csv_data.append(csv_row)
            
            # Show progress
            if i % 10 == 0 or i == total_files:
                print(f"   📈 Progress: {i}/{total_files} ({(i/total_files)*100:.1f}%)")
        
        # Create DataFrame
        print("📝 Creating CSV file...")
        df = pd.DataFrame(csv_data)
        
        # Reorder columns as requested
        column_order = [
            'pdf_source',
            'Human_text', 
            'ocr_text',
            'type_of_error',
            'discrepancy_analysis',
            'Feedback',
            'student_image',
            'page_number',
            'question_number',
            'has_errors'
        ]
        
        df = df[column_order]
        
        # Save to CSV
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        
        print(f"✅ CSV file created successfully!")
        print(f"📂 Location: {output_csv_path}")
        print(f"📊 Total rows: {len(df)}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Show sample data
        print(f"\n🔍 Sample data (first 3 rows):")
        print("=" * 80)
        if len(df) > 0:
            for idx, row in df.head(3).iterrows():
                print(f"Row {idx + 1}:")
                print(f"   PDF Source: {row['pdf_source']}")
                print(f"   Question: {row['question_number']}")
                print(f"   Pages: {row['page_number']}")
                print(f"   Human Text: {row['Human_text'][:50]}...")
                print(f"   OCR Text: {row['ocr_text'][:50]}...")
                print(f"   Error Type: {row['type_of_error']}")
                print(f"   Student Image: {row['student_image']}")
                print("-" * 40)
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def analyze_csv_stats(csv_path):
    """
    Analyze the created CSV and show statistics
    """
    try:
        df = pd.read_csv(csv_path)
        
        print(f"\n📊 CSV ANALYSIS:")
        print("=" * 50)
        print(f"Total records: {len(df)}")
        print(f"Unique PDFs: {df['pdf_source'].nunique()}")
        print(f"Records with errors: {df['has_errors'].sum()}")
        print(f"Records without errors: {(~df['has_errors']).sum()}")
        
        print(f"\n📋 Error Types Distribution:")
        error_counts = df['type_of_error'].value_counts()
        for error_type, count in error_counts.head(10).items():
            print(f"   {error_type}: {count}")
        
        print(f"\n📄 Pages Distribution:")
        page_counts = df['page_number'].value_counts()
        for page, count in page_counts.head(10).items():
            print(f"   Page {page}: {count}")
            
    except Exception as e:
        print(f"❌ Error analyzing CSV: {e}")

if __name__ == "__main__":
    # File paths
    json_file_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr/chemistry/final_table_ordered.json"
    output_csv_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr/chemistry/final.csv"
    
    print("🎯 JSON to CSV Converter")
    print("=" * 70)
    print(f"📂 Input JSON: {json_file_path}")
    print(f"📂 Output CSV: {output_csv_path}")
    print("=" * 70)
    
    # Convert JSON to CSV
    success = convert_json_to_csv(json_file_path, output_csv_path)
    
    if success:
        # Analyze the created CSV
        analyze_csv_stats(output_csv_path)
        
        print(f"\n🎉 Conversion completed successfully!")
        print(f"📁 CSV file saved as: final.csv")
        print(f"📊 Ready for analysis and review!")
    else:
        print(f"\n❌ Conversion failed!")
    
    print("=" * 70)