import os
import base64
import numpy as np
import cv2
from PIL import Image


def resize_image(image, dim=768, save_path=None):
    """
    Resize image to specified dimension while maintaining aspect ratio.
    
    Args:
        image: PIL Image object
        dim: Target dimension for the larger side
        save_path: Optional path to save the resized image
        
    Returns:
        tuple: (original_size, new_size, resized_image_pil)
    """
    if type(image) == str:
        image = Image.open(image)
    image1 = np.array(image.convert('RGB'))  # Ensure the image is in RGB mode
    original_size = image1.shape  # (height, width, channels)
    image1 = image1.mean(axis=2)  # Convert image to grayscale
    h, w = image1.shape
    
    if w > h:
        new_w = dim
        new_h = int(h * (dim / w))
    else:
        new_h = dim
        new_w = int(w * (dim / h))
        
    resized_image = cv2.resize(image1, (new_w, new_h), interpolation=cv2.INTER_AREA)
    resized_image_pil = Image.fromarray(resized_image)
    resized_image_pil = resized_image_pil.convert('RGB')  # Convert to RGB before saving
    
    if save_path:
        resized_image_pil.save(save_path)
        
    return original_size, (new_h, new_w), resized_image_pil


def load_base64_images(folder_path, num_pages):
    """
    Load images from folder and convert to base64 format.
    
    Args:
        folder_path: Path to folder containing images
        num_pages: Number of pages to load
        
    Returns:
        list: List of base64 encoded image strings
    """
    b64_list = []
    for i in range(num_pages):
        img_filename_dim = f"DIM_768_PAGE_{i + 1}.jpeg"  # Use dim variable here
        img_filename_default = f"page_{i + 1}.jpeg"  # Old naming convention

        img_path_dim = os.path.join(folder_path, img_filename_dim)
        img_path_default = os.path.join(folder_path, img_filename_default)

        if os.path.exists(img_path_dim):
            path = img_path_dim
        elif os.path.exists(img_path_default):
            path = img_path_default
        else:
            print(f"Image {img_filename_dim} or {img_filename_default} not found in {folder_path}")
            continue

        with open(path, "rb") as f:
            b64_list.append(base64.b64encode(f.read()).decode())
    return b64_list 