"""
Visualization Module for PDF and Question Analysis

This module provides components for visualizing PDF pages and question analysis results
with synchronized navigation and detailed feedback display.

This module now uses modular components for better maintainability.
"""

import streamlit as st
import pandas as pd
import os
from typing import List, Dict, Any, Optional

# Import the new modular components
from components import (
    PDFVisualizer,
    QuestionVisualizer,
    ImageRenderer,
    PDFQuestionViewer as ModularPDFQuestionViewer,
    rotate_image
)

# Import local utilities
from utils import validate_ocr_result, clean_html_content_basic
from ocr_handler import ocr_handler


# Re-export the main components for backward compatibility
__all__ = [
    'PDFVisualizer',
    'QuestionVisualizer',
    'PDFQuestionViewer',
    'ImageRenderer',
    'rotate_image',
    'render_image_with_rotation',
    'render_pil_image_with_rotation'
]


def render_image_with_rotation(image_path: str, caption: str, key_prefix: str = ""):
    """Render an image with rotation controls - wrapper for component method"""
    from components.image_renderer import render_image_with_rotation as render_img
    render_img(image_path, caption, key_prefix)


def render_pil_image_with_rotation(image, caption: str, key_prefix: str = ""):
    """Render a PIL Image with rotation controls - wrapper for component method"""
    from components.image_renderer import render_pil_image_with_rotation as render_pil
    render_pil(image, caption, key_prefix)


# Legacy class for backward compatibility
class PDFQuestionViewer:
    """Legacy wrapper for the new modular PDFQuestionViewer component"""
    
    def __init__(self, pdf_path: str, cache_dir: str, ocr_results: List[Dict], 
                 questions_list: List, metadata: pd.DataFrame, prompt_version: str = None):
        self.viewer = ModularPDFQuestionViewer(pdf_path, cache_dir, ocr_results, questions_list, metadata, prompt_version)
    
    def render_viewer(self):
        """Render the viewer using the new modular approach with comparison support"""
        # The new modular viewer handles comparison internally
        self.viewer.render_viewer()
    
    def render_simple_viewer(self):
        """Render the simple viewer layout"""
        self.viewer.render_simple_viewer()
    
    def render_stacked_viewer(self):
        """Render the stacked viewer layout"""
        self.viewer.render_stacked_viewer()
    
    def render_comparison_viewer(self):
        """Render the comparison viewer layout"""
        return self.viewer.render_comparison_viewer()