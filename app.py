import streamlit as st
import pandas as pd
import pdfplumber
import docx2txt
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set page config
st.set_page_config(page_title="📄 AI Resume Analyzer", layout="wide")

# Title
st.title("📄 AI-Powered Resume Analyzer")

# Upload Resume
st.sidebar.header("📂 Upload Your Resume")
uploaded_file = st.sidebar.file_uploader("Choose a PDF or DOCX file", type=["pdf", "docx"])

# Function to extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file):
    return docx2txt.process(file)

# Function to analyze resume
def analyze_resume(text):
    skills = ["Python", "Machine Learning", "Data Science", "SQL", "Excel", "Power BI", "Tableau", "Deep Learning", "JavaScript", "Cloud Computing", "Project Management"]
    found_skills = [skill for skill in skills if re.search(rf'\b{skill}\b', text, re.IGNORECASE)]
    word_count = len(text.split())
    ats_friendly = "Yes" if word_count > 200 and len(found_skills) >= 3 else "No"
    
    return {
        "Word Count": word_count,
        "Skills Found": found_skills,
        "ATS Friendly": ats_friendly
    }

# Function to score resume
def resume_score(text):
    ideal_resume = "Data Scientist Machine Learning Python SQL Deep Learning Cloud Computing"
    vectorizer = CountVectorizer().fit_transform([text, ideal_resume])
    vectors = vectorizer.toarray()
    score = cosine_similarity([vectors[0]], [vectors[1]])[0][0] * 100
    return round(score, 2)

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if file_extension == "pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_extension == "docx":
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("⚠️ Unsupported file format. Please upload a PDF or DOCX file.")
        resume_text = None
    
    if resume_text:
        st.subheader("📜 Resume Preview")
        st.text_area("Extracted Text", resume_text, height=200)
        
        st.subheader("🔍 Resume Analysis")
        analysis = analyze_resume(resume_text)
        st.write(pd.DataFrame(analysis.items(), columns=["Metric", "Value"]))
        
        if analysis["ATS Friendly"] == "No":
            st.warning("⚠️ Your resume might be too short or missing key skills for ATS systems.")
        
        st.subheader("📊 Resume Score")
        score = resume_score(resume_text)
        st.metric(label="Resume Match Score", value=f"{score}%")
        
        if score < 50:
            st.error("🚀 Your resume needs improvement! Consider adding relevant skills and details.")
        elif score < 75:
            st.warning("👍 Good job! But there's still room for optimization.")
        else:
            st.success("🎉 Excellent! Your resume is well-optimized.")
        
else:
    st.info("📥 Please upload your resume to analyze.")
