import os
import sys
from typing import List, Union
from PIL import Image

# Ensure we import from the local config in this directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from config import IMAGE_RESIZE_DIM, RESIZED_IMAGE_PATTERN
from image_utils import resize_image
from pdf_utils import pdf_to_images


def process_images_to_resized_objects(images: List[str], output_folder: str, pdf_name: str = None) -> List[Image.Image]:
    """Resizes images to configured dimension and saves to output folder."""
    print(f"Resizing images to {IMAGE_RESIZE_DIM}...")
    resized_images = []
    
    # Extract PDF name from first image path if not provided
    if pdf_name is None and images:
        first_image = os.path.basename(images[0])
        if '_page_' in first_image:
            pdf_name = first_image.split('_page_')[0]
        else:
            pdf_name = "unknown"
    
    for page_num, img_path in enumerate(images):
        img_filename_dim = RESIZED_IMAGE_PATTERN.format(
            pdf_name=pdf_name, 
            dim=IMAGE_RESIZE_DIM, 
            page_num=page_num + 1
        )
        
        _, _, resized_image = resize_image(
            Image.open(img_path), 
            dim=IMAGE_RESIZE_DIM, 
            save_path=os.path.join(output_folder, img_filename_dim)
        )
        
        resized_images.append(resized_image)
    
    print(f"Resized {len(resized_images)} images to {IMAGE_RESIZE_DIM}")
    return resized_images


def process_pdf_to_images(pdf_file_path: str, output_folder: str) -> tuple[List[str], int]:
    """Converts PDF pages to individual image files."""
    print(f"Processing PDF: {pdf_file_path}")
    print("Converting PDF to images...")
    
    images, num_pages = pdf_to_images(pdf_file_path, output_folder)
    print(f"Converted {num_pages} pages to images")
    
    return images, num_pages


def process_mixed_images(hand_written_solution_images: List[Union[str, Image.Image]], 
                        output_folder: str) -> List[Image.Image]:
    """Handles both file paths and PIL Image objects, resizing all to standard dimension."""
    print(f"Processing {len(hand_written_solution_images)} solution images...")
    
    hand_written_solutions = []
    for i, img in enumerate(hand_written_solution_images):
        if isinstance(img, str):
            # It's a file path
            img_filename_dim = RESIZED_IMAGE_PATTERN.format(dim=IMAGE_RESIZE_DIM, page_num=i + 1)
            _, _, resized_image = resize_image(
                Image.open(img), 
                dim=IMAGE_RESIZE_DIM, 
                save_path=os.path.join(output_folder, img_filename_dim)
            )
            hand_written_solutions.append(resized_image)
        elif isinstance(img, Image.Image):
            # It's already a PIL Image, just resize if needed
            img_filename_dim = RESIZED_IMAGE_PATTERN.format(dim=IMAGE_RESIZE_DIM, page_num=i + 1)
            _, _, resized_image = resize_image(
                img, 
                dim=IMAGE_RESIZE_DIM, 
                save_path=os.path.join(output_folder, img_filename_dim)
            )
            hand_written_solutions.append(resized_image)
        else:
            raise ValueError(f"Unsupported image type: {type(img)}")
    
    print(f"Processed {len(hand_written_solutions)} solution images")
    return hand_written_solutions


class ImageProcessor:
    """Image processing coordinator for OCR workflows."""
    
    def __init__(self, output_folder: str):
        """Creates output folder if it doesn't exist."""
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
    
    def process_pdf(self, pdf_file_path: str) -> List[Image.Image]:
        """Converts PDF to images, then resizes them."""
        images, _ = process_pdf_to_images(pdf_file_path, self.output_folder)
        pdf_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
        return process_images_to_resized_objects(images, self.output_folder, pdf_name)
    
    def process_image_list(self, image_paths: List[str]) -> List[Image.Image]:
        """Resizes all images in the list."""
        return process_images_to_resized_objects(image_paths, self.output_folder)
    
    def process_mixed_inputs(self, mixed_images: List[Union[str, Image.Image]]) -> List[Image.Image]:
        """Handles mix of file paths and PIL Images."""
        return process_mixed_images(mixed_images, self.output_folder) 