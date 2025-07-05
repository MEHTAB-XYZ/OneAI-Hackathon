
import streamlit as st
import easyocr
import PyPDF2
import io
import numpy as np

# Set the title of the app
st.title('AI Appeal Letter Generator')

@st.cache_resource
def load_ocr_model():
    """Load and cache the EasyOCR reader."""
    return easyocr.Reader(['en'])

def extract_text_from_file(uploaded_file):
    """Extract text from an uploaded file using OCR for images and PyPDF2 for PDFs."""
    reader = load_ocr_model()
    if uploaded_file is None:
        return ""
    file_type = uploaded_file.type
    # Handle PDF files
    if file_type == 'application/pdf' or uploaded_file.name.lower().endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    # Handle image files (jpg, jpeg, png, etc.)
    elif file_type.startswith('image/'):
        image_bytes = uploaded_file.read()
        image_array = np.frombuffer(image_bytes, np.uint8)
        # Use easyocr to read text from image
        results = reader.readtext(image_bytes)
        extracted_text = " ".join([res[1] for res in results])
        return extracted_text
    # Handle text files
    elif file_type == 'text/plain' or uploaded_file.name.lower().endswith('.txt'):
        return uploaded_file.read().decode('utf-8')
    # Handle docx files (optional, not implemented here)
    else:
        return "Unsupported file type."
insurance_denial = st.file_uploader('1. Upload the Insurance Denial Letter', type=['txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg'])

# File uploader for the original claim or doctor's letter
original_claim = st.file_uploader("2. Upload the Original Claim or Doctor's Letter", type=['txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg'])

# Display extracted text for denial letter
if insurance_denial is not None:
    denial_text = extract_text_from_file(insurance_denial)
    st.subheader('Extracted Text from Denial Letter:')
    st.text_area('Denial Letter Text', denial_text, height=200)

# Display extracted text for claim letter
if original_claim is not None:
    claim_text = extract_text_from_file(original_claim)
    st.subheader('Extracted Text from Claim Letter:')
    st.text_area('Claim Letter Text', claim_text, height=200)
