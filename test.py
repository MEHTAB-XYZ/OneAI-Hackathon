import streamlit as st
import easyocr
import PyPDF2
import io
import numpy as np
import os
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv
import json
from datetime import datetime, timedelta
import re

# --------------------- UI HEADER ---------------------
st.set_page_config(page_title="AI Appeal Letter Generator", layout="centered")
st.title('📝 AI Appeal Letter Generator')
st.markdown("""
Upload your *insurance denial letter* and the *doctor's claim letter* or medical justification.
The AI will extract the text and generate a *professional appeal letter* in seconds.
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

def get_denial_reason(denial_text):
    """
    Extract the primary reason for denial using Google Generative AI.
    Returns a concise reason like 'Not Medically Necessary'.
    """
    try:
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

def draft_appeal_letter(denial_reason, claim_summary, patient_info):
    """
    Use Google Generative AI to generate a professional appeal letter.
    Enhanced with comprehensive prompting for better appeals.
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Google API key not found in environment."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        Role: You are a highly skilled, professional Insurance Appeal Specialist and Medical Documentation Expert. Your core objective is to craft exceptionally persuasive and effective appeal letters for denied insurance claims.

        Task: Generate a compelling appeal letter that directly addresses the denial and advocates for claim approval.

        Patient Information:
        - Name: {patient_info.get('Patient Name', 'Not provided')}
        - Member ID: {patient_info.get('Member ID', 'Not provided')}

        Denial Reason: {denial_reason}
        Claim Summary: {claim_summary}

        Key Requirements:
        1. Clear Intent & Identification: Begin with direct statement of appeal, clearly identifying patient details
        2. Medical Necessity & Justification: Articulate why treatment is essential for patient's health
        3. Direct Refutation of Denial: Systematically address and refute the denial reason with specific facts
        4. Timeliness: Acknowledge appeal timeframe compliance
        5. Professional Tone: Maintain formal, clinical, and authoritative language
        6. Supporting Documentation: Reference attached documents that substantiate medical necessity
        7. Clear Call to Action: Conclude with firm request for reconsideration and approval

        Generate a professional, persuasive appeal letter that follows these guidelines and directly addresses the specific denial reason provided.
        """

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error drafting appeal letter: {e}"

def generate_xai_explanation(denial_reason, denial_text):
    """
    Generate XAI (Explainable AI) explanation for the denial reason.
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Google API key not found."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        Analyze the denial reason and provide an XAI explanation:

        Denial Reason: {denial_reason}
        Denial Text: {denial_text}

        Please provide:
        1. The exact quote from the denial letter stating the reason
        2. A clear explanation of what this means for the patient/provider
        3. Specific evidence or actions needed to overcome this denial

        Format as JSON with keys: "quoted_reason", "explanation", "required_evidence"
        """

        response = model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except:
            return {
                "quoted_reason": denial_reason,
                "explanation": "Standard denial requiring medical justification",
                "required_evidence": "Additional medical documentation needed"
            }
    except Exception as e:
        return {"error": f"XAI generation failed: {e}"}

def predict_confidence_level(denial_reason, claim_summary):
    """
    Predict the confidence level for appeal success.
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Medium"
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        Based on the denial reason and claim summary, predict the likelihood of appeal success:

        Denial Reason: {denial_reason}
        Claim Summary: {claim_summary}

        Rate the confidence level as High, Medium, or Low and provide a brief explanation.
        Consider factors like:
        - Strength of medical evidence
        - Common success rates for this denial type
        - Completeness of documentation
        - Clarity of medical necessity

        Return only: "High", "Medium", or "Low" followed by a brief explanation.
        """

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Medium - Unable to assess: {e}"

def extract_denial_date(denial_text):
    """
    Extract denial date from the denial letter text.
    """
    # Common date patterns
    date_patterns = [
        r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
        r'\b(\d{1,2}\s+\w+\s+\d{2,4})\b',
        r'\b(\w+\s+\d{1,2},?\s+\d{2,4})\b'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, denial_text)
        if matches:
            return matches[0]
    
    return None

def calculate_appeal_deadline(denial_date_str, days=30):
    """
    Calculate appeal deadline based on denial date.
    """
    if not denial_date_str:
        return "Unable to determine deadline - please check your policy"
    
    try:
        # Try to parse various date formats
        for fmt in ('%m/%d/%Y', '%m-%d-%Y', '%B %d, %Y', '%b %d, %Y', '%d %B %Y'):
            try:
                denial_date = datetime.strptime(denial_date_str, fmt)
                deadline = denial_date + timedelta(days=days)
                return deadline.strftime('%B %d, %Y')
            except ValueError:
                continue
        return "Unable to parse date format"
    except Exception as e:
        return f"Error calculating deadline: {e}"

def is_genuine_letter(text, letter_type="denial"):
    """
    Use AI to check if the uploaded text looks like a genuine denial or claim letter.
    Returns True if genuine, False otherwise.
    """
    try:
        load_dotenv(find_dotenv(), override=True)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return False
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = (
            f"You are an insurance expert. Analyze the following text and answer YES or NO: Is this a genuine {letter_type} letter from a real insurance process?\n"
            "If it is a random string, a test, or does not look like a real {letter_type} letter, answer NO.\n"
            f"Text: {text}\n"
            "Answer only YES or NO."
        )
        response = model.generate_content(prompt)
        answer = response.text.strip().upper()
        return answer.startswith("YES")
    except Exception:
        return False

# --------------------- FILE UPLOAD UI ---------------------
st.markdown("### Step 1: Upload Files")
insurance_denial = st.file_uploader('📄 Upload the *Insurance Denial Letter*', type=['pdf', 'txt', 'jpg', 'jpeg', 'png'])
original_claim = st.file_uploader('📄 Upload the *Doctor\'s Letter / Claim Document*', type=['pdf', 'txt', 'jpg', 'jpeg', 'png'])

# ------------------- TEXT EXTRACTION VIEW -----------------
denial_text = ""
claim_text = ""
denial_date = None
# Always define patient_info and denial_info to avoid NameError
patient_info = None
denial_info = None


# --- Only extract details after both documents are uploaded and validated ---
if insurance_denial and original_claim:
    denial_text = extract_text_from_file(insurance_denial)
    claim_text = extract_text_from_file(original_claim)
    valid_denial = is_genuine_letter(denial_text, letter_type="denial")
    valid_claim = is_genuine_letter(claim_text, letter_type="claim")

    if not valid_denial:
        st.error("❌ The uploaded denial letter does not appear to be a genuine insurance denial letter. Please upload a valid document.")
    if not valid_claim:
        st.error("❌ The uploaded claim letter does not appear to be a genuine claim/doctor letter. Please upload a valid document.")

    if valid_denial and valid_claim:
        with st.spinner("Extracting details from both documents..."):
            patient_info = extract_patient_info(denial_text)
            denial_info = get_denial_reason(denial_text)
            denial_date = extract_denial_date(denial_text)
            # claim_text already extracted above

        # Display extracted info section (optional: uncomment if needed)
        # st.markdown("#### 🧑‍⚕️ Extracted Patient & Denial Info")
        # col1, col2, col3 = st.columns(3)
        # col1.metric("Patient Name", patient_info.get("Patient Name") or "Not found")
        # col2.metric("Member ID", patient_info.get("Member ID") or "Not found")
        # col3.metric("Denial Reason", denial_info or "Not found")

        # Appeal deadline calculator
        if denial_date:
            deadline = calculate_appeal_deadline(denial_date)
            st.info(f"📅 *Appeal Deadline Calculator*: Based on denial date {denial_date}, your appeal should be submitted by {deadline}")

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
            highlight = "✅" if reason.lower() in extracted_reason else ""
            table_rows.append(f"| {reason} | {highlight} |")
        st.markdown("""
| Reason | Detected |
|--------|----------|
""" + "\n".join(table_rows))

        with st.expander("📑 Extracted Denial Letter Text"):
            st.text_area("Denial Letter", denial_text, height=200, key="denial_text")
        with st.expander("📑 Extracted Claim Letter Text"):
            st.text_area("Claim Letter", claim_text, height=200, key="claim_text")

# -------------------- GENERATE LETTER ---------------------
if insurance_denial and original_claim:
    if st.button("🚀 Generate Appeal Letter"):
        with st.spinner("AI is drafting your appeal letter..."):
            # Extract all necessary information
            denial_reason = get_denial_reason(denial_text)
            claim_summary = get_claim_summary(claim_text)
            patient_info = extract_patient_info(denial_text)
            
            # Generate main appeal letter
            final_letter = draft_appeal_letter(denial_reason, claim_summary, patient_info)
            
            # Generate XAI explanation
            xai_explanation = generate_xai_explanation(denial_reason, denial_text)
            
            # Predict confidence level
            confidence_prediction = predict_confidence_level(denial_reason, claim_summary)

        st.success("✅ Appeal letter generated successfully!")
        
        # Display XAI Explanation
        st.markdown("### 🔍 Denial Reason Explainer (XAI Layer)")
        if isinstance(xai_explanation, dict) and 'error' not in xai_explanation:
            st.markdown(f"*Quoted Reason:* {xai_explanation.get('quoted_reason', 'N/A')}")
            st.markdown(f"*Explanation:* {xai_explanation.get('explanation', 'N/A')}")
            st.markdown(f"*Required Evidence:* {xai_explanation.get('required_evidence', 'N/A')}")
        else:
            st.warning("Unable to generate detailed XAI explanation")

        # Display Confidence Level
        st.markdown("### 📊 Appeal Success Confidence Level")
        confidence_parts = confidence_prediction.split(' - ', 1)
        confidence_level = confidence_parts[0]
        confidence_explanation = confidence_parts[1] if len(confidence_parts) > 1 else "No explanation provided"
        
        if confidence_level.upper() == "HIGH":
            st.success(f"🟢 *{confidence_level}* - {confidence_explanation}")
        elif confidence_level.upper() == "MEDIUM":
            st.warning(f"🟡 *{confidence_level}* - {confidence_explanation}")
        else:
            st.error(f"🔴 *{confidence_level}* - {confidence_explanation}")

        # Display the appeal letter
        st.markdown("### 📬 Your Generated Appeal Letter")
        st.markdown(final_letter)

        # Required attachments checklist
        st.markdown("### 📋 Required Attachments Checklist")
        st.markdown("""
        Before submitting your appeal, ensure you have attached:
        - [ ] Copy of the original denial letter
        - [ ] All supporting medical documents
        - [ ] Physician's notes and operative reports
        - [ ] Diagnostic test results and lab reports
        - [ ] Treatment guidelines or medical journal articles (if applicable)
        - [ ] Prior authorization numbers (if applicable)
        - [ ] Patient identification verification
        """)

        # Risk assessment
        st.markdown("### ⚠️ Risk Assessment")
        if confidence_level.upper() == "LOW":
            st.error("""
            *High Risk Appeal* - Consider the following:
            - Ensure all requested documentation is complete
            - Strengthen medical necessity arguments
            - Consider consulting with a medical professional
            - Review policy exclusions carefully
            """)
        elif confidence_level.upper() == "MEDIUM":
            st.warning("""
            *Medium Risk Appeal* - Recommendations:
            - Double-check all patient details are accurate
            - Ensure medical necessity is clearly explained
            - Verify all supporting documents are attached
            """)
        else:
            st.success("""
            *Strong Appeal* - You appear to have:
            - Solid medical documentation
            - Clear justification for treatment
            - Proper refutation of denial reason
            """)

        # Download button for the appeal letter
        st.download_button(
            label="📥 Download Appeal Letter",
            data=final_letter,
            file_name="appeal_letter.txt",
            mime="text/plain"
        )

# --------------------- SIDEBAR TOOLS ---------------------
st.sidebar.markdown("## 🛠️ Appeal Tools")

# Claim ID Validation
st.sidebar.markdown("### Claim ID Validation")
claim_id_check = st.sidebar.radio(
    "Are all patient details correct in your documents?",
    ["✅ Yes, all details are present", "❌ Some details are missing"]
)

if claim_id_check == "❌ Some details are missing":
    st.sidebar.error("Please verify patient name, member ID, and policy number before submitting.")

# Appeal deadline reminder
st.sidebar.markdown("### ⏰ Appeal Deadline Reminder")
st.sidebar.info("Most insurance companies require appeals within 30-60 days of the denial date. Check your specific policy for exact deadlines.")

# Help section
st.sidebar.markdown("### 📞 Need Help?")
st.sidebar.markdown("""
- Review your insurance policy for specific appeal procedures
- Consider consulting with a healthcare advocate
- Keep copies of all submitted documents
- Follow up on your appeal status regularly
""")