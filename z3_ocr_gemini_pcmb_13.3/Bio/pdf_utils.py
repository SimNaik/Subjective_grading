import os
import fitz  # PyMuPDF for PDF processing


def pdf_to_images(pdf_path, output_folder):
    """Converts PDF pages to JPEG images at 300 DPI."""
    doc = fitz.open(pdf_path)
    images = []
    num_pages = doc.page_count
    
    # Extract PDF filename without extension
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    for i in range(num_pages):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=300)
        img_path = os.path.join(output_folder, f"{pdf_name}_page_{i + 1}.jpeg")
        pix.save(img_path)
        images.append(img_path)
        
    doc.close()
    return images, num_pages 