"""
UI Utility Functions

This module contains utility functions for the UI components that don't depend on external OCR modules.
"""

import json
import re
from typing import Optional, List, Dict, Any
import pandas as pd


def clean_html_content_basic(html_content: str) -> str:
    """
    Basic HTML cleaning without external dependencies
    
    Args:
        html_content: Raw HTML content string
        
    Returns:
        Cleaned text string
    """
    try:
        # Basic HTML tag removal
        clean_text = re.sub('<[^<]+?>', '', html_content)
        # Clean up extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()
    except Exception:
        return str(html_content)


def clean_qb_html_content_basic(html_content: str) -> str:
    """
    Clean QB HTML content without external dependencies
    
    Args:
        html_content: QB content string (JSON format)
        
    Returns:
        Cleaned text string
    """
    try:
        cleaned_data_string = html_content.replace('\\/', '/')
        data = json.loads(cleaned_data_string)
        html_content_string = data[0]['questionStem']['text']
        return clean_html_content_basic(html_content_string)
    except Exception as e:
        return str(html_content)


def extract_pdf_name_from_url(url: str) -> str:
    """
    Extract PDF name from UPLOADED_ANS URL
    
    Args:
        url: Full URL to the PDF
        
    Returns:
        PDF filename
    """
    try:
        return url.split("/")[-1] if url else ""
    except Exception:
        return ""


def validate_pdf_name(pdf_name: str) -> bool:
    """
    Validate PDF name format
    
    Args:
        pdf_name: PDF filename to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not pdf_name:
        return False
    
    # Check if it ends with .pdf
    if not pdf_name.lower().endswith('.pdf'):
        return False
    
    # Check if it's not just .pdf
    if len(pdf_name) <= 4:
        return False
    
    return True


def format_metadata_display(metadata: pd.DataFrame) -> Dict[str, Any]:
    """
    Format metadata for display in the UI
    
    Args:
        metadata: DataFrame containing PDF metadata
        
    Returns:
        Dictionary with formatted metadata information
    """
    if metadata.empty:
        return {}
    
    try:
        result = {}
        
        # Basic information
        if 'SUBJECT' in metadata.columns:
            result['subjects'] = list(metadata['SUBJECT'].unique())
        
        if 'TEST_NAME' in metadata.columns:
            result['test_names'] = list(metadata['TEST_NAME'].unique())
        
        if 'Question_no' in metadata.columns:
            result['question_count'] = len(metadata['Question_no'].unique())
            result['question_numbers'] = sorted(metadata['Question_no'].unique())
        
        if 'Marks' in metadata.columns:
            result['total_marks'] = metadata['Marks'].sum()
            result['avg_marks'] = metadata['Marks'].mean()
        
        # Additional metadata
        result['total_records'] = len(metadata)
        
        return result
        
    except Exception:
        return {}


def get_prompt_version_info() -> Dict[str, str]:
    """
    Get information about available prompt versions
    
    Returns:
        Dictionary mapping version codes to descriptions
    """
    return {
        "v8": "v8 - gemini 2.5 pro out of the box assessment",
        "v9": "v9 - LearnLM Pedagogical Analysis (Socratic Method)",
        "v10": "v10 - CBSE Examiner Evaluation (Quantitative Marking)",
        "v11": "v11 - Hybrid Assessment (CBSE + Learning Feedback)"
    }


def create_download_filename(pdf_name: str, prompt_version: str, extension: str = "json") -> str:
    """
    Create a standardized filename for downloads
    
    Args:
        pdf_name: Original PDF name
        prompt_version: Prompt version used
        extension: File extension (default: json)
        
    Returns:
        Formatted filename
    """
    # Remove .pdf extension from pdf_name if present
    base_name = pdf_name.replace('.pdf', '') if pdf_name.endswith('.pdf') else pdf_name
    return f"ocr_results_{base_name}_{prompt_version}.{extension}"


def validate_ocr_result(ocr_result: Any) -> bool:
    """
    Validate OCR result format
    
    Args:
        ocr_result: OCR processing result
        
    Returns:
        True if valid result, False otherwise
    """
    if not ocr_result:
        return False
    
    if isinstance(ocr_result, list) and len(ocr_result) > 0:
        return True
    
    if isinstance(ocr_result, dict) and ocr_result:
        return True
    
    return False 