"""
Data preprocessing module for subjective answer analysis.
Handles loading, cleaning, and validation of text solutions.
"""

import pandas as pd
import numpy as np
import json
import re
from bs4 import BeautifulSoup

class TextPreprocessor:
    def __init__(self, min_chars=10):
        self.min_chars = min_chars
        
    def clean_html(self, text):
        """Remove styling-related HTML tags while preserving content."""
        if not isinstance(text, str):
            return ""
            
        # Parse HTML
        soup = BeautifulSoup(text, 'html.parser')
        
        # Remove style attributes and specific tags
        for tag in soup.find_all(True):
            if 'style' in tag.attrs:
                del tag['style']
                
        # Get text content
        text = soup.get_text(separator=' ')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
        
    def is_valid_solution(self, text):
        """Check if solution meets minimum requirements."""
        if not isinstance(text, str):
            return False
        
        # Remove whitespace and check length
        clean_text = re.sub(r'\s+', '', text)
        return len(clean_text) >= self.min_chars
        
    def process_solution(self, solution_json):
        """Process a single solution from JSON format."""
        try:
            solutions = json.loads(solution_json) if pd.notna(solution_json) else []
            
            # Get text from all language versions
            all_text = []
            for sol in solutions:
                if isinstance(sol, dict) and 'text' in sol:
                    cleaned_text = self.clean_html(sol['text'])
                    if cleaned_text:
                        all_text.append(cleaned_text)
            
            # Combine all valid text
            combined_text = ' '.join(all_text)
            
            return combined_text if self.is_valid_solution(combined_text) else None
            
        except Exception as e:
            print(f"Error processing solution: {e}")
            return None
            
    def load_and_process_data(self, csv_path):
        """Load and preprocess the CSV data."""
        print("Loading data from CSV...")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"CSV loaded with {len(df)} rows")
        
        # Process solutions
        solutions_data = []
        
        for _, row in df.iterrows():
            processed_text = self.process_solution(row['textsolutions'])
            if processed_text:
                solutions_data.append({
                    'oldquestionid': row['oldquestionid'],
                    'solution_text': processed_text
                })
        
        # Create DataFrame with unique solutions
        solutions_df = pd.DataFrame(solutions_data)
        solutions_df = solutions_df.drop_duplicates(subset=['oldquestionid'])
        
        print(f"Found {len(solutions_df)} valid unique questions by oldquestionid")
        
        return solutions_df
