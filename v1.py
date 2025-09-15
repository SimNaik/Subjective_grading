import streamlit as st
import os
import fitz  # PyMuPDF
import base64
from login import create_users_table, show_login_form
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from dbmanager import PDFDatabaseManager
import json

# Load environment variables from .env file
load_dotenv()

# Configure API key
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API"))

# Initialize the model
model = genai.GenerativeModel('gemini-2.5-flash')

# Initialize database manager
db_manager = PDFDatabaseManager()

def get_pdf_display(pdf_file, page_num=0):
    """Convert PDF to base64 for display of a specific page."""
    doc = fitz.open(stream=pdf_file.getvalue(), filetype="pdf")
    page = doc[page_num]
    pix = page.get_pixmap(dpi=300)
    img_data = pix.tobytes("png")
    base64_img = base64.b64encode(img_data).decode('utf-8')
    doc.close()
    return f'<img src="data:image/png;base64,{base64_img}" style="width:100%;">'

def process_pdf_to_images(uploaded_pdf, target_folder):
    """Process PDF and convert each page to an image."""
    try:
        # Create main directory for PDF uploads if it doesn't exist
        pdf_uploads_dir = "pdf_uploads"
        if not os.path.exists(pdf_uploads_dir):
            os.makedirs(pdf_uploads_dir)
        
        # Create directory for this specific PDF
        pdf_name = os.path.splitext(uploaded_pdf.name)[0]
        pdf_dir = os.path.join(pdf_uploads_dir, pdf_name)
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Save the PDF file
        pdf_path = os.path.join(pdf_dir, uploaded_pdf.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        
        # Create images and OCR directories
        images_dir = os.path.join(pdf_dir, "images")
        model_name = st.session_state.selected_model.replace('.', '_')
        ocr_dir = os.path.join(pdf_dir, f"ocr_{model_name}")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(ocr_dir, exist_ok=True)
        
        # Convert PDF to images
        doc = None
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for page_num in range(total_pages):
                # Update progress
                progress = (page_num + 1) / total_pages
                progress_bar.progress(progress)
                status_text.text(f"Processing page {page_num + 1} of {total_pages}")
                
                # Process page
                page = doc[page_num]
                pix = page.get_pixmap(dpi=300)  # Convert page to image with 300 DPI
                output_image_path = os.path.join(images_dir, f"page_{page_num+1}.png")
                pix.save(output_image_path)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            return True, f"Successfully processed {total_pages} pages", total_pages
            
        finally:
            if doc:
                doc.close()
                
    except Exception as e:
        return False, f"Error processing PDF: {str(e)}", 0

def perform_ocr(image_path, ocr_dir):
    """Perform OCR on the given image using Gemini and save results."""
    try:
        # Ensure OCR directory exists
        os.makedirs(ocr_dir, exist_ok=True)
        
        # Open and process the image
        image = Image.open(image_path)
        
        # Create a specific prompt for OCR
        prompt = """Carefully extract all text content from this image, maintaining the exact order and formatting as it appears.
Preserve all mathematical equations, formulas, and special characters exactly as they appear in the image.
Do not add any headers, descriptions, or labels to the output.
Output only the extracted text content."""
        
        # Generate content with image and prompt
        response = model.generate_content([image, prompt])
        response.resolve()  # Ensure the response is fully resolved
        
        # Save OCR result to file
        ocr_result = response.text
        ocr_file_path = os.path.join(ocr_dir, f"ocr_{os.path.basename(image_path).replace('.png', '.txt')}")
        with open(ocr_file_path, 'w', encoding='utf-8') as f:
            f.write(ocr_result)
        
        return ocr_result
    except Exception as e:
        return f"Error performing OCR: {str(e)}"

def process_pdf_from_bytes(pdf_bytes, original_filename):
    """Process PDF data from database and create images for OCR."""
    try:
        # Create main directory for PDF uploads if it doesn't exist
        pdf_uploads_dir = "pdf_uploads"
        if not os.path.exists(pdf_uploads_dir):
            os.makedirs(pdf_uploads_dir)
        
        # Create directory for this specific PDF
        pdf_name = os.path.splitext(original_filename)[0]
        pdf_dir = os.path.join(pdf_uploads_dir, pdf_name)
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Create BytesIO object from PDF data
        pdf_file = BytesIO(pdf_bytes)
        
        # Create images and OCR directories
        images_dir = os.path.join(pdf_dir, "images")
        model_name = st.session_state.selected_model.replace('.', '_')
        ocr_dir = os.path.join(pdf_dir, f"ocr_{model_name}")
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(ocr_dir, exist_ok=True)
        
        # Convert PDF to images
        doc = None
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for page_num in range(total_pages):
                # Update progress
                progress = (page_num + 1) / total_pages
                progress_bar.progress(progress)
                status_text.text(f"Processing page {page_num + 1} of {total_pages}")
                
                # Process page
                page = doc[page_num]
                pix = page.get_pixmap(dpi=300)  # Convert page to image with 300 DPI
                output_image_path = os.path.join(images_dir, f"page_{page_num+1}.png")
                pix.save(output_image_path)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            return True, f"Successfully processed {total_pages} pages", total_pages
            
        finally:
            if doc:
                doc.close()
                
    except Exception as e:
        return False, f"Error processing PDF: {str(e)}", 0

def get_ocr_result(image_path, ocr_dir):
    """Get OCR result from file or perform OCR if not available."""
    try:
        # Ensure OCR directory exists
        os.makedirs(ocr_dir, exist_ok=True)
        
        model_name = st.session_state.selected_model.replace('.', '_')
        ocr_file_path = os.path.join(ocr_dir, f"ocr_{os.path.basename(image_path).replace('.png', '.txt')}")
        
        if os.path.exists(ocr_file_path):
            with open(ocr_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    except Exception as e:
        st.error(f"Error getting OCR result: {str(e)}")
        return None

def merge_ocr_results(pdf_name, ocr_dir):
    """Merge all OCR results for a PDF into a single file."""
    try:
        # Get all OCR files for this PDF
        ocr_files = sorted([f for f in os.listdir(ocr_dir) if f.startswith('ocr_') and f.endswith('.txt')])
        
        if not ocr_files:
            return False, "No OCR files found to merge"
        
        # Create merged content
        merged_content = []
        for ocr_file in ocr_files:
            with open(os.path.join(ocr_dir, ocr_file), 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:  # Only add non-empty content
                    merged_content.append(content)
        
        # Save merged content
        pdf_dir = os.path.dirname(ocr_dir)
        model_name = st.session_state.selected_model.replace('.', '_')
        merged_file_path = os.path.join(pdf_dir, f"{pdf_name}_{model_name}.txt")
        with open(merged_file_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(merged_content))  # Use double newline to separate pages
        
        return True, f"Successfully merged {len(ocr_files)} OCR files"
    except Exception as e:
        return False, f"Error merging OCR files: {str(e)}"

def segregate_ocr_results(pdf_name, pdf_dir):
    """Process the merged OCR file using Gemini to segregate questions."""
    try:
        # Get model name from session state
        model_name = st.session_state.selected_model.replace('.', '_')
        
        # Read the merged OCR file
        merged_file_path = os.path.join(pdf_dir, f"{pdf_name}_{model_name}.txt")
        if not os.path.exists(merged_file_path):
            return False, "No merged OCR file found. Please run Segregate OCR first."
        
        with open(merged_file_path, 'r', encoding='utf-8') as f:
            merged_content = f.read()
        
        # Create the prompt
        prompt = """You will be given a raw text input containing a worksheet with multiple types of questions: multiple choice, true/false, and fill-in-the-blanks. 

Your task is to extract each question with its number and full text (including options if present) and produce a JSON array where each element is an object with two keys:

- "Equidnumber": the question number (integer)
- "question solution": the full question text as a single string (including options for MCQs, or blanks for fill-in-the-blank questions)

Guidelines (not hard rules):
1. Extract EVERY SINGLE question from the input text.
2. Include ALL text content for each question, such as:
   - All options for multiple choice
   - All parts of multi-part questions
   - All text between question numbers
   - All mathematical equations and special characters
3. Recognize question numbers in any format.
4. Preserve all formatting, line breaks, and special characters.
5. If a question spans multiple lines or paragraphs, include all of it.
6. Do not skip or summarize any content.
7. Do not generate or add any content that is not explicitly present in the input text.

Format the output exactly as a JSON array. For example:

[
  {
    "Equidnumber": 1,
    "question solution": "Question text including options or blanks."
  },
  {
    "Equidnumber": 2,
    "question solution": "Next question text."
  }
]

Do not include any extra explanation or commentary. Only output the JSON array.

Here is the input text:

"""
        prompt += f'"""\n{merged_content}\n"""'
        
        # Process with Gemini
        response = model.generate_content(prompt)
        response.resolve()
        
        # Clean the response text by removing JSON code block markers
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        
        # Save the segregated results with model name
        segregated_file_path = os.path.join(pdf_dir, f"{pdf_name}_{model_name}_segregated.txt")
        with open(segregated_file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        # Save the segregated json results with model name
        segregated_file_path = os.path.join(pdf_dir, f"{pdf_name}_{model_name}_segregated.json")
        with open(segregated_file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        st.rerun()
        return True, f"Successfully segregated questions into {segregated_file_path}"
    except Exception as e:
        return False, f"Error segregating OCR results: {str(e)}"

def display_segregated_questions(pdf_name, pdf_dir, in_sidebar=False):
    """Display segregated questions in card format."""
    try:
        # Read the JSON file with model name
        model_name = st.session_state.selected_model.replace('.', '_')
        json_file_path = os.path.join(pdf_dir, f"{pdf_name}_{model_name}_segregated.json")
        if not os.path.exists(json_file_path):
            return False, "No segregated questions file found. Please run Segregate OCR first."
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            questions = json.loads(f.read())
        
        # Add custom CSS for cards
        st.markdown("""
            <style>
            .question-card {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0;
                background-color: #f8f9fa;
                font-size: 0.9em;
            }
            .question-number {
                color: #1f77b4;
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 5px;
            }
            .question-text {
                white-space: pre-wrap;
                font-size: 0.9em;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Display each question in a card
        for question in questions:
            st.markdown(f"""
                <div class="question-card">
                    <div class="question-number">Question {question['Equidnumber']}</div>
                    <div class="question-text">{question['question solution']}</div>
                </div>
            """, unsafe_allow_html=True)
        
        return True, f"Displayed {len(questions)} questions"
    except Exception as e:
        return False, f"Error displaying questions: {str(e)}"

def display_model_comparison(pdf_name, pdf_dir):
    """Display questions from all models side by side for comparison."""
    try:
        # Get all available models
        available_models = [
            "gemini-2.5-flash-preview-05-20",
            "gemini-2.5-pro-preview-05-06",
            "gemini-2.5-pro-preview-03-25"
        ]
        
        # Create a container for the comparison view
        st.markdown("""
            <style>
            .comparison-container {
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 10px;
                margin: 10px 0;
            }
            .model-column {
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 5px;
            }
            .question-card {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0;
                background-color: #f8f9fa;
                font-size: 0.9em;
            }
            .question-number {
                color: #1f77b4;
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 5px;
            }
            .question-text {
                white-space: pre-wrap;
                font-size: 0.9em;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Create a header for the comparison view
        st.markdown("""
            <div class="comparison-container">
                <h2 style="text-align: center; color: #1f77b4;">Model Comparison View</h2>
                <p style="text-align: center; color: #666;">Compare OCR results from different models side by side</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Create three columns for model comparison
        cols = st.columns(3)
        
        # Display questions from each model
        for idx, model in enumerate(available_models):
            model_name = model.replace('.', '_')
            json_file_path = os.path.join(pdf_dir, f"{pdf_name}_{model_name}_segregated.json")
            
            with cols[idx]:
                st.markdown(f"""
                    <div class="model-column">
                        <h3 style="color: #1f77b4; text-align: center;">{model}</h3>
                """, unsafe_allow_html=True)
                
                if os.path.exists(json_file_path):
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        questions = json.loads(f.read())
                    
                    # Display each question in a card
                    for question in questions:
                        st.markdown(f"""
                            <div class="question-card">
                                <div class="question-number">Question {question['Equidnumber']}</div>
                                <div class="question-text">{question['question solution']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"No segregated questions found for {model}")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        return True, "Model comparison displayed successfully"
    except Exception as e:
        return False, f"Error displaying model comparison: {str(e)}"

def main():
    st.set_page_config(page_title="PDF Upload System", page_icon="📄", layout="wide")
    
    # Add custom CSS to reduce space between sidebar and main content
    st.markdown("""
        <style>
        [data-testid="stSidebar"][aria-expanded="true"]{
            padding-right: 0;
        }
        .main .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .stButton button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create users table if it doesn't exist
    create_users_table()
    
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'total_pages' not in st.session_state:
        st.session_state.total_pages = 0
    if 'ocr_results' not in st.session_state:
        st.session_state.ocr_results = {}
    if 'selected_pdf' not in st.session_state:
        st.session_state.selected_pdf = None
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "gemini-2.5-flash-preview-05-20"
    
    # Model selection dropdown
    available_models = [
        "gemini-2.5-flash-preview-05-20",
        "gemini-2.5-pro-preview-05-06",
        "gemini-2.5-pro-preview-03-25"
    ]
    selected_model = st.selectbox(
        "Select Model",
        available_models,
        index=available_models.index(st.session_state.selected_model)
    )
    
    # Update model if changed
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        model = genai.GenerativeModel(selected_model)
        st.rerun()
    
    # Main container with reduced padding
    st.title("📄 PDF Upload System")
    
    # Check if user is logged in
    if not st.session_state.user:
        st.info("Please login to access PDF upload features.")
        show_login_form()
    else:
        # Sidebar for user actions with reduced padding
        with st.sidebar:
            st.success(f"Welcome, {st.session_state.user['username']}!")
            
            # PDF Upload Section in sidebar
            st.header("Upload PDF")
            uploaded_pdf = st.file_uploader("Select a PDF file", type=["pdf"], key="pdf_uploader_1")
            
            # Show previously uploaded PDFs
            st.header("Your PDFs")
            with st.expander("Show all PDFs"):
                user_pdfs = db_manager.get_user_pdfs(st.session_state.user['id'])
            
                # Debug information
                st.write(f"Debug - User ID: {st.session_state.user['id']}")
                st.write(f"Debug - Number of PDFs found: {len(user_pdfs) if user_pdfs else 0}")
                
                if user_pdfs:
                    for pdf in user_pdfs:
                        pdf_id, original_filename, upload_date, total_pages = pdf
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if st.button(f"📄 {original_filename}", key=f"select_{pdf_id}"):
                                st.session_state.selected_pdf = pdf
                                st.session_state.current_page = 0
                                st.session_state.total_pages = total_pages
                                st.session_state.pdf_processed = False
                                st.rerun()
                        with col2:
                            if st.button("🗑️", key=f"delete_{pdf_id}"):
                                if db_manager.delete_pdf(pdf_id, st.session_state.user['id']):
                                    st.success("PDF deleted successfully!")
                                    st.rerun()
                else:
                    st.info("No PDFs uploaded yet.")
            
            # Logout button at the bottom of sidebar
            st.markdown("---")  # Add a separator
            if st.button("Logout"):
                st.session_state.user = None
                st.rerun()
            
            # Show Questions section in sidebar
            if st.session_state.selected_pdf:
                pdf_id, original_filename, upload_date, total_pages = st.session_state.selected_pdf
                pdf_name = os.path.splitext(original_filename)[0]
                pdf_dir = os.path.join("pdf_uploads", pdf_name)
                
                # Add Compare Models toggle
                compare_models = st.toggle("Compare Models", key="compare_models_toggle")
                
                if compare_models:
                    # Clear the main content area
                    st.empty()
                    
                    # Display model comparison in the main area
                    with st.spinner("Loading model comparison..."):
                        success, message = display_model_comparison(pdf_name, pdf_dir)
                        if not success:
                            st.error(message)
                else:
                    # Check if segregated JSON exists for current model
                    model_name = st.session_state.selected_model.replace('.', '_')
                    json_file_path = os.path.join(pdf_dir, f"{pdf_name}_{model_name}_segregated.json")
                    
                    if os.path.exists(json_file_path):
                        st.markdown("---")  # Add a separator
                        st.header("Segregated Questions")
                        with st.spinner("Loading questions..."):
                            success, message = display_segregated_questions(pdf_name, pdf_dir, in_sidebar=True)
                            if not success:
                                st.error(message)
                    else:
                        st.info("No segregated questions found. Please run Segregate OCR first.")
        
        # Main content area with reduced padding
        if uploaded_pdf is not None:
            # Process the PDF
            success, message, total_pages = process_pdf_to_images(uploaded_pdf, "pdf_uploads")
            
            if success:
                st.success(message)
                st.session_state.total_pages = total_pages
                
                # Save to database
                try:
                    # Read PDF data
                    pdf_data = uploaded_pdf.getvalue()
                    st.write(f"Debug - PDF size: {len(pdf_data)} bytes")
                    st.write(f"Debug - User ID: {st.session_state.user['id']}")
                    st.write(f"Debug - Filename: {uploaded_pdf.name}")
                    
                    db_manager.add_pdf(uploaded_pdf.name, st.session_state.user['id'], pdf_data, total_pages)
                    st.success("PDF saved to database successfully!")
                    
                    # Verify the PDF was saved
                    user_pdfs = db_manager.get_user_pdfs(st.session_state.user['id'])
                    st.write(f"Debug - PDFs after save: {len(user_pdfs)}")
                except Exception as e:
                    st.error(f"Error saving PDF to database: {str(e)}")
                    st.write(f"Debug - Error details: {str(e)}")
                
                # Create two columns for the layout with reduced spacing
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Display PDF preview with navigation
                    st.write("PDF Preview:")
                    
                    # Navigation controls
                    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
                    with nav_col1:
                        if st.button("⬅️ Previous") and st.session_state.current_page > 0:
                            st.session_state.current_page -= 1
                    with nav_col2:
                        st.write(f"Page {st.session_state.current_page + 1} of {total_pages}")
                    with nav_col3:
                        if st.button("Next ➡️") and st.session_state.current_page < total_pages - 1:
                            st.session_state.current_page += 1
                    
                    # Display current page
                    pdf_display = get_pdf_display(uploaded_pdf, st.session_state.current_page)
                    st.markdown(pdf_display, unsafe_allow_html=True)
                
                with col2:
                    # Get the current page's image path and OCR directory
                    pdf_name = os.path.splitext(uploaded_pdf.name)[0]
                    image_path = os.path.join("pdf_uploads", pdf_name, "images", f"page_{st.session_state.current_page + 1}.png")
                    model_name = st.session_state.selected_model.replace('.', '_')
                    ocr_dir = os.path.join("pdf_uploads", pdf_name, f"ocr_{model_name}")
                    
                    # Add Segregate button above OCR Results
                    if st.button("🔍 Segregate"):
                        with st.spinner("Processing OCR results..."):
                            # First merge OCR results
                            merge_success, merge_message = merge_ocr_results(pdf_name, ocr_dir)
                            if merge_success:
                                # Then segregate the merged results
                                seg_success, seg_message = segregate_ocr_results(pdf_name, os.path.dirname(ocr_dir))
                                if seg_success:
                                    st.success("Successfully processed and segregated questions!")
                                else:
                                    st.error(f"Error segregating questions: {seg_message}")
                            else:
                                st.error(f"Error merging OCR results: {merge_message}")
                    
                    st.write("OCR Results:")
                    
                    # Debug information for paths
                    st.write(f"Debug - Image path: {image_path}")
                    st.write(f"Debug - Image exists: {os.path.exists(image_path)}")
                    st.write(f"Debug - OCR directory: {ocr_dir}")
                    st.write(f"Debug - Model name: {model_name}")
                    
                    # Get or perform OCR
                    ocr_text = get_ocr_result(image_path, ocr_dir)
                    if ocr_text is None and os.path.exists(image_path):
                        with st.spinner("Performing OCR..."):
                            ocr_text = perform_ocr(image_path, ocr_dir)
                    elif not os.path.exists(image_path):
                        st.error(f"Image file not found: {image_path}")
                        ocr_text = "No OCR results available"
                    
                    # Display OCR results
                    st.text_area("Extracted Text", ocr_text, height=400)
                    
                    # Add Refresh OCR button
                    if st.button("🔄 Refresh OCR"):
                        with st.spinner("Performing OCR..."):
                            if os.path.exists(image_path):
                                ocr_text = perform_ocr(image_path, ocr_dir)
                                st.rerun()
                            else:
                                st.error(f"Image file not found: {image_path}")
            else:
                st.error(message)
        
        # Display selected PDF from database
        elif st.session_state.selected_pdf:
            pdf_id, original_filename, upload_date, total_pages = st.session_state.selected_pdf
            
            # Get PDF data from database
            pdf_data = db_manager.get_pdf_data(pdf_id, st.session_state.user['id'])
            if pdf_data:
                pdf_bytes, original_filename, total_pages = pdf_data
                
                # Process PDF if not already processed
                if not st.session_state.pdf_processed:
                    success, message, total_pages = process_pdf_from_bytes(pdf_bytes, original_filename)
                    if success:
                        st.session_state.pdf_processed = True
                        st.session_state.total_pages = total_pages
                    else:
                        st.error(message)
                        return
                
                # Create BytesIO object from PDF data
                pdf_file = BytesIO(pdf_bytes)
                
                # Create two columns for the layout with reduced spacing
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Display PDF preview with navigation
                    st.write(f"PDF Preview: {original_filename}")
                    
                    # Navigation controls
                    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
                    with nav_col1:
                        if st.button("⬅️ Previous") and st.session_state.current_page > 0:
                            st.session_state.current_page -= 1
                    with nav_col2:
                        st.write(f"Page {st.session_state.current_page + 1} of {total_pages}")
                    with nav_col3:
                        if st.button("Next ➡️") and st.session_state.current_page < total_pages - 1:
                            st.session_state.current_page += 1
                    
                    # Display current page
                    pdf_display = get_pdf_display(pdf_file, st.session_state.current_page)
                    st.markdown(pdf_display, unsafe_allow_html=True)
                
                with col2:
                    # Get the current page's image path and OCR directory
                    pdf_name = os.path.splitext(original_filename)[0]
                    image_path = os.path.join("pdf_uploads", pdf_name, "images", f"page_{st.session_state.current_page + 1}.png")
                    model_name = st.session_state.selected_model.replace('.', '_')
                    ocr_dir = os.path.join("pdf_uploads", pdf_name, f"ocr_{model_name}")
                    
                    # Add Segregate button above OCR Results
                    if st.button("🔍 Segregate"):
                        with st.spinner("Processing OCR results..."):
                            # First merge OCR results
                            merge_success, merge_message = merge_ocr_results(pdf_name, ocr_dir)
                            if merge_success:
                                # Then segregate the merged results
                                seg_success, seg_message = segregate_ocr_results(pdf_name, os.path.dirname(ocr_dir))
                                if seg_success:
                                    st.success("Successfully processed and segregated questions!")
                                else:
                                    st.error(f"Error segregating questions: {seg_message}")
                            else:
                                st.error(f"Error merging OCR results: {merge_message}")
                    
                    st.write("OCR Results:")
                    
                    # Debug information for paths
                    st.write(f"Debug - Image path: {image_path}")
                    st.write(f"Debug - Image exists: {os.path.exists(image_path)}")
                    st.write(f"Debug - OCR directory: {ocr_dir}")
                    st.write(f"Debug - Model name: {model_name}")
                    
                    # Get or perform OCR
                    ocr_text = get_ocr_result(image_path, ocr_dir)
                    if ocr_text is None and os.path.exists(image_path):
                        with st.spinner("Performing OCR..."):
                            ocr_text = perform_ocr(image_path, ocr_dir)
                    elif not os.path.exists(image_path):
                        st.error(f"Image file not found: {image_path}")
                        ocr_text = "No OCR results available"
                    
                    # Display OCR results
                    st.text_area("Extracted Text", ocr_text, height=400)
                    
                    # Add Refresh OCR button
                    if st.button("🔄 Refresh OCR"):
                        with st.spinner("Performing OCR..."):
                            if os.path.exists(image_path):
                                ocr_text = perform_ocr(image_path, ocr_dir)
                                st.rerun()
                            else:
                                st.error(f"Image file not found: {image_path}")
            else:
                st.error("Error loading PDF from database")

if __name__ == "__main__":
    main()