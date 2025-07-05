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
    Extracts structured information from a denial letter using Gemini.
    Returns a dictionary with keys: reason, quote, treatment, policy_clause. If error, returns {'error': ...}
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return {"error": "Google API key not found in environment."}
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = (
            "You are a claims expert reviewing an insurance denial letter. Identify the following:\n"
            "1. Primary reason for denial (e.g., Not Medically Necessary, Experimental Treatment)\n"
            "2. Specific phrase or sentence from the denial letter that explains the reason\n"
            "3. Mentioned procedure/treatment or diagnosis being denied\n"
            "4. Any referenced insurance policy clause or rule (if present)\n\n"
            "Text:\n"
            f"{denial_text}\n\n"
            "Output format:\nReason:\nQuote:\nTreatment:\nPolicy Clause:"
        )

        response = model.generate_content(prompt)
        output = response.text.strip()

        # Parse the output into fields
        fields = {"reason": "", "quote": "", "treatment": "", "policy_clause": ""}
        for line in output.splitlines():
            if line.strip().lower().startswith("reason:"):
                fields["reason"] = line.split(":", 1)[-1].strip()
            elif line.strip().lower().startswith("quote:"):
                fields["quote"] = line.split(":", 1)[-1].strip()
            elif line.strip().lower().startswith("treatment:"):
                fields["treatment"] = line.split(":", 1)[-1].strip()
            elif line.strip().lower().startswith("policy clause:"):
                fields["policy_clause"] = line.split(":", 1)[-1].strip()
        return fields
    except Exception as e:
        return {"error": f"Error extracting denial info: {e}"}

def get_claim_summary(claim_text):
    """
    Extracts a deep structured summary from a claim letter using Gemini.
    Returns a dictionary with keys: diagnosis, treatment, justification, symptoms, functional_impact, urgency. If error, returns {'error': ...}
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return {"error": "Google API key not found in environment."}
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = (
            "You are a medical assistant reviewing a claim letter. Extract the following structured information:\n"
            "1. Diagnosis\n"
            "2. Treatment requested\n"
            "3. Medical justification for treatment\n"
            "4. Key symptoms experienced by the patient\n"
            "5. How the condition affects the patient’s daily functioning\n"
            "6. Urgency or time sensitivity of the treatment\n\n"
            "Text:\n"
            f"{claim_text}\n\n"
            "Respond with the following format:\nDiagnosis:\nTreatment:\nJustification:\nSymptoms:\nFunctional Impact:\nUrgency:"
        )

        response = model.generate_content(prompt)
        output = response.text.strip()

        # Parse the output into fields
        fields = {
            "diagnosis": "",
            "treatment": "",
            "justification": "",
            "symptoms": "",
            "functional_impact": "",
            "urgency": ""
        }
        for line in output.splitlines():
            if line.strip().lower().startswith("diagnosis:"):
                fields["diagnosis"] = line.split(":", 1)[-1].strip()
            elif line.strip().lower().startswith("treatment:"):
                fields["treatment"] = line.split(":", 1)[-1].strip()
            elif line.strip().lower().startswith("justification:"):
                fields["justification"] = line.split(":", 1)[-1].strip()
            elif line.strip().lower().startswith("symptoms:"):
                fields["symptoms"] = line.split(":", 1)[-1].strip()
            elif line.strip().lower().startswith("functional impact:"):
                fields["functional_impact"] = line.split(":", 1)[-1].strip()
            elif line.strip().lower().startswith("urgency:"):
                fields["urgency"] = line.split(":", 1)[-1].strip()
        return fields
    except Exception as e:
        return {"error": f"Error extracting claim summary: {e}"}

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

if insurance_denial:
    denial_text = extract_text_from_file(insurance_denial)
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
            # Extract denial info
            denial_info = get_denial_reason(denial_text)
            claim_info = get_claim_summary(claim_text)
            # For draft_appeal_letter, use denial_info['reason'] if available, else pass blank
            denial_reason_for_letter = denial_info.get('reason', '') if isinstance(denial_info, dict) else ''
            # For draft_appeal_letter, use claim_info['justification'] if available, else pass blank (or pass the whole dict as string)
            claim_summary_for_letter = claim_info.get('justification', '') if isinstance(claim_info, dict) else ''
            final_letter = draft_appeal_letter(denial_reason_for_letter, claim_summary_for_letter)

        # Show denial info
        if "error" in denial_info:
            st.error(f"❌ Error extracting denial info: {denial_info['error']}")
        else:
            st.subheader("🔍 AI-Extracted Denial Insights")
            st.markdown(f"**• Reason:** {denial_info.get('reason', 'N/A')}")
            st.markdown(f"**• Quote:** {denial_info.get('quote', 'N/A')}")
            st.markdown(f"**• Treatment:** {denial_info.get('treatment', 'N/A')}")
            st.markdown(f"**• Policy Clause:** {denial_info.get('policy_clause', 'N/A')}")

        # Show claim info
        if "error" in claim_info:
            st.error(f"❌ Error extracting claim summary: {claim_info['error']}")
        else:
            st.subheader("📋 AI-Extracted Claim Summary")
            st.markdown(f"**• Diagnosis:** {claim_info.get('diagnosis', 'N/A')}")
            st.markdown(f"**• Treatment:** {claim_info.get('treatment', 'N/A')}")
            st.markdown(f"**• Justification:** {claim_info.get('justification', 'N/A')}")
            st.markdown(f"**• Symptoms:** {claim_info.get('symptoms', 'N/A')}")
            st.markdown(f"**• Functional Impact:** {claim_info.get('functional_impact', 'N/A')}")
            st.markdown(f"**• Urgency:** {claim_info.get('urgency', 'N/A')}")

        st.success("✅ Appeal letter generated successfully!")
        st.subheader("📬 Your Generated Appeal Letter:")
        st.markdown(final_letter)
