import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# === Load API Key ===
load_dotenv()

# Fetch the API Key
api_key = os.getenv("GOOGLE_GEMINI_API")

# Check if the API Key is loaded correctly
if api_key is None:
    st.error("API Key is missing! Please check your .env file.")
else:
    st.success("API Key loaded successfully.")

# Configure the Gemini API with the loaded API Key
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

# Test the configuration
st.write("Gemini model is configured!")
