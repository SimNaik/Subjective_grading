import streamlit as st
import pandas as pd
import os
import requests
from pathlib import Path
import json
from typing import List, Optional

# Import local UI modules
from .utils import (
    extract_pdf_name_from_url,
    validate_pdf_name,
    format_metadata_display,
    get_prompt_version_info,
    create_download_filename,
    validate_ocr_result
)
from .ocr_handler import ocr_handler
from .visualizers import PDFQuestionViewer


@st.cache_data
def load_metadata(hw_solution_with_qb_meta_csv):
    """Load the metadata CSV file with Parquet caching for performance"""
    
    # Define cache path
    cache_path = "data/metadata_cache.parquet"
    
    try:
        # If cache exists, load it
        if os.path.exists(cache_path):
            print("✓ Loading metadata from cached Parquet file")
            return pd.read_parquet(cache_path)
        
        # If no cache, load from CSV and create cache
        print("⏳ No cache found, loading from CSV and creating cache...")
        qb_meta_df = pd.read_csv(hw_solution_with_qb_meta_csv, low_memory=False)
        
        # --- Data processing ---
        if 'UPLOADED_ANS' in qb_meta_df.columns:
            qb_meta_df['pdf_name'] = qb_meta_df['UPLOADED_ANS'].apply(extract_pdf_name_from_url)
            
            # Add cleaned_solution column
            try:
                from data_processing.preprocessor import TextPreprocessor
                text_preprocessor = TextPreprocessor()
                qb_meta_df['cleaned_solution'] = qb_meta_df['textsolutions'].apply(text_preprocessor.process_solution)
                print("✓ Successfully added cleaned_solution column")
            except Exception as e:
                print(f"⚠️ Could not add cleaned_solution column: {e}")
                qb_meta_df['cleaned_solution'] = ""
        else:
            st.error("UPLOADED_ANS column not found in metadata CSV")
            return pd.DataFrame()
            
        # --- Save to cache ---
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            qb_meta_df.to_parquet(cache_path)
            print(f"✓ Metadata cached successfully to {cache_path}")
        except Exception as e:
            st.warning(f"⚠️ Could not save metadata cache: {e}")
            
        return qb_meta_df
        
    except FileNotFoundError:
        st.error(f"Metadata CSV file not found: {hw_solution_with_qb_meta_csv}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading metadata: {str(e)}")
        return pd.DataFrame()


