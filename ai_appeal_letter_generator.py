import json
# ------------------ AI FUNCTIONS ---------------------
def extract_patient_info(denial_text):
    """
    Extract the patient's full name and member ID from the denial letter using Gemini.
    Returns a dict: {"Patient Name": ..., "Member ID": ...}
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return {"Patient Name": "", "Member ID": ""}
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = (
            "Extract the patient's full name and member ID from the following insurance denial letter text.  "
            'Return a JSON object with keys "Patient Name" and "Member ID".  '
            "If any information is missing, leave the value empty.  "
            f"Text: {denial_text}"
        )
        response = model.generate_content(prompt)
        try:
            data = json.loads(response.text)
            return {
                "Patient Name": data.get("Patient Name", ""),
                "Member ID": data.get("Member ID", "")
            }
        except Exception:
            return {"Patient Name": "", "Member ID": ""}
    except Exception:
        return {"Patient Name": "", "Member ID": ""}
import streamlit as st
import easyocr
import PyPDF2
import io
import numpy as np
import os
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv

# --------------------- UI HEADER ---------------------
st.set_page_config(page_title="AI Appeal Letter Generator", layout="centered")
st.title('📝 AI Appeal Letter Generator')
st.markdown("""
Upload your **insurance denial letter** and the **doctor’s claim letter** or medical justification.
The AI will extract the text and generate a **professional appeal letter** in seconds.
""")

# ------------------ OCR LOADER -----------------------
@st.cache_resource
def load_ocr_model():
    """Load and cache the EasyOCR reader."""
    return easyocr.Reader(['en'])

# ------------------ FILE PROCESSOR -------------------
def extract_text_from_file(uploaded_file):
    """Extract text from PDF, image, or plain text file."""
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

    # Handle image files (jpg, jpeg, png)
    elif file_type.startswith('image/'):
        image_bytes = uploaded_file.read()
        results = reader.readtext(image_bytes)
        extracted_text = " ".join([res[1] for res in results])
        return extracted_text

    # Handle plain text files
    elif file_type == 'text/plain' or uploaded_file.name.lower().endswith('.txt'):
        return uploaded_file.read().decode('utf-8')

    # Unsupported format
    return "Unsupported file type."

# ------------------ AI FUNCTIONS ---------------------
def get_denial_reason(denial_text):
    """
    Extract the primary reason for denial using Google Generative AI.
    Returns a concise reason like 'Not Medically Necessary'.
    """
    try:
        # Ensure .env is loaded only once and early in the app
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Google API key not found in environment."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = (
            "You are a medical insurance analyst. Your task is to extract the primary reason for denial from the following insurance letter.\n\n"
            "Only return a short phrase such as:\n"
            "- Not Medically Necessary\n"
            "- Experimental Treatment\n"
            "- Coverage Exclusion\n"
            "- Incomplete Documentation\n\n"
            "Text:\n"
            f"{denial_text}\n\n"
            "Denial Reason:"
        )

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error extracting denial reason: {e}"

def get_claim_summary(claim_text):
    """
    Summarize the claim/doctor letter. Extract diagnosis, requested treatment, and justification.
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Google API key not found in environment."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = (
            "You are a medical assistant AI. Read the claim letter below and summarize it into 3 parts:\n"
            "1. Patient diagnosis\n"
            "2. Requested treatment\n"
            "3. Justification for the treatment\n\n"
            f"{claim_text}\n\n"
            "Summary:"
        )

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error extracting claim summary: {e}"

def draft_appeal_letter(denial_reason, claim_summary):
    """
    Use Google Generative AI to generate a professional appeal letter.
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Google API key not found in environment."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = (
            "You are an expert medical appeal writer. Draft a formal appeal letter to an insurance company.\n"
            "Use the provided denial reason and claim summary.\n\n"
            f"Denial Reason: {denial_reason}\n"
            f"Claim Summary: {claim_summary}\n\n"
            "Make it sound professional, persuasive, and medically justified."
        )

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error drafting appeal letter: {e}"

# --------------------- FILE UPLOAD UI ---------------------
st.markdown("### Step 1: Upload Files")
insurance_denial = st.file_uploader('📄 Upload the **Insurance Denial Letter**', type=['pdf', 'txt', 'jpg', 'jpeg', 'png'])
original_claim = st.file_uploader('📄 Upload the **Doctor’s Letter / Claim Document**', type=['pdf', 'txt', 'jpg', 'jpeg', 'png'])

# ------------------- TEXT EXTRACTION VIEW -----------------
denial_text = ""
claim_text = ""


# --- After denial letter upload, extract patient info and denial reason ---
if insurance_denial:
    denial_text = extract_text_from_file(insurance_denial)
    with st.spinner("Extracting patient info and denial reason..."):
        patient_info = extract_patient_info(denial_text)
        denial_info = get_denial_reason(denial_text)
    # Display extracted info section
    #st.markdown("#### 🧑‍⚕️ Extracted Patient & Denial Info")
    #col1, col2, col3 = st.columns(3)
    #col1.metric("Patient Name", patient_info.get("Patient Name") or "-")
    #col2.metric("Member ID", patient_info.get("Member ID") or "-")
    #col3.metric("Denial Reason", denial_info or "-")

    # Denial reason classification table
    common_reasons = [
        "Not Medically Necessary",
        "Experimental Treatment",
        "Coverage Exclusion",
        "Incomplete Documentation",
        "Out of Network",
        "Pre-Authorization Required",
        "Benefit Maximum Reached",
        "Other"
    ]
    st.markdown("#### 📋 Denial Reason Classification")
    table_rows = []
    extracted_reason = (denial_info or "").strip().lower()
    for reason in common_reasons:
        highlight = "✅" if reason.lower() == extracted_reason else ""
        table_rows.append(f"| {reason} | {highlight} |")
    st.markdown("""
| Reason | Extracted |
|--------|-----------|
""" + "\n".join(table_rows))

    with st.expander("📑 Extracted Denial Letter Text"):
        st.text_area("Denial Letter", denial_text, height=200)

if original_claim:
    claim_text = extract_text_from_file(original_claim)
    with st.expander("📑 Extracted Claim Letter Text"):
        st.text_area("Claim Letter", claim_text, height=200)

# -------------------- GENERATE LETTER ---------------------
if insurance_denial and original_claim:
    if st.button("🚀 Generate Appeal Letter"):
        with st.spinner("AI is drafting your appeal letter..."):
            denial_reason = get_denial_reason(denial_text)
            claim_summary = get_claim_summary(claim_text)
            final_letter = draft_appeal_letter(denial_reason, claim_summary)

        st.success("✅ Appeal letter generated successfully!")
        st.subheader("📬 Your Generated Appeal Letter:")
        st.markdown(final_letter)