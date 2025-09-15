"""
File Manager Component

Handles all file operations including PDF management, downloads, and file validation.
Separates file handling concerns from the main UI logic.
"""

import os
import requests
from pathlib import Path
from typing import List, Optional

from utils import extract_pdf_name_from_url, validate_pdf_name


class FileManager:
    """Manages file operations for PDFs and related assets"""
    
    def __init__(self, pdf_dir: str, image_dir: str, cache_dir: str):
        """
        Initialize FileManager with required directories
        
        Args:
            pdf_dir: Directory for PDF files
            image_dir: Directory for images
            cache_dir: Directory for cache files
        """
        self.pdf_dir = pdf_dir
        self.image_dir = image_dir
        self.cache_dir = cache_dir
        
        # Ensure directories exist
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        """Create directories if they don't exist"""
        for dir_path in [self.pdf_dir, self.image_dir, self.cache_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def get_existing_pdfs(self) -> List[str]:
        """
        Get list of existing PDF files in the PDF directory
        
        Returns:
            List of PDF filenames
        """
        try:
            pdf_files = []
            for file in os.listdir(self.pdf_dir):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(file)
            return sorted(pdf_files)
        except (OSError, FileNotFoundError):
            return []
    
    def pdf_exists(self, pdf_name: str) -> bool:
        """
        Check if a PDF file exists in the directory
        
        Args:
            pdf_name: Name of the PDF file
            
        Returns:
            True if file exists, False otherwise
        """
        if not validate_pdf_name(pdf_name):
            return False
        
        pdf_path = os.path.join(self.pdf_dir, pdf_name)
        return os.path.isfile(pdf_path)
    
    def get_pdf_path(self, pdf_name: str) -> Optional[str]:
        """
        Get full path to a PDF file
        
        Args:
            pdf_name: Name of the PDF file
            
        Returns:
            Full path to PDF if it exists, None otherwise
        """
        if not self.pdf_exists(pdf_name):
            return None
        
        return os.path.join(self.pdf_dir, pdf_name)
    
    def download_pdf(self, pdf_name: str, base_url: str) -> bool:
        """
        Download a PDF file from URL
        
        Args:
            pdf_name: Name of the PDF file  
            base_url: Base URL for downloading
            
        Returns:
            True if download successful, False otherwise
        """
        if not validate_pdf_name(pdf_name):
            print(f"Invalid PDF name: {pdf_name}")
            return False
        
        # Check if file already exists
        if self.pdf_exists(pdf_name):
            print(f"PDF {pdf_name} already exists.")
            return True
        
        try:
            # Construct download URL
            if base_url.endswith('/'):
                download_url = f"{base_url}{pdf_name}"
            else:
                download_url = f"{base_url}/{pdf_name}"
            
            # Download with progress
            print(f"Downloading {pdf_name}...")
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            # Save to file
            pdf_path = os.path.join(self.pdf_dir, pdf_name)
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Successfully downloaded {pdf_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {pdf_name}: {str(e)}")
            return False
        except Exception as e:
            print(f"Error saving {pdf_name}: {str(e)}")
            return False
    
    def get_file_size(self, pdf_name: str) -> Optional[str]:
        """
        Get human-readable file size for a PDF
        
        Args:
            pdf_name: Name of the PDF file
            
        Returns:
            File size string or None if file doesn't exist
        """
        pdf_path = self.get_pdf_path(pdf_name)
        if not pdf_path:
            return None
        
        try:
            size_bytes = os.path.getsize(pdf_path)
            
            # Convert to human readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
            
        except OSError:
            return None
    
    def cleanup_temp_files(self):
        """Clean up temporary files in cache directory"""
        try:
            temp_pattern = "*.tmp"
            import glob
            
            temp_files = glob.glob(os.path.join(self.cache_dir, temp_pattern))
            removed_count = 0
            
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                    removed_count += 1
                except OSError:
                    continue
            
            if removed_count > 0:
                print(f"Cleaned up {removed_count} temporary files")
                
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
    
    def get_directory_info(self) -> dict:
        """
        Get information about managed directories
        
        Returns:
            Dictionary with directory information
        """
        info = {}
        
        for name, path in [
            ("PDF Directory", self.pdf_dir),
            ("Image Directory", self.image_dir), 
            ("Cache Directory", self.cache_dir)
        ]:
            try:
                if os.path.exists(path):
                    file_count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
                    info[name] = {
                        "path": path,
                        "exists": True,
                        "file_count": file_count
                    }
                else:
                    info[name] = {
                        "path": path,
                        "exists": False,
                        "file_count": 0
                    }
            except OSError:
                info[name] = {
                    "path": path,
                    "exists": False,
                    "file_count": 0
                }
        
        return info
