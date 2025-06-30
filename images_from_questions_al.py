#here i am specifying the location of the row d the name of the image where the csv is converted into df then the column cotent has the images taken 
import os
import pandas as pd
from render_and_save_qb_questions import visualize_and_save_question, batch_save_questions_as_images, set_image_base_url

# Read the CSV into a DataFrame
qb_meta_df = pd.read_csv("/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/HW_DF/hw_df_with_solutions_and_questions.csv")

# Configure image base URL (optional)
set_image_base_url("https://your-cdn.com/images/")

# Define the directory to save the images
image_dir = "/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/images"

# Create the directory if it does not exist
os.makedirs(image_dir, exist_ok=True)

# **Process the specific row (row 18, index 17)**
row_18 = qb_meta_df.iloc[17]  # Access row at index 17 (row 18 in human terms)

# Construct the image filename with the full path
image_filename = os.path.join(image_dir, "question_18.png")

# Access the 'content' from row 18 and save it as an image
visualize_and_save_question(row_18['content'], image_filename)

# Print confirmation
print(f"Saved image for row 18 as '{image_filename}'")
