import os
import json
import csv
import glob

def process_json_files(base_path):
    """
    Process JSON files to extract gemini_ocr, page_number, pdf_name, and question_number
    
    Args:
        base_path: Path to the directory containing JSON files
    """
    
    # Get all JSON files recursively
    json_pattern = os.path.join(base_path, "**", "*.json")
    json_files = glob.glob(json_pattern, recursive=True)
    
    # Prepare CSV data
    csv_data = []
    csv_headers = ['gemini_ocr', 'page_number', 'pdf_name', 'question_number']
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Extract required fields
            gemini_ocr = json_data.get('ocr_text', '')
            question_number = json_data.get('question_number', '')
            pdf_name = json_data.get('pdf_name', '')
            
            # Extract page numbers from ocr_pages array (comma-separated if multiple)
            ocr_pages = json_data.get('ocr_pages', [])
            page_number = ','.join(map(str, ocr_pages)) if ocr_pages else ''
            
            # Add row to CSV data
            csv_data.append([gemini_ocr, page_number, pdf_name, question_number])
            
            print(f"Processed: {os.path.basename(json_file)} - Question {question_number}, PDF: {pdf_name}")
            
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON format in {json_file}")
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
    
    # Write CSV file
    if csv_data:
        csv_filename = "gemini_ocr.csv"
        csv_path = os.path.join(base_path, csv_filename)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_headers)
            writer.writerows(csv_data)
        
        print(f"\nCreated {csv_filename} with {len(csv_data)} rows at {csv_path}")
    else:
        print("No valid JSON data found")

def main():
    """
    Main function to process JSON files and create CSV
    """
    # Base path where the JSON files are located
    base_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z3_ocr_gemini_pcmb_13.3/maths/table_format"
    
    print(f"Processing JSON files in: {base_path}")
    
    if os.path.exists(base_path):
        process_json_files(base_path)
    else:
        print(f"Error: Directory not found at {base_path}")

if __name__ == "__main__":
    main()
