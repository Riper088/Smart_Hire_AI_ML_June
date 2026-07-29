"""SmartHire web portal (Streamlit). Run: streamlit run app/streamlit_app.py"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd

from src.parsing.resume_parser import extract_text
from src.models.classifier import predict_category
from src.models.recommender import recommend_jobs
from src.features.match_features import extract_resume_skills, analyze_skill_gap

st.set_page_config(page_title="SmartHire", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# Inject custom CSS for a premium feel
st.markdown("""
<style>
    /* Keyframe Animations */
    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulseGlow {
        0% { box-shadow: 0 10px 15px rgba(43, 88, 118, 0.2); }
        50% { box-shadow: 0 15px 25px rgba(78, 67, 118, 0.4); }
        100% { box-shadow: 0 10px 15px rgba(43, 88, 118, 0.2); }
    }
    
    @keyframes fillBar {
        from { width: 0%; }
        /* target width is set inline */
    }
    
    @keyframes popIn {
        0% { opacity: 0; transform: scale(0.8); }
        70% { transform: scale(1.05); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .main {
        background-color: #0E1117;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.3);
    }
    
    .job-card {
        background: #1E2127;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0; /* Starts hidden, revealed by animation */
    }
    .job-card:hover {
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 8px 16px rgba(0,0,0,0.5);
    }
    .job-title {
        color: #4CAF50;
        margin-top: 0;
        font-size: 1.4em;
    }
    .job-company {
        color: #A0AEC0;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .tag {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        margin-right: 8px;
        margin-bottom: 8px;
        font-weight: 500;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        opacity: 0;
    }
    .tag:hover {
        transform: scale(1.08) rotate(1deg);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .tag-blue { background: #2b5876; color: #E2E8F0; }
    .tag-green { background: rgba(76, 175, 80, 0.2); color: #81C784; border: 1px solid #4CAF50; }
    .tag-red { background: rgba(244, 67, 54, 0.1); color: #E57373; border: 1px solid #F44336; }
    
    .cat-box {
        background: linear-gradient(135deg, #2b5876, #4e4376, #2b5876);
        background-size: 200% 200%;
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 10px 15px rgba(0,0,0,0.2);
        animation: slideUpFade 0.6s ease-out forwards, pulseGlow 4s infinite ease-in-out, gradientShift 6s infinite ease;
        transition: transform 0.3s ease;
        opacity: 0;
    }
    .cat-box:hover {
        transform: translateY(-5px) scale(1.02);
    }
    .cat-box h2 {
        margin: 0;
        font-size: 2.2em;
        color: white;
    }
    
    .progress-bar-fill {
        height: 8px;
        border-radius: 4px;
        background: linear-gradient(90deg, #4CAF50, #81C784);
        animation: fillBar 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    
    .shimmer-text {
        background: linear-gradient(90deg, #A0AEC0 0%, #FFFFFF 50%, #A0AEC0 100%);
        background-size: 200% auto;
        color: #A0AEC0;
        background-clip: text;
        text-fill-color: transparent;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s infinite linear;
        display: inline-block;
    }
    
    @keyframes typing {
      from { width: 0 }
      to { width: 100% }
    }
    @keyframes blink-caret {
      from, to { border-color: transparent }
      50% { border-color: #4CAF50; }
    }
    .typewriter-text {
      overflow: hidden;
      border-right: .15em solid #4CAF50;
      white-space: nowrap;
      letter-spacing: .02em;
      animation: typing 2.5s steps(40, end), blink-caret .75s step-end infinite;
      font-size: 1.2em; 
      color: #A0AEC0;
      width: 100%;
      max-width: fit-content;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }
    .floating-element {
        animation: float 4s ease-in-out infinite;
        display: inline-block;
    }
    
</style>

""", unsafe_allow_html=True)

st.title("🚀 SmartHire")
st.markdown("<div class='typewriter-text'>AI-Powered Resume-to-Job Matching & Career Guidance Engine</div>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.header("1. Provide Your Resume")
    st.markdown("Upload your resume as a file or paste the text directly below.")
    
    upload_tab, paste_tab = st.tabs(["📁 Upload File", "📝 Paste Text"])
    
    resume_text = ""
    
    with upload_tab:
        uploaded_file = st.file_uploader("Drop your resume here (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            try:
                resume_text = extract_text(uploaded_file, uploaded_file.name)
                st.success(f"✓ Extracted {len(resume_text)} characters.")
            except Exception as e:
                st.error(f"Error parsing file: {e}")
                
    with paste_tab:
        pasted_text = st.text_area("Paste your resume content:", height=250, placeholder="Paste your experience, skills, and education here...")
        if pasted_text and not resume_text:
            resume_text = pasted_text
            
    analyze_btn = st.button("✨ Analyze My Profile", use_container_width=True)

with col2:
    st.header("2. Your Insights & Matches")
    
    if analyze_btn:
        if not resume_text.strip():
            st.warning("Please upload a resume or paste text first.")
        else:
            with st.spinner("🧠 AI is analyzing your profile..."):
                try:
                    # Context 1: Extracted Skills
                    extracted_skills = extract_resume_skills(resume_text)
                    if extracted_skills:
                        skills_html = "".join([f'<span class="tag tag-blue" style="animation-delay: {0.05 * i}s">{s.title()}</span>' for i, s in enumerate(extracted_skills)])
                        st.markdown(f"**Identified Core Skills:**<br>{skills_html}", unsafe_allow_html=True)
                    else:
                        st.markdown("**Identified Core Skills:** None found from our standard tech list.")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Context 2: Predicted Category
                    category = predict_category(resume_text)
                    st.markdown(f"""
                        <div class="cat-box">
                            <p style="margin:0; font-size: 1.1em; opacity: 0.9;">Based on your profile, you are a great fit for:</p>
                            <h2>{category}</h2>
                        </div>
                        <br>
                    """, unsafe_allow_html=True)
                    
                    # Context 3: Job Recommendations & Gap Analysis
                    jobs = recommend_jobs(resume_text, top_n=5)
                    st.balloons()
                    st.subheader(f"🔥 Top {len(jobs)} Job Recommendations")
                    
                    for i, (_, row) in enumerate(jobs.iterrows()):
                        score = row['similarity_score'] * 100
                        
                        # Skill Gap Analysis
                        gap_analysis = analyze_skill_gap(resume_text, row['skills'])
                        
                        matched_html = "".join([f'<span class="tag tag-green" style="animation-delay: {0.1 * j}s">✓ {s.title()}</span>' for j, s in enumerate(gap_analysis['matched'])])
                        missing_html = "".join([f'<span class="tag tag-red" style="animation-delay: {0.1 * (len(gap_analysis["matched"]) + j)}s">✗ {s.title()}</span>' for j, s in enumerate(gap_analysis['missing'])])
                        
                        st.markdown(f"""
                            <div class="job-card" style="animation-delay: {0.15 * i}s">
                                <h3 class="job-title">{row['title']}</h3>
                                <div class="job-company">🏢 {row['company']} &nbsp;|&nbsp; 📍 {row['location']} &nbsp;|&nbsp; ⏱️ {row['experience']}</div>
                                
                                <div style="margin-bottom: 15px;">
                                    <strong class="shimmer-text">Match Score: {score:.1f}%</strong>
                                    <div style="width: 100%; background-color: #2D3748; border-radius: 4px; margin-top: 5px; overflow: hidden;">
                                        <div class="progress-bar-fill" style="width: {score}%;"></div>
                                    </div>
                                </div>
                                
                                <div><strong style="color: #A0AEC0;">Skills Breakdown:</strong></div>
                                <div style="margin-top: 5px;">
                                    {matched_html}
                                    {missing_html}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander("Read Full Job Description"):
                            st.write(row['description'])
                            
                except FileNotFoundError:
                    st.error("Models are not trained yet! Please run the training scripts in the background first.")
                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")
    else:
        st.markdown("""
            <div style='text-align: center; margin-top: 60px;'>
                <div class='floating-element' style='font-size: 4em; margin-bottom: 20px;'>📄</div>
                <h3 style='color: #E2E8F0;'>Waiting for your resume...</h3>
                <p style='color: #A0AEC0; font-size: 1.1em;'>Upload your resume and click <b style='color: #4CAF50;'>Analyze</b> to unlock personalized insights.</p>
            </div>
        """, unsafe_allow_html=True)


