"""
OCR Handler Module

This module handles all OCR-related functionality and imports, providing a clean interface
for the UI components while managing import dependencies gracefully.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import pandas as pd
import json
import config

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import UI utilities
from utils import clean_qb_html_content_basic

class OCRHandler:
    """Handles all OCR-related operations and manages import dependencies"""
    
    def __init__(self):
        self.available_modules = {}
        self.is_available = False
        self.clean_html_content = config.OCR_CONFIG['clean_html_content']
        self._initialize_imports()
    
    def _initialize_imports(self):
        """Initialize and test all required imports"""
        print("Initializing OCR Handler...")
        
        # Try to import OCR modules
        try:
            from ocr.gemini import ocr_with_questions
            self.available_modules['ocr_with_questions'] = ocr_with_questions
            print("✓ Successfully imported ocr_with_questions")
        except ImportError as e:
            print(f"✗ Failed to import ocr.gemini: {e}")
            self.available_modules['ocr_with_questions'] = None
        
        # Try to import HTML text cleaner
        try:
            from render_and_save_qb_questions.html_text_cleaner import extract_text_from_html
            self.available_modules['extract_text_from_html'] = extract_text_from_html
            print("✓ Successfully imported extract_text_from_html")
        except ImportError as e:
            print(f"✗ Failed to import extract_text_from_html: {e}")
            self.available_modules['extract_text_from_html'] = None
        
        # Try to import visualization functions
        try:
            from render_and_save_qb_questions import visualize_and_save_question
            self.available_modules['visualize_and_save_question'] = visualize_and_save_question
            print("✓ Successfully imported visualize_and_save_question")
        except ImportError as e:
            print(f"✗ Failed to import visualize_and_save_question: {e}")
            self.available_modules['visualize_and_save_question'] = None
        
        # Try to import image utilities
        try:
            from ocr.utils.image_utils import resize_image
            self.available_modules['resize_image'] = resize_image
            print("✓ Successfully imported resize_image")
        except ImportError as e:
            print(f"✗ Failed to import resize_image: {e}")
            self.available_modules['resize_image'] = None
        
        # Determine overall availability
        self.is_available = (
            self.available_modules['ocr_with_questions'] is not None and
            self.available_modules['extract_text_from_html'] is not None
        )
        
        print(f"OCR Handler availability: {self.is_available}")
    
    def clean_qb_html_content(self, html_content: str) -> str:
        """
        Clean QB HTML content using available methods
        
        Args:
            html_content: QB content string (JSON format)
            
        Returns:
            Cleaned text string
        """
        extract_text_from_html = self.available_modules.get('extract_text_from_html')
        
        if extract_text_from_html is not None:
            try:
                cleaned_data_string = html_content.replace('\\/', '/')
                data = json.loads(cleaned_data_string)
                html_content_string = data[0]['questionStem']['text']
                return extract_text_from_html(html_content_string)
            except Exception as e:
                print(f"Error using extract_text_from_html: {e}")
                return clean_qb_html_content_basic(html_content)
        else:
            # Fallback to basic cleaning
            return clean_qb_html_content_basic(html_content)
    
    def get_question_list(self, test_df: pd.DataFrame, image_dir: str, resize_dim: int = 768) -> List:
        """
        Generate question list from test dataframe
        
        Args:
            test_df: DataFrame containing question data
            image_dir: Directory for storing images
            resize_dim: Image resize dimension
            
        Returns:
            List of questions and images
        """
        question_list = []
        
        visualize_and_save_question = self.available_modules.get('visualize_and_save_question')
        resize_image = self.available_modules.get('resize_image')
        
        try:
            for _, row in test_df.iterrows():
                question_content = row['content']
                question_id = row['QB_ID']
                question_number = row['Question_no']
                question_list.append(f"Question {question_number}")
                
                if 'image.png' in str(question_content):
                    # Handle questions with images
                    if visualize_and_save_question is not None and resize_image is not None:
                        try:
                            image_path = visualize_and_save_question(
                                question_content, 
                                f'{question_id}.jpg', 
                                image_dir
                            )
                            _, _, resized_image = resize_image(image_path, dim=resize_dim)
                            question_list.append(resized_image)
                        except Exception as e:
                            print(f"Error processing image for question {question_id}: {e}")
                            question_list.append(self.clean_qb_html_content(question_content))
                    else:
                        # Fallback to text if image processing not available
                        if self.clean_html_content:
                            question_list.append(self.clean_qb_html_content(question_content))
                        else:
                            question_list.append(question_content)
                else:
                    # Handle text-only questions
                    question_list.append(self.clean_qb_html_content(question_content))
            
            return question_list
            
        except Exception as e:
            print(f"Error generating question list: {e}")
            return []
    
    def get_solution_list(self, test_df: pd.DataFrame) -> List[str]:
        """
        Generate solution list from test dataframe using cleaned solutions
        
        Args:
            test_df: DataFrame containing question data with 'textsolutions' column
            
        Returns:
            List of cleaned solutions corresponding to questions
        """
        solution_list = []
        
        try:
            # Import text preprocessor
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from data_processing.preprocessor import TextPreprocessor
            text_preprocessor = TextPreprocessor(min_chars=1)
            
            for _, row in test_df.iterrows():
                question_number = row['Question_no']
                
                # Get and clean the solution
                if 'textsolutions' in row and pd.notna(row['textsolutions']):
                    cleaned_solution = text_preprocessor.process_solution(row['textsolutions'])
                    # Only add non-empty solutions
                    if cleaned_solution and cleaned_solution.strip() and len(cleaned_solution.strip()) > 1:
                        solution_list.append(f"QB Solution {question_number}: {cleaned_solution}")
                    else:
                        solution_list.append(f"QB Solution {question_number}: Not available")
                else:
                    solution_list.append(f"QB Solution {question_number}: Not available")
            
            return solution_list
            
        except Exception as e:
            print(f"Error generating solution list: {e}")
            return []
    
    def get_interleaved_question_solution_list(self, test_df: pd.DataFrame, image_dir: str, resize_dim: int = 768) -> List:
        """
        Generate interleaved question and solution list for QB-guided assessment
        
        Args:
            test_df: DataFrame containing question data
            image_dir: Directory for storing images
            resize_dim: Image resize dimension
            
        Returns:
            List with format: [Question 1, QB Solution 1, Question 2, QB Solution 2, ...]
        """
        interleaved_list = []
        
        visualize_and_save_question = self.available_modules.get('visualize_and_save_question')
        resize_image = self.available_modules.get('resize_image')
        
        try:
            # Import text preprocessor
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from data_processing.preprocessor import TextPreprocessor
            text_preprocessor = TextPreprocessor(min_chars=1)
            
            # Iterate over DataFrame rows to ensure question and solution are from the same row
            for _, row in test_df.iterrows():
                question_content = row['content']
                question_id = row['QB_ID']
                question_number = row['Question_no']
                
                # Add question number header
                interleaved_list.append(f"Question {question_number}")
                
                # Add question content/image
                if 'image.png' in str(question_content):
                    # Handle questions with images
                    if visualize_and_save_question is not None and resize_image is not None:
                        try:
                            image_path = visualize_and_save_question(
                                question_content, 
                                f'{question_id}.jpg', 
                                image_dir
                            )
                            _, _, resized_image = resize_image(image_path, dim=resize_dim)
                            interleaved_list.append(resized_image)
                        except Exception as e:
                            print(f"Error processing image for question {question_id}: {e}")
                            interleaved_list.append(self.clean_qb_html_content(question_content))
                    else:
                        # Fallback to text if image processing not available
                        if self.clean_html_content:
                            interleaved_list.append(self.clean_qb_html_content(question_content))
                        else:
                            interleaved_list.append(question_content)
                else:
                    # Handle text-only questions
                    if self.clean_html_content:
                        interleaved_list.append(self.clean_qb_html_content(question_content))
                    else:
                        interleaved_list.append(question_content)
                
                # Add QB solution for the same question
                if 'textsolutions' in row and pd.notna(row['textsolutions']):
                    cleaned_solution = text_preprocessor.process_solution(row['textsolutions'])
                    # Only add non-empty solutions
                    if cleaned_solution and cleaned_solution.strip() and len(cleaned_solution.strip()) > 1:
                        interleaved_list.append(f"QB Solution {question_number}: {cleaned_solution}")
                    else:
                        interleaved_list.append(f"QB Solution {question_number}: Not available")
                else:
                    interleaved_list.append(f"QB Solution {question_number}: Not available")
            
            return interleaved_list
            
        except Exception as e:
            print(f"Error generating interleaved list: {e}")
            return []  # Return empty list on error
    
    def run_ocr_processing(
        self, 
        pdf_path: str, 
        questions_list: List, 
        output_folder: str, 
        cache_dir: str, 
        prompt_version: str
    ) -> Optional[Any]:
        """
        Run OCR processing with the selected prompt version
        
        Args:
            pdf_path: Path to the PDF file
            questions_list: List of questions to process
            output_folder: Output directory
            cache_dir: Cache directory
            prompt_version: Prompt version to use
            
        Returns:
            OCR result or None if failed
        """
        ocr_with_questions = self.available_modules.get('ocr_with_questions')
        
        if ocr_with_questions is None:
            raise Exception("OCR functionality is not available. Missing ocr_with_questions module.")
        
        if not questions_list:
            raise Exception("No questions provided for processing")
        
        try:
            # Ensure output directory exists
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            
            # Run OCR processing
            ocr_result = ocr_with_questions(
                questions_list, 
                pdf_path, 
                output_folder, 
                cache_dir, 
                prompt_version=prompt_version
            )
            
            return ocr_result
            
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def get_availability_status(self) -> Dict[str, bool]:
        """
        Get detailed availability status of all modules
        
        Returns:
            Dictionary with module availability status
        """
        return {
            'overall_available': self.is_available,
            'ocr_with_questions': self.available_modules['ocr_with_questions'] is not None,
            'extract_text_from_html': self.available_modules['extract_text_from_html'] is not None,
            'visualize_and_save_question': self.available_modules['visualize_and_save_question'] is not None,
            'resize_image': self.available_modules['resize_image'] is not None,
        }


# Global OCR handler instance
ocr_handler = OCRHandler()
