import json
import tempfile
import webbrowser
from docx import Document
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

# ------------------ OCR LOADER ----------------------w-
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

def extract_insurance_details(denial_text):
    """
    Extract insurance company name, address, policy number, and claim number from the denial letter using Gemini.
    Returns a dict with keys: 'Insurance Company Name', 'Insurance Company Address', 'Policy Number', 'Claim Number'.
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return {"Insurance Company Name": "", "Insurance Company Address": "", "Policy Number": "", "Claim Number": ""}
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = (
            "Extract the insurance company name, address, policy number, and claim number from the following insurance denial letter text. "
            'Return a JSON object with keys "Insurance Company Name", "Insurance Company Address", "Policy Number", and "Claim Number". '
            "If any information is missing, leave the value empty. "
            f"Text: {denial_text}"
        )
        response = model.generate_content(prompt)
        try:
            data = json.loads(response.text)
            return {
                "Insurance Company Name": data.get("Insurance Company Name", ""),
                "Insurance Company Address": data.get("Insurance Company Address", ""),
                "Policy Number": data.get("Policy Number", ""),
                "Claim Number": data.get("Claim Number", "")
            }
        except Exception:
            return {"Insurance Company Name": "", "Insurance Company Address": "", "Policy Number": "", "Claim Number": ""}
    except Exception:
        return {"Insurance Company Name": "", "Insurance Company Address": "", "Policy Number": "", "Claim Number": ""}

def draft_appeal_letter(denial_reason, claim_summary, insurance_details, patient_info):
    """
    Use Google Generative AI to generate a professional, finished, ready-to-send appeal letter with all details filled in.
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Google API key not found in environment."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = (
            "You are an expert medical appeal writer. Draft a complete, formal, and ready-to-send appeal letter to an insurance company.\n"
            "Use all the provided information below. The letter should be fully finished, professional, and require no further editing.\n"
            f"Insurance Company Name: {insurance_details.get('Insurance Company Name', '')}\n"
            f"Insurance Company Address: {insurance_details.get('Insurance Company Address', '')}\n"
            f"Policy Number: {insurance_details.get('Policy Number', '')}\n"
            f"Claim Number: {insurance_details.get('Claim Number', '')}\n"
            f"Patient Name: {patient_info.get('Patient Name', '')}\n"
            f"Member ID: {patient_info.get('Member ID', '')}\n"
            f"Denial Reason: {denial_reason}\n"
            f"Claim Summary: {claim_summary}\n"
            "Do not include any placeholders or instructions to add more details.\n"
            "The letter should be addressed to the insurance company, reference the denial, and clearly and persuasively argue for approval based on the claim summary.\n"
            "Close with a professional sign-off."
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

# --- Only extract details after both documents are uploaded ---
if insurance_denial and original_claim:
    denial_text = extract_text_from_file(insurance_denial)
    claim_text = extract_text_from_file(original_claim)
    with st.spinner("Extracting all details from denial and claim letters..."):
        patient_info = extract_patient_info(denial_text)
        denial_info = get_denial_reason(denial_text)
        insurance_details = extract_insurance_details(denial_text)
        # Use AI to extract a concise, plain-language explanation from the denial letter
        try:
            load_dotenv(find_dotenv(), override=True)
            api_key = os.environ.get("GOOGLE_API_KEY")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            explanation_prompt = (
                "Given the following insurance denial letter and claim letter, provide a short, plain-language summary (1-2 sentences) explaining why the claim was denied. Do not quote the letter, just summarize the main reason in simple terms.\n"
                f"Denial Reason: {denial_info}\n"
                f"Denial Letter: {denial_text}\n"
                f"Claim Letter: {claim_text}\n"
                "Explanation:"
            )
            explanation_response = model.generate_content(explanation_prompt)
            denial_explanation = explanation_response.text.strip()
        except Exception:
            denial_explanation = "(Could not extract simple explanation.)"
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

    # Denial reason explanation and overcoming statement
    st.markdown("#### ℹ️ Denial Reason Explanation")
    if denial_info and denial_info != "-":
        st.write(f"**Explanation:** {denial_explanation}")
        st.info("The appeal letter will address this reason and work on overcoming it with supporting evidence and arguments.")
    else:
        st.write("No specific denial reason was extracted.")

    with st.expander("📑 Extracted Denial Letter Text"):
        st.text_area("Denial Letter", denial_text, height=200)
    with st.expander("📑 Extracted Claim Letter Text"):
        st.text_area("Claim Letter", claim_text, height=200)

    if st.button("🚀 Generate Appeal Letter"):
        with st.spinner("AI is drafting your appeal letter..."):
            # Use the extracted details for a fully filled letter
            final_letter = draft_appeal_letter(
                denial_info,
                get_claim_summary(claim_text),
                insurance_details,
                patient_info
            )

        st.success("✅ Appeal letter generated successfully!")
        st.subheader("📬 Your Generated Appeal Letter:")
        st.markdown(final_letter)

        # Generate .docx file
        doc = Document()
        for para in final_letter.split('\n'):
            doc.add_paragraph(para)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmpfile:
            doc.save(tmpfile.name)
            docx_path = tmpfile.name
        with open(docx_path, "rb") as f:
            st.download_button(
                label="📥 Download Appeal Letter as .docx",
                data=f,
                file_name="appeal_letter.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        # Open .docx in new tab (will prompt download in most browsers, but user can open in Word/Google Docs)
        webbrowser.open_new_tab(f"file://{docx_path}")