class SubjectiveAssessment:
    """
    Main interface for Subjective Assessment System.
    Handles PDF processing, OCR, and grading functionality.
    """

    def __init__(self, pdf_dir: str, image_dir: str, cache_dir: str, hw_solution_with_qb_meta_csv: str):
        """
        Initialize the Subjective Assessment interface.
        
        Args:
            pdf_dir: Directory containing PDF files
            image_dir: Directory for storing images
            cache_dir: Directory for OCR cache
            hw_solution_with_qb_meta_csv: Path to the metadata CSV file
        """
        self.pdf_dir = pdf_dir
        self.image_dir = image_dir
        self.cache_dir = cache_dir

        # Ensure directories exist
        for dir_path in [pdf_dir, image_dir, cache_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

        # Load metadata
        self.qb_meta_df = load_metadata(hw_solution_with_qb_meta_csv)

    def get_existing_pdfs(self) -> List[str]:
        """Get list of existing PDF files in pdf_dir"""
        try:
            pdf_files = []
            for file in os.listdir(self.pdf_dir):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(file)
            return sorted(pdf_files)
        except FileNotFoundError:
            return []

    def download_pdf(self, pdf_name: str, base_url: str) -> bool:
        """
        Download PDF from the given base URL
        
        Args:
            pdf_name: Name of the PDF file to download
            base_url: Base URL for PDF downloads
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            pdf_url = f"{base_url}{pdf_name}"
            pdf_path = os.path.join(self.pdf_dir, pdf_name)

            # Check if file already exists
            if os.path.exists(pdf_path):
                st.info(f"PDF {pdf_name} already exists in {self.pdf_dir}")
                return True

            # Download the PDF
            with st.spinner(f"Downloading {pdf_name}..."):
                response = requests.get(pdf_url, stream=True)
                response.raise_for_status()

                with open(pdf_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                st.success(f"Successfully downloaded {pdf_name}")
                return True

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to download PDF: {str(e)}")
            return False
        except Exception as e:
            st.error(f"Unexpected error during download: {str(e)}")
            return False

    #@st.cache_data
    def get_pdf_metadata(self, pdf_name: str) -> Optional[pd.DataFrame]:
        """
        Get metadata for a specific PDF
        
        Args:
            pdf_name: Name of the PDF file
            
        Returns:
            DataFrame with metadata for the PDF
        """
        if self.qb_meta_df.empty:
            return None

        # Filter metadata for the specific PDF
        pdf_metadata = self.qb_meta_df[self.qb_meta_df['pdf_name'] == pdf_name]
        return pdf_metadata if not pdf_metadata.empty else None

    def display_pdf_info(self, pdf_name: str):
        """Display information about the selected PDF"""
        metadata = self.get_pdf_metadata(pdf_name)

        if metadata is not None:
            st.subheader("PDF Metadata")

            # Display basic info
            if 'SUBJECT' in metadata.columns:
                subjects = metadata['SUBJECT'].unique()
                st.write(f"**Subject(s):** {', '.join(subjects)}")

            if 'TEST_NAME' in metadata.columns:
                test_names = metadata['TEST_NAME'].unique()
                st.write(f"**Test Name(s):** {', '.join(test_names)}")

            if 'Question_no' in metadata.columns:
                question_count = len(metadata['Question_no'].unique())
                st.write(f"**Number of Questions:** {question_count}")

            # Display detailed metadata table (excluding info already shown above)
            st.subheader("Detailed Metadata")
            display_columns = ['Question_no', 'QB_ID', 'Marks', 'cleaned_solution']
            available_columns = [col for col in display_columns if col in metadata.columns]

            if available_columns:
                st.dataframe(
                    metadata[available_columns].sort_values('Question_no' if 'Question_no' in available_columns else available_columns[0]),
                    use_container_width=True
                )
        else:
            st.warning(f"No metadata found for PDF: {pdf_name}")

    def run_ocr_processing(self, pdf_path: str, pdf_name: str, prompt_version: str) -> Optional[dict]:
        """Run OCR processing with the selected prompt version"""
        if not ocr_handler.is_available:
            st.error("OCR modules are not available. Please check your installation.")
            return None

        try:
            # Get OCR configuration from config file
            from config_manager import ConfigManager
            config_manager = ConfigManager()
            ocr_config = config_manager.get_ocr_config()

            # Use the configured cache directory
            cache_dir = ocr_config.get('default_cache_dir', './data/ocr_cache')

            # Ensure cache directory is absolute path
            if not os.path.isabs(cache_dir):
                cache_dir = os.path.join(os.getcwd(), cache_dir)

            # Get metadata for the PDF
            metadata = self.get_pdf_metadata(pdf_name)
            if metadata is None:
                st.error(f"No metadata found for PDF: {pdf_name}")
                return None

            # Prepare test dataframe
            test_df = metadata[['content', 'Question_no', 'Marks', 'QB_ID', 'textsolutions', 'streams', 'oldtags', 'cleaned_solution']].sort_values(by='Question_no')

            # Generate question list (interleaved with solutions for v12)
            with st.spinner("Generating question list..."):
                if prompt_version == 'v12':
                    questions_list = ocr_handler.get_interleaved_question_solution_list(test_df, self.image_dir)
                    st.info(f"Generated interleaved question-solution list for QB-guided assessment")
                else:
                    questions_list = ocr_handler.get_question_list(test_df, self.image_dir)

            if not questions_list:
                st.error("Failed to generate question list")
                return None

            if prompt_version == 'v12':
                st.info(f"Generated {len(questions_list)} items (questions + QB solutions)")
            else:
                st.info(f"Generated {int(len(questions_list) / 2)} question items")

            # Set up output folder using config
            output_folder = os.path.join(cache_dir, "ocr_files")
            os.makedirs(output_folder, exist_ok=True)

            # Show cache info
            st.info(f"💾 Using cache directory: {cache_dir}")

            # Run OCR processing
            with st.spinner(f"Running OCR with prompt version {prompt_version.upper()}..."):
                ocr_result = ocr_handler.run_ocr_processing(
                    pdf_path,
                    questions_list,
                    output_folder,
                    cache_dir,  # Use config-based cache directory
                    prompt_version
                )

            return ocr_result

        except Exception as e:
            st.error(f"Error during OCR processing: {str(e)}")
            return None

    def _render_visualization_section(self, pdf_path: str, pdf_name: str):
        """Render the visualization section for PDF and question analysis"""
        st.header("🔍 Visualization & Analysis")

        # Check if we have OCR results to visualize
        if (hasattr(st.session_state, 'ocr_results') and
            hasattr(st.session_state, 'current_pdf_path') and
            hasattr(st.session_state, 'questions_list')):

            ocr_results = st.session_state.ocr_results
            current_pdf_path = st.session_state.current_pdf_path
            questions_list = st.session_state.questions_list
            metadata = st.session_state.get('current_pdf_metadata', pd.DataFrame())

            # Only show visualization if we have results for the current PDF
            if current_pdf_path == pdf_path and ocr_results:
                st.info(f"📊 Visualizing results for {pdf_name} ({len(ocr_results)} questions)")

                # Display Assessment Summary DataFrame (persistent)
                try:
                    from .components.assessment_summary import AssessmentSummaryRenderer, PromptVersionComparison
                    assessment_renderer = AssessmentSummaryRenderer()
                    prompt_version = getattr(st.session_state, 'prompt_version', None)

                    if prompt_version:
                        assessment_renderer.render_assessment_summary(
                            ocr_results=ocr_results,
                            prompt_version=prompt_version
                        )

                    # Add comparison functionality if we have multiple versions
                    st.markdown("---")
                    with st.expander("🔄 Compare with Other Prompt Versions"):
                        st.write("Compare assessment results between different prompt versions")

                        # Version selection for comparison
                        available_versions = ['v8', 'v9', 'v10', 'v11', 'v12']
                        current_version = prompt_version if prompt_version in available_versions else 'v8'

                        col1, col2 = st.columns(2)
                        with col1:
                            version1 = st.selectbox("First Version", available_versions,
                                                  index=available_versions.index(current_version) if current_version in available_versions else 0)
                        with col2:
                            version2 = st.selectbox("Second Version", available_versions,
                                                  index=available_versions.index('v12') if 'v12' in available_versions else -1)

                        if st.button("🔍 Run Comparison") and version1 != version2:
                            st.info("Comparison functionality requires OCR results from both versions. This is a placeholder for future implementation.")
                            st.write(f"Would compare {version1} vs {version2}")

                    st.markdown("---")
                except Exception as e:
                    st.error(f"Error rendering assessment summary: {str(e)}")
                    st.write(f"Debug: {str(e)}")

                # Initialize and render the synchronized viewer
                try:
                    # Get prompt version from session state
                    prompt_version = getattr(st.session_state, 'prompt_version', None)

                    pdf_question_viewer = PDFQuestionViewer(
                        pdf_path=pdf_path,
                        cache_dir=self.cache_dir,
                        ocr_results=ocr_results,
                        questions_list=questions_list,
                        metadata=metadata,
                        prompt_version=prompt_version
                    )

                    pdf_question_viewer.render_viewer()

                except Exception as e:
                    st.error(f"Error initializing visualization: {str(e)}")
                    st.write("**Debug Info:**")
                    st.write(f"- PDF Path: {pdf_path}")
                    st.write(f"- OCR Results Count: {len(ocr_results) if ocr_results else 0}")
                    st.write(f"- Questions List Count: {len(questions_list) if questions_list else 0}")
                    st.write(f"- Metadata Shape: {metadata.shape if not metadata.empty else 'Empty'}")
            else:
                st.info("🔄 OCR results available, but not for the currently selected PDF. Please run OCR processing first.")
        else:
            st.info("🚀 Run OCR processing first to enable visualization features.")

            # Show what's available for visualization
            if st.button("🔍 Check Visualization Status"):
                st.write("**Visualization Requirements:**")
                st.write(f"- OCR Results: {'✓' if hasattr(st.session_state, 'ocr_results') else '✗'}")
                st.write(f"- PDF Path: {'✓' if hasattr(st.session_state, 'current_pdf_path') else '✗'}")
                st.write(f"- Questions List: {'✓' if hasattr(st.session_state, 'questions_list') else '✗'}")
                st.write(f"- Current PDF: {pdf_name}")

                if hasattr(st.session_state, 'current_pdf_path'):
                    st.write(f"- Stored PDF: {os.path.basename(st.session_state.current_pdf_path)}")

    def show(self):
        """Main method to display the Streamlit interface."""
        st.set_page_config(
            page_title="Subjective Assessment System",
            page_icon="🎓",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # PDF Selection Section
        st.header("📄 PDF Selection")

        # Get existing PDFs
        existing_pdfs = self.get_existing_pdfs()

        # Create two columns for input methods
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Select Existing PDF")
            if existing_pdfs:
                selected_pdf = st.selectbox(
                    "Choose from available PDFs:",
                    options=[""] + existing_pdfs,
                    key="existing_pdf_select"
                )
            else:
                st.info("No PDFs found in the PDF directory")
                selected_pdf = ""

        with col2:
            st.subheader("Add New PDF")
            new_pdf_name = st.text_input(
                "Enter PDF name to download:",
                placeholder="e.g., 100047465393540311181708431172.pdf",
                key="new_pdf_input"
            )

            from config import PDF_BASE_URL
            download_button = st.button("Download PDF", key="download_btn")

            if download_button and new_pdf_name:
                if self.download_pdf(new_pdf_name, PDF_BASE_URL):
                    st.rerun()  # Refresh to update the dropdown

        # Determine which PDF to work with
        current_pdf = ""
        if selected_pdf:
            current_pdf = selected_pdf
        elif new_pdf_name and os.path.exists(os.path.join(self.pdf_dir, new_pdf_name)):
            current_pdf = new_pdf_name

        # Display PDF information if a PDF is selected
        if current_pdf:
            st.markdown("---")
            st.header(f"📊 Information for: {current_pdf}")
            self.display_pdf_info(current_pdf)

            # PDF file path for further processing
            pdf_path = os.path.join(self.pdf_dir, current_pdf)
            st.info(f"PDF Path: {pdf_path}")

            # OCR Processing Section
            st.markdown("---")
            st.header("🔄 OCR Processing")

            if ocr_handler.is_available:
                # Prompt version selection
                col1, col2 = st.columns([2, 1])

                with col1:
                    prompt_versions = get_prompt_version_info()

                    selected_prompt = st.selectbox(
                        "Select Prompt Version:",
                        options=list(prompt_versions.keys()),
                        format_func=lambda x: prompt_versions[x],
                        key="prompt_version_select"
                    )

                    st.info(f"**Selected:** {prompt_versions[selected_prompt]}")

                with col2:
                    run_ocr_button = st.button(
                        "🚀 Run OCR",
                        type="primary",
                        use_container_width=True,
                        key="run_ocr_btn"
                    )

                # Run OCR processing
                if run_ocr_button:
                    if os.path.exists(pdf_path):
                        st.info(f"Starting OCR processing with {selected_prompt.upper()} prompt...")

                        # Run OCR processing
                        ocr_result = self.run_ocr_processing(pdf_path, current_pdf, selected_prompt)

                        if ocr_result and validate_ocr_result(ocr_result):
                            st.success("OCR processing completed successfully!")

                            # Display results
                            st.subheader("📊 OCR Results")

                            # Show summary
                            if isinstance(ocr_result, list) and len(ocr_result) > 0:
                                st.write(f"**Questions processed:** {len(ocr_result)}")
                                st.info("📊 Assessment summary and detailed analysis available in the Visualization section below.")

                                # Option to download full results
                                if st.button("📥 Download Full Results"):
                                    # Convert to JSON string for download
                                    json_str = json.dumps(ocr_result, indent=2, ensure_ascii=False)
                                    download_filename = create_download_filename(current_pdf, selected_prompt)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_str,
                                        file_name=download_filename,
                                        mime="application/json"
                                    )

                                # Store results for visualization
                                st.session_state.ocr_results = ocr_result
                                st.session_state.current_pdf_path = pdf_path
                                st.session_state.current_pdf_metadata = self.get_pdf_metadata(current_pdf)
                                st.session_state.prompt_version = selected_prompt

                                # Get questions list for visualization
                                metadata = self.get_pdf_metadata(current_pdf)
                                if metadata is not None:
                                    test_df = metadata[['content', 'Question_no', 'Marks', 'QB_ID', 'textsolutions', 'streams', 'oldtags', 'cleaned_solution']].sort_values(by='Question_no')
                                    questions_list = ocr_handler.get_question_list(test_df, self.image_dir)
                                    st.session_state.questions_list = questions_list
                                else:
                                    st.session_state.questions_list = []
                            else:
                                st.write("No results to display")
                        else:
                            st.error("OCR processing failed. Please check the logs for details.")
                    else:
                        st.error(f"PDF file not found: {pdf_path}")
            else:
                st.error("OCR functionality is not available. Please check your installation and ensure all required modules are installed.")

                # Show detailed status
                status = ocr_handler.get_availability_status()
                with st.expander("View Detailed Status"):
                    for module, available in status.items():
                        icon = "✓" if available else "✗"
                        st.write(f"{icon} {module}: {'Available' if available else 'Not Available'}")

            # Visualization Section
            st.markdown("---")
            self._render_visualization_section(pdf_path, current_pdf)

        # Show metadata statistics
        if not self.qb_meta_df.empty:
            st.sidebar.header("📈 Metadata Statistics")
            st.sidebar.write(f"Total records: {len(self.qb_meta_df)}")
            if 'SUBJECT' in self.qb_meta_df.columns:
                subject_counts = self.qb_meta_df['SUBJECT'].value_counts()
                st.sidebar.write("**Subject distribution:**")
                st.sidebar.dataframe(subject_counts)


if __name__ == "__main__":
    # For testing purposes
    interface = SubjectiveAssessment(
        pdf_dir="./data/pdfs",
        image_dir="./data/images",
        cache_dir="./data/ocr_cache",
        hw_solution_with_qb_meta_csv="./data/hw_df_with_solutions_and_questions.csv"
    )
