#images_for gemini model to generate coords
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os

# Set your API key here
api_key = "AIzaSyAO0XQdLaNbd9xtHSIqP4oUhwB3uteh14Q"

# Create a GenAI client with the API key
client = genai.Client(api_key=api_key)

# Open the image
image_path = '/Users/simrannaik/Desktop/solution_improvement/ds-prototypes/subjective_grading/solution_improvement/01_1002115268961841141690701450/page_1.png'
image = Image.open(image_path)

# Define your text input
text_input = ''

# Send request to the GenAI model
response = client.models.generate_content(
    model="gemini-2.0-flash-preview-image-generation",
    contents=[text_input, image],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)

# Process the response
for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)  # Print the text response
    elif part.inline_data is not None:
        # Load the image data from the response
        generated_image = Image.open(BytesIO(part.inline_data.data))

        # Save the generated image to a file
        output_image_path = '/path/to/save/generated_image.png'  # Specify your desired file path here
        generated_image.save(output_image_path)  # Save the image

        # Show the generated image
        generated_image.show()  # Optionally display the image

        # Print the output path
        print(f"Image saved at: {output_image_path}")
