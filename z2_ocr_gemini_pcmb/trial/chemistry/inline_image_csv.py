# 🖼️ DISPLAY IMAGES INLINE IN CSV CELLS
# Copy this code into your Jupyter notebook

import pandas as pd
import base64
from IPython.display import HTML, display
import os
from io import BytesIO
from PIL import Image

def image_to_base64(image_path, max_width=200, max_height=300):
    """
    Convert image to base64 string for inline display in HTML
    """
    try:
        if os.path.exists(image_path):
            # Open and resize image
            with Image.open(image_path) as img:
                # Calculate aspect ratio and resize
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                return f'<img src="data:image/png;base64,{img_str}" style="max-width:{max_width}px; max-height:{max_height}px;">'
        else:
            return f'<span style="color:red;">❌ Image not found</span>'
    except Exception as e:
        return f'<span style="color:red;">❌ Error: {str(e)}</span>'

def create_image_html_table(csv_path, num_rows=10):
    """
    Create HTML table with images embedded in cells
    """
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"📊 Loading {len(df)} records from CSV...")
        
        # Fix image paths first
        base_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr/chemistry/Chemistry_Gemini/chem/images/"
        
        # Create a copy for display
        display_df = df.head(num_rows).copy()
        
        # Convert images to base64 HTML
        print("🖼️ Converting images to inline display format...")
        display_df['student_image_display'] = display_df.apply(
            lambda row: image_to_base64(
                os.path.join(base_dir, f"{row['pdf_source']}_page_1.png")
            ), axis=1
        )
        
        # Create HTML table
        html_table = """
        <style>
        .csv-table {
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
        }
        .csv-table th, .csv-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
            vertical-align: top;
        }
        .csv-table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .csv-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .text-cell {
            max-width: 200px;
            word-wrap: break-word;
        }
        .image-cell {
            text-align: center;
            width: 220px;
        }
        </style>
        <table class="csv-table">
        <thead>
            <tr>
                <th>PDF Source</th>
                <th>Student Image</th>
                <th>Human Text</th>
                <th>OCR Text</th>
                <th>Error Type</th>
                <th>Has Errors</th>
            </tr>
        </thead>
        <tbody>
        """
        
        for _, row in display_df.iterrows():
            html_table += f"""
            <tr>
                <td class="text-cell">{row['pdf_source']}</td>
                <td class="image-cell">{row['student_image_display']}</td>
                <td class="text-cell">{str(row['Human_text'])[:100]}...</td>
                <td class="text-cell">{str(row['ocr_text'])[:100]}...</td>
                <td class="text-cell">{row['type_of_error']}</td>
                <td class="text-cell">{'✅' if not row['has_errors'] else '❌'}</td>
            </tr>
            """
        
        html_table += """
        </tbody>
        </table>
        """
        
        return html_table
        
    except Exception as e:
        return f"<p style='color:red;'>❌ Error creating table: {str(e)}</p>"

def display_csv_with_inline_images(csv_path, num_rows=5):
    """
    Display CSV data with images embedded in the table cells
    """
    print("🎯 CREATING CSV TABLE WITH INLINE IMAGES")
    print("=" * 60)
    
    html_table = create_image_html_table(csv_path, num_rows)
    
    print(f"✅ Table created! Displaying first {num_rows} rows with inline images...")
    print("=" * 60)
    
    # Display the HTML table
    display(HTML(html_table))

# Alternative method using pandas styling
def display_csv_with_pandas_styling(csv_path, num_rows=5):
    """
    Alternative method using pandas styling to show images
    """
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        base_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr/chemistry/Chemistry_Gemini/chem/images/"
        
        # Take first few rows
        display_df = df.head(num_rows).copy()
        
        # Function to create image HTML for styling
        def make_image_html(pdf_source):
            image_path = os.path.join(base_dir, f"{pdf_source}_page_1.png")
            return image_to_base64(image_path, max_width=150, max_height=200)
        
        # Apply styling to student_image column
        display_df['student_image'] = display_df['pdf_source'].apply(make_image_html)
        
        # Select columns to display
        cols_to_show = ['pdf_source', 'student_image', 'Human_text', 'ocr_text', 'type_of_error', 'has_errors']
        display_df = display_df[cols_to_show]
        
        # Truncate text columns
        display_df['Human_text'] = display_df['Human_text'].astype(str).str[:80] + '...'
        display_df['ocr_text'] = display_df['ocr_text'].astype(str).str[:80] + '...'
        
        # Style the dataframe
        styled_df = display_df.style.format({'student_image': lambda x: x}, escape=False)
        styled_df = styled_df.set_properties(**{
            'text-align': 'left',
            'vertical-align': 'top',
            'border': '1px solid black'
        })
        
        print("🎯 PANDAS STYLED TABLE WITH INLINE IMAGES")
        print("=" * 60)
        print(f"✅ Displaying first {num_rows} rows...")
        
        return styled_df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Quick display function
def quick_show_images_in_csv():
    """Quick function to display your CSV with inline images"""
    csv_path = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/z2_ocr/chemistry/final.csv"
    
    print("🚀 QUICK DISPLAY: CSV WITH INLINE IMAGES")
    print("=" * 70)
    
    # Method 1: HTML Table
    display_csv_with_inline_images(csv_path, num_rows=3)
    
    print("\n" + "=" * 70)
    print("📊 ALTERNATIVE: PANDAS STYLED TABLE")
    print("=" * 70)
    
    # Method 2: Pandas Styling
    styled_table = display_csv_with_pandas_styling(csv_path, num_rows=3)
    if styled_table is not None:
        display(styled_table)

# Usage instructions
print("""
🎯 USAGE INSTRUCTIONS:
======================

In your Jupyter notebook, run:

1. quick_show_images_in_csv()                    # Show CSV with inline images
2. display_csv_with_inline_images('file.csv', 5) # Custom HTML table
3. display_csv_with_pandas_styling('file.csv', 5) # Pandas styled table

The images will appear INSIDE the table cells, not as separate outputs!
""")

# Uncomment to run immediately:
# quick_show_images_in_csv()