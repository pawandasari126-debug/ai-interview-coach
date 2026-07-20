import streamlit as st
from groq import Groq
import pandas as pd
import re
from pypdf import PdfReader
import speech_recognition as sr
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import numpy as np
import cv2
from deepface import DeepFace
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
from datetime import datetime
import base64
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.let_it_rain import rain
import random
import edge_tts
import asyncio
import os

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI Interview Coach PRO",
    page_icon="🎤",
    layout="wide"
)

st.markdown("""
<style>

/* Hide Streamlit Branding */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}

/* Main App */
.stApp{

background:
radial-gradient(circle at top left,#1e3a8a,#111827 65%);

}

/* Titles */
h1{
    color:white !important;
    font-weight:700 !important;
}

h2,h3{
    color:#f8fafc !important;
}

/* Buttons */
.stButton>button{

width:100%;

background:linear-gradient(90deg,#2563eb,#7c3aed);

border:none;

border-radius:15px;

font-size:18px;

font-weight:600;

padding:15px;

transition:.3s;

color:white;

}

.stButton>button:hover{

transform:translateY(-4px);

box-shadow:0 18px 35px rgba(37,99,235,.45);

}
    background:linear-gradient(90deg,#2563eb,#7c3aed);
    color:white;
    border:none;
    border-radius:12px;
    padding:12px 25px;
    font-weight:bold;
    transition:0.3s;
}

.stButton>button:hover{
    transform:scale(1.04);
    box-shadow:0 0 20px #3b82f6;
}

/* Metric Cards */
div[data-testid="metric-container"]{
    background:#1e293b;
    border-radius:18px;
    padding:20px;
    border:1px solid rgba(255,255,255,.08);
    transition:all .3s ease;
    box-shadow:0 10px 25px rgba(0,0,0,.25);
}

div[data-testid="metric-container"]:hover{
    transform:translateY(-6px);
    box-shadow:0 20px 40px rgba(59,130,246,.35);
    border:1px solid #3b82f6;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:#0f172a;
}

/* Expanders */
.streamlit-expanderHeader{
    font-weight:bold;
}

/* Progress */
.stProgress > div > div{
    background:#3b82f6;
}

/* Info/Success/Warning */
.stAlert{
    border-radius:15px;
}

</style>
""",unsafe_allow_html=True)

# =====================================================
# TOTAL QUESTIONS
# =====================================================
TOTAL_QUESTIONS = 10

# =====================================================
# GROQ CLIENT
# =====================================================
import os
import streamlit as st

api_key = os.getenv("GROQ_API_KEY")

if api_key is None:
    api_key = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)

# =====================================================
# TITLE
# =====================================================


# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:

    st.markdown("""
    <div style="
    background:linear-gradient(135deg,#2563eb,#7c3aed);
    padding:20px;
    border-radius:18px;
    text-align:center;
    margin-bottom:20px;
    ">

    <h2 style="color:white;margin:0;">
    🤖 AI Coach
    </h2>

    <p style="color:#e2e8f0;margin-top:10px;">
    Professional Interview Simulator
    </p>

    </div>
    """,unsafe_allow_html=True)

    st.markdown("### 📂 Navigation")

    page = st.radio(
        "",
        [
            "🏠 Home",
            "🎤 Interview Round",
            "🎙️ Voice Interview",
            "📹 Webcam Analysis",
            "💻 Coding Round",
            "📈 Reports"
        ]
    )

    st.markdown(
    """
    <hr style="
    border:1px solid #334155;
    margin-top:30px;
    margin-bottom:30px;
    ">
    """,
    unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("""
    <div style="
    text-align:center;
    color:#94a3b8;
    font-size:14px;
    ">

    Built with ❤️ using

    <b>Streamlit</b><br>

    AI Interview Coach PRO

    Powered by Groq AI

    Version 2.0

    </div>
    """,unsafe_allow_html=True)

# =====================================================
# SESSION STATES
# =====================================================
defaults = {
    # Interview
    "started": False,
    "question": "",
    "next_question": "",
    "question_number": 1,
    "scores": [],
    "history": [],
    "interview_complete": False,
    "feedback_generated": False,

    # Voice
    "voice_started": False,
    "voice_question": "",
    "voice_question_number": 1,
    "voice_scores": [],
    "voice_history": [],
    "voice_feedback_generated": False,
    "voice_next_question": "",
    "voice_complete": False,

    # Coding
    "coding_question": "",
    "coding_scores": [],
    "coding_history": [],
    "coding_question_number": 1,
    "coding_feedback_generated": False,
    "coding_complete": False,
    "next_coding_question": "",

    # Webcam
    "current_emotion": "neutral",
    "emotion_history": []
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value

async def generate_voice(text):

    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-GuyNeural"
    )

    await communicate.save("question.mp3")


def speak(text):

    asyncio.run(generate_voice(text))

    audio_file = open("question.mp3", "rb")

    st.audio(audio_file.read(), format="audio/mp3")

# =====================================================
# PDF FUNCTION
# =====================================================
def generate_pdf():

    filename = "Interview_Report.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    content = []

    title = Paragraph(
        "AI Interview Report",
        styles['Title']
    )

    content.append(title)
    content.append(Spacer(1, 20))

    if len(st.session_state.scores) > 0:

        avg_score = (
            sum(st.session_state.scores)
            / len(st.session_state.scores)
        )

    else:
        avg_score = 0

    summary = Paragraph(
        f"""
        <b>Average Score:</b> {avg_score:.1f}/10
        """,
        styles['BodyText']
    )

    content.append(summary)
    content.append(Spacer(1, 20))

    for i, item in enumerate(st.session_state.history):

        question = Paragraph(
            f"<b>Question {i+1}:</b> {item['question']}",
            styles['BodyText']
        )

        answer = Paragraph(
            f"<b>Answer:</b> {item['answer']}",
            styles['BodyText']
        )

        feedback = Paragraph(
            f"<b>Feedback:</b> {item['feedback']}",
            styles['BodyText']
        )

        score = Paragraph(
            f"<b>Score:</b> {item['score']}/10",
            styles['BodyText']
        )

        content.append(question)
        content.append(Spacer(1, 10))

        content.append(answer)
        content.append(Spacer(1, 10))

        content.append(feedback)
        content.append(Spacer(1, 10))

        content.append(score)
        content.append(Spacer(1, 20))

    doc.build(content)

    return filename

# =====================================================
# HOME PAGE
# =====================================================
if page == "🏠 Home":
    rain(
    emoji="⭐",
    font_size=18,
    falling_speed=5,
    animation_length="2"
    )

    hour = datetime.now().hour

    if hour < 12:
        greet = "☀ Good Morning"

    elif hour < 18:
        greet = "🌤 Good Afternoon"

    else:
        greet = "🌙 Good Evening"

    st.markdown(f"# {greet},👋")

    st.caption(
    datetime.now().strftime("%A, %d %B %Y • %I:%M %p")
    )

    st.markdown("""
    <div style="
        background:linear-gradient(135deg,#2563eb,#7c3aed);
        padding:30px;
        border-radius:25px;
        text-align:center;
        color:white;
        margin-bottom:30px;
    ">

    <h1 style="font-size:48px;margin-bottom:10px;">
    🎤 AI Interview Coach PRO
    </h1>

    <h3 style="color:#e2e8f0;">
    Practice • Analyze • Improve • Get Hired
    </h3>

    <p style="font-size:18px;">
    HR Interviews • Technical Interviews • Coding • Voice • Emotion Analysis
    </p>

    </div>
    """, unsafe_allow_html=True)

    quotes = [

    "Success is where preparation meets opportunity.",

    "Confidence comes from preparation.",

    "Every interview is practice for the next.",

    "Stay calm. Stay confident. Stay prepared.",

    "Small improvements every day lead to big results."

    ]

    st.info(
        f"💡 {random.choice(quotes)}"
    )

    col1, col2, col3, col4 = st.columns(4)

    cards = [
        ("🎤", "Interviews", len(st.session_state.history)),
        ("⭐", "Average Score",
        f"{(sum(st.session_state.scores)/len(st.session_state.scores)):.1f}/10"
        if st.session_state.scores else "0.0/10"),
        ("💻", "Coding", len(st.session_state.coding_history)),
        ("🎙", "Voice", len(st.session_state.voice_history))
    ]

    for col, card in zip([col1, col2, col3, col4], cards):
        with col:
            st.markdown(f"""
            <div style="
            background:rgba(255,255,255,.05);
            border:1px solid rgba(255,255,255,.08);
            border-radius:20px;
            padding:25px;
            text-align:center;
            backdrop-filter:blur(15px);
            box-shadow:0 10px 25px rgba(0,0,0,.25);
            ">
                <h1>{card[0]}</h1>
                <h2 style="margin:0;">{card[2]}</h2>
                <p style="color:#94a3b8;">{card[1]}</p>
            </div>
            """, unsafe_allow_html=True)
            
        completed = len(st.session_state.history)

    progress = completed / TOTAL_QUESTIONS

    st.progress(progress)

    st.caption(f"Interview Progress : {completed}/{TOTAL_QUESTIONS}")

    st.markdown(
    """
    <hr style="
    border:1px solid #334155;
    margin-top:30px;
    margin-bottom:30px;
    ">
    """,
    unsafe_allow_html=True
    )

    st.subheader("🤖 AI Career Recommendation")

    if len(st.session_state.scores) >= 5:

        avg = sum(st.session_state.scores) / len(st.session_state.scores)

        if avg >= 8:

            st.success("""
    ### 🚀 Excellent Performance

    You are ready for:

    ✅ Data Analyst Interviews

    ✅ Python Developer Interviews

    ✅ AI/ML Fresher Roles

    Recommendation:
    Keep practicing advanced interview questions and system design.
    """)

        elif avg >= 6:

            st.info("""
    ### 📈 Good Progress

    You have a solid foundation.

    Recommendation:

    • Improve communication

    • Give more structured answers

    • Practice behavioral interviews
    """)

        else:

            st.warning("""
    ### 📚 More Practice Needed

    Recommendation:

    • Practice HR questions

    • Improve technical concepts

    • Do more mock interviews

    • Improve confidence
    """)

    else:

        st.info("Complete an interview to unlock AI Career Recommendations.")

    st.markdown(
    """
    <hr style="
    border:1px solid #334155;
    margin-top:30px;
    margin-bottom:30px;
    ">
    """,
    unsafe_allow_html=True
    )

    st.subheader("📚 Recent Interview History")

    if st.session_state.history:

        for i, item in enumerate(reversed(st.session_state.history[-5:]), 1):

            with st.expander(f"Interview {len(st.session_state.history)-i+1}"):

                st.write(f"**Question:** {item['question']}")

                st.write(f"**Your Answer:**")

                st.write(item['answer'])

                st.write(f"**Score:** {item['score']}/10")

    else:

        st.info("No interviews completed yet.")

    st.markdown(
    """
    <hr style="
    border:1px solid #334155;
    margin-top:30px;
    margin-bottom:30px;
    ">
    """,
    unsafe_allow_html=True
    )

    st.subheader("🎯 Interview Readiness")

    if len(st.session_state.scores) >= 5:

        avg = sum(st.session_state.scores) / len(st.session_state.scores)

        readiness = int((avg / 10) * 100)

        st.progress(readiness)

        st.metric(
            "Interview Ready",
            f"{readiness}%"
        )

        if readiness >= 85:

            st.success("""
    ✅ You are interview ready.

    You can confidently attempt Data Analyst and Python interviews.
    """)

        elif readiness >= 65:

            st.info("""
    ⚡ Almost Ready

    Practice a few more mock interviews to improve consistency.
    """)

        else:

            st.warning("""
    📚 Keep Practicing

    Your communication and interview structure still need improvement.
    """)

    else:

        st.info("Complete at least 5 interview questions to calculate readiness.")

    st.markdown(
    """
    <hr style="
    border:1px solid #334155;
    margin-top:30px;
    margin-bottom:30px;
    ">
    """,
    unsafe_allow_html=True
    )

    st.subheader("🧠 AI Performance Summary")

    if len(st.session_state.scores) >= 5:

        avg = sum(st.session_state.scores) / len(st.session_state.scores)

        if avg >= 8:
            level = "🏆 Expert"
            color = "success"

        elif avg >= 6:
            level = "🥈 Intermediate"
            color = "info"

        else:
            level = "🥉 Beginner"
            color = "warning"

        st.metric(
            "Current Skill Level",
            level
        )

        if color == "success":
            st.success("Excellent interview performance. Keep refining your answers.")

        elif color == "info":
            st.info("Good progress. Focus on giving more detailed and structured answers.")

        else:
            st.warning("Practice more mock interviews to improve confidence and communication.")

    else:

        st.info("Complete your first interview to unlock your AI Performance Summary.")


        st.write(
        """
    Welcome to **AI Interview Coach PRO**.

    This platform helps you prepare for technical and HR interviews using AI.

    Practice, improve, and track your interview performance in one place.
    """
        )

        st.markdown(
        """
        <hr style="
        border:1px solid #334155;
        margin-top:30px;
        margin-bottom:30px;
        ">
        """,
        unsafe_allow_html=True
        )

        st.markdown("## ✨ Platform Features")

        st.markdown("""
        <style>

        .feature-grid{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:20px;
        margin-top:20px;
        }

        .feature-card{

        background:rgba(255,255,255,.05);

        border:1px solid rgba(255,255,255,.08);

        border-radius:22px;

        padding:25px;

        transition:.3s;

        backdrop-filter:blur(18px);

        box-shadow:0 10px 30px rgba(0,0,0,.2);

        height:250px;

        }

        .feature-card:hover{

        transform:translateY(-8px);

        box-shadow:0 20px 45px rgba(59,130,246,.35);

        border:1px solid #3b82f6;

        }

        .feature-title{

        font-size:28px;

        font-weight:bold;

        margin-bottom:15px;

        }

        .feature-desc{

        color:#cbd5e1;

        font-size:17px;

        line-height:30px;

        }

        </style>

        <div class="feature-grid">

        <div class="feature-card">

        <div class="feature-title">📄 Resume Analyzer</div>

        <div class="feature-desc">

        ✅ ATS Score<br>

        ✅ Resume Feedback<br>

        ✅ Missing Skills

        </div>

        </div>

        <div class="feature-card">

        <div class="feature-title">🎤 AI Interview</div>

        <div class="feature-desc">

        ✅ HR Interview<br>

        ✅ Technical Interview<br>

        ✅ AI Evaluation

        </div>

        </div>

        <div class="feature-card">

        <div class="feature-title">🎙 Voice Interview</div>

        <div class="feature-desc">

        ✅ Speech Recognition<br>

        ✅ Communication Analysis<br>

        ✅ AI Feedback

        </div>

        </div>

        <div class="feature-card">

        <div class="feature-title">📹 Webcam Analysis</div>

        <div class="feature-desc">

        ✅ Emotion Detection<br>

        ✅ Confidence Analysis<br>

        ✅ Behaviour Analysis

        </div>

        </div>

        <div class="feature-card">

        <div class="feature-title">💻 Coding Round</div>

        <div class="feature-desc">

        ✅ Python<br>

        ✅ SQL<br>

        ✅ AI Code Review

        </div>

        </div>

        <div class="feature-card">

        <div class="feature-title">📈 Reports</div>

        <div class="feature-desc">

        ✅ Charts<br>

        ✅ PDF Reports<br>

        ✅ AI Recommendation

        </div>

        </div>

        </div>

        """, unsafe_allow_html=True)

    st.markdown(
        "<h2 style='text-align:center;'>Ready to Ace Your Next Interview?</h2>",
        unsafe_allow_html=True
    )


    if st.button("🚀 Start Interview Preparation", use_container_width=True):
        st.success("👈 Select any module from the sidebar to begin!")


# =====================================================
# INTERVIEW ROUND
# =====================================================
if page == "🎤 Interview Round":

    st.markdown("""
    <div style="
    background:linear-gradient(135deg,#2563eb,#7c3aed);
    padding:30px;
    border-radius:20px;
    text-align:center;
    color:white;
    margin-bottom:20px;
    ">

    <h1>🎤 AI Interview Round</h1>

    <h3>Practice • Learn • Improve</h3>

    <p>Answer AI-generated interview questions and receive instant feedback.</p>

    </div>
    """, unsafe_allow_html=True)

    mode = st.selectbox(
        "Select Interview Type",
        [
            "HR Interview",
            "Data Analyst",
            "Python Developer",
            "AI/ML Engineer"
        ]
    )

    uploaded_resume = st.file_uploader(
        "Upload Resume (Optional)",
        type=["pdf"]
    )

    st.info(
    "📄 Upload your resume to analyze the resume or generate resume-based interview questions."
    )

    resume_text = ""

    if uploaded_resume:

        reader = PdfReader(uploaded_resume)

        for page_pdf in reader.pages:

            resume_text += (
                page_pdf.extract_text() or ""
            )

        st.success(
            "✅ Resume uploaded successfully"
        )

        if st.button("🔍 Analyze Resume"):
    
            prompt = f"""
            Analyze this resume professionally.

            Resume:
            {resume_text}

            Give:

            1. Resume Score out of 10
            2. ATS Score out of 100
            3. Strengths
            4. Weaknesses
            5. Missing Skills
            6. Suitable Roles
            7. Interview Readiness
            """

            with st.spinner("🤖 AI is thinking..."):

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
            

            st.subheader("📄 AI Resume Analysis")

            st.write(
            response.choices[0].message.content
            )

    # =================================================
    # START INTERVIEW
    # =================================================
    if not st.session_state.started:

        if st.button("🚀 Start Interview"):

            response = (
                client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            You are a professional interviewer.

                            Interview Type:
                            {mode}

                            Resume:
                            {resume_text}

                            Generate ONE NEW interview question.

                            Rules:
                            - Do not repeat previous questions
                            - Ask a different question
                            - Ask only the question
                            """
                        }
                    ]
                )
            )

            question = (
                response.choices[0]
                .message.content
            )

            st.session_state.question = question
            speak(question)
            st.session_state.started = True

            st.rerun()

    # =================================================
    # INTERVIEW FLOW
    # =================================================
    elif not st.session_state.interview_complete:

        st.markdown(
            f"## 📝 Question {st.session_state.question_number} of {TOTAL_QUESTIONS}"
        )

        st.markdown(f"""
        <div style="
        background:#1e293b;
        padding:25px;
        border-radius:20px;
        border-left:6px solid #3b82f6;
        box-shadow:0 8px 20px rgba(0,0,0,.25);
        margin-bottom:20px;
        ">

        <h3>🤖 AI Interviewer</h3>

        <p style="font-size:20px; color:white;">
        {st.session_state.question}
        </p>

        </div>
        """, unsafe_allow_html=True)

        if len(st.session_state.scores) > 0:
    
                avg_score = (
                    sum(st.session_state.scores)
                    / len(st.session_state.scores)
                )

                st.metric(
                    "Current Average Score",
                    f"{avg_score:.1f}/10"
                )

        st.markdown("## 💬 Your Response")

        answer = st.text_area(
            "",
            placeholder="Type your interview answer here...",
            height=220,
            key=f"answer_{st.session_state.question_number}"
        )

        if not st.session_state.feedback_generated:

                st.button(
                    "🚀 Submit Answer",
                    use_container_width=True
                )

                if answer.strip() == "":

                    st.warning(
                        "Please enter answer."
                    )

                else:

                    eval_prompt = f"""
                    IMPORTANT:

                    Start with:

                    SCORE: X/10

                    Then give ONLY:

                    Strengths:
                    - point 1
                    - point 2

                    Weaknesses:
                    - point 1
                    - point 2

                    Improvement:
                    - one specific suggestion

                    Keep the entire response under 120 words.

                    Question:
                    {st.session_state.question}

                    Answer:
                    {answer}

                    IMPORTANT:

                    Start your response with:

                    SCORE: X/10

                    Then provide:

                    Strengths
                    Weaknesses
                    Improvements
                    """

                    response = (
                        client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {
                                    "role": "user",
                                    "content": eval_prompt
                                }
                            ]
                        )
                    )

                    feedback = (
                        response.choices[0]
                        .message.content
                    )

                    score = 0

                    match = re.search(
                        r"SCORE:\s*(\d+)/10",
                        feedback,
                        re.IGNORECASE
                    )

                    if match:
                        score = int(match.group(1))

                    st.session_state.scores.append(
                        score
                    )

                    st.session_state.history.append({
                        "question":
                            st.session_state.question,

                        "answer":
                            answer,

                        "feedback":
                            feedback,

                        "score":
                            score
                    })

                    next_prompt = f"""
                    You are a professional interviewer.

                    Interview Type:
                    {mode}

                    Previous Questions:
                    {[item["question"] for item in st.session_state.history]}

                    Candidate's Last Answer:
                    {answer}

                    Generate ONE NEW interview question.

                    Rules:
                    - Do NOT repeat previous questions.
                    - Ask a different question.
                    - Increase difficulty gradually.
                    - Ask only the question.
                    """

                    next_response = (
                        client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {
                                    "role": "user",
                                    "content":
                                        next_prompt
                                }
                            ]
                        )
                    )

                    next_question = (
                        next_response
                        .choices[0]
                        .message.content
                    )

                    st.session_state.next_question = (
                        next_question
                    )
                    speak(st.session_state.question)

                    st.session_state.feedback_generated = True

                    st.rerun()

        # =================================================
        # SHOW FEEDBACK
        # =================================================
        if st.session_state.feedback_generated:

            latest = (
                st.session_state.history[-1]
            )

            st.markdown("## 📊 AI Interview Evaluation")

            score = latest["score"]

            # Score Card
            st.markdown(f"""
            <div style="
            background:linear-gradient(135deg,#2563eb,#7c3aed);
            padding:25px;
            border-radius:20px;
            text-align:center;
            color:white;
            margin-bottom:20px;
            ">

            <h1>⭐ {score}/10</h1>

            <h3>Overall Interview Score</h3>

            </div>
            """, unsafe_allow_html=True)

            feedback = latest["feedback"]

            st.markdown("### 📝 Detailed Feedback")

            st.markdown(feedback)

            if (
                st.session_state.question_number
                >= TOTAL_QUESTIONS
            ):

                st.session_state.interview_complete = True

                st.rerun()

            else:

                if st.button("➡️ Next Question"):

                    st.session_state.question = (
                        st.session_state.next_question
                    )

                    st.session_state.question_number += 1

                    st.session_state.feedback_generated = False

                    st.rerun()

                

# =====================================================
# FINAL INTERVIEW REPORT
# =====================================================
    if st.session_state.interview_complete:
                
        st.header("🏆 Final Interview Evaluation")

        avg_score = (
            sum(st.session_state.scores)
            / len(st.session_state.scores)
        )

        st.metric(
            "Overall Interview Score",
            f"{avg_score:.1f}/10"
        )

        prompt = f"""
        You are a senior HR interviewer.

        Based on these interview responses:

        {st.session_state.history}

        Give:

        1. Overall Strengths

        2. Weaknesses

        3. Communication Skills

        4. Technical Readiness

        5. Hiring Recommendation

        6. Final Interview Verdict

        Keep it professional.
        """

        with st.spinner("🤖 AI is thinking..."):

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                            "content": prompt
                    }
                ]
            )

        st.subheader("📋 AI Final Feedback")

        st.write(
            response.choices[0].message.content
        )

        st.success("✅ Interview Completed!")

        st.info("📈 View the complete analytics in the Reports Dashboard from the sidebar.")

# =====================================================
# VOICE INTERVIEW
# =====================================================
elif page == "🎙️ Voice Interview":

    st.header("🎙️ AI Voice Interview")

    voice_mode = st.selectbox(
        "Select Voice Interview Type",
        [
            "HR Interview",
            "Data Analyst",
            "Python Developer",
            "AI/ML Engineer"
        ]
    )

    # ==========================================
    # SESSION STATES
    # ==========================================
    if "voice_started" not in st.session_state:
        st.session_state.voice_started = False

    if "voice_question" not in st.session_state:
        st.session_state.voice_question = ""

    if "voice_question_number" not in st.session_state:
        st.session_state.voice_question_number = 1

    if "voice_scores" not in st.session_state:
        st.session_state.voice_scores = []

    if "voice_history" not in st.session_state:
        st.session_state.voice_history = []

    if "voice_feedback_generated" not in st.session_state:
        st.session_state.voice_feedback_generated = False

    if "voice_next_question" not in st.session_state:
        st.session_state.voice_next_question = ""

    if "voice_complete" not in st.session_state:
        st.session_state.voice_complete = False

    recognizer = sr.Recognizer()

    # ==========================================
    # START INTERVIEW
    # ==========================================
    if not st.session_state.voice_started:

        if st.button("🚀 Start Voice Interview"):

            prompt = f"""
            You are a professional interviewer.

            Generate ONE interview question for:
            {voice_mode}

            Rules:
            - Do not repeat previous questions
            - Ask a different question
            - Ask only the question
            """

            with st.spinner("🤖 AI is thinking..."):

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
            

            question = response.choices[0].message.content

            st.session_state.voice_question = question
            st.session_state.voice_started = True

            st.rerun()

    # ==========================================
    # INTERVIEW FLOW
    # ==========================================
    elif not st.session_state.voice_complete:

        st.subheader(
            f"Question {st.session_state.voice_question_number} / {TOTAL_QUESTIONS}"
        )

        st.info(
            st.session_state.voice_question
        )

        st.write("### 🎤 Record Your Answer")

        # ======================================
        # RECORD BUTTON
        # ======================================
        if not st.session_state.voice_feedback_generated:

            if st.button("🎙️ Start Recording"):

                try:

                    with sr.Microphone() as source:

                        st.warning(
                            "Listening... Speak now"
                        )

                        audio = recognizer.listen(
                            source,
                            timeout=20
                        )

                        st.success(
                            "Voice recorded"
                        )

                    text = recognizer.recognize_google(audio)

                    st.subheader("📝 Transcribed Answer")

                    st.write(text)

                    # ==================================
                    # AI EVALUATION
                    # ==================================
                    eval_prompt = f"""
                    IMPORTANT:

                    Start with:

                    SCORE: X/10

                    Then give ONLY:

                    Strengths:
                    - point 1
                    - point 2

                    Weaknesses:
                    - point 1
                    - point 2

                    Improvement:
                    - one specific suggestion

                    Keep the entire response under 120 words.

                    Question:
                    {st.session_state.voice_question}

                    Answer:
                    {text}

                    IMPORTANT:

                    Start your response with:

                    SCORE: X/10

                    Then provide:

                    Strengths
                    Weaknesses
                    Improvements
                    """

                    with st.spinner("🤖 AI is thinking..."):

                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {
                                    "role": "user",
                                    "content": eval_prompt
                                }
                            ]
                        )
                    

                    feedback = (
                        response.choices[0]
                        .message.content
                    )

                    # ==================================
                    # SCORE EXTRACTION
                    # ==================================
                    score = 0

                    match = re.search(
                        r"SCORE:\s*(\d+)/10",
                        feedback,
                        re.IGNORECASE
                    )

                    if match:
                        score = int(match.group(1))

                    # ==================================
                    # SAVE HISTORY
                    # ==================================
                    st.session_state.voice_scores.append(
                        score
                    )

                    st.session_state.voice_history.append({
                        "question":
                            st.session_state.voice_question,

                        "answer":
                            text,

                        "feedback":
                            feedback,

                        "score":
                            score
                    })

                    # ==================================
                    # GENERATE NEXT QUESTION
                    # ==================================
                    next_prompt = f"""
                    Generate ONE follow-up interview question.

                    Previous Question:
                    {st.session_state.voice_question}

                    Previous Answer:
                    {text}

                    Interview Type:
                    {voice_mode}

                    Ask only ONE realistic interview question.
                    """

                    next_response = (
                        client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {
                                    "role": "user",
                                    "content": next_prompt
                                }
                            ]
                        )
                    )

                    next_question = (
                        next_response
                        .choices[0]
                        .message.content
                    )

                    st.session_state.voice_next_question = (
                        next_question
                    )

                    st.session_state.voice_feedback_generated = True

                    st.rerun()

                except Exception as e:

                    st.error(f"Error: {e}")

        # ======================================
        # SHOW FEEDBACK
        # ======================================
        if st.session_state.voice_feedback_generated:

            latest = (
                st.session_state.voice_history[-1]
            )

            st.subheader("📊 AI Voice Feedback")

            st.write(latest["feedback"])

            st.success(
                f"Score: {latest['score']}/10"
            )

            # ==================================
            # INTERVIEW COMPLETE
            # ==================================
            if (
                st.session_state.voice_question_number
                >= 5
            ):

                st.session_state.voice_complete = True

                st.rerun()

            else:

                if st.button("➡️ Next Voice Question"):

                    st.session_state.voice_question = (
                        st.session_state.voice_next_question
                    )

                    st.session_state.voice_question_number += 1

                    st.session_state.voice_feedback_generated = False

                    st.rerun()

    # ==========================================
    # FINAL REPORT
    # ==========================================
    if st.session_state.voice_complete:

        st.header("📈 Voice Interview Report")

        avg_score = (
            sum(st.session_state.voice_scores)
            / len(st.session_state.voice_scores)
        )

        st.metric(
            "Average Voice Score",
            f"{avg_score:.1f}/10"
        )

        # ======================================
        # CHART
        # ======================================
        chart_data = pd.DataFrame({
            "Question": [
                f"Q{i+1}"
                for i in range(
                    len(
                        st.session_state.voice_scores
                    )
                )
            ],
            "Score":
                st.session_state.voice_scores
        })

        st.bar_chart(
            chart_data.set_index("Question")
        )

        # ======================================
        # HISTORY
        # ======================================
        st.subheader("📚 Full Interview History")

        for i, item in enumerate(
            st.session_state.voice_history
        ):

            with st.expander(
                f"Question {i+1}"
            ):

                st.write(
                    f"**Question:** {item['question']}"
                )

                st.write(
                    f"**Your Answer:** {item['answer']}"
                )

                st.write(
                    f"**Score:** {item['score']}/10"
                )

                st.write(
                    item['feedback']
                )

        # ======================================
        # RESTART
        # ======================================
        if st.button("🔄 Restart Voice Interview"):

            st.session_state.voice_started = False
            st.session_state.voice_question = ""
            st.session_state.voice_question_number = 1
            st.session_state.voice_scores = []
            st.session_state.voice_history = []
            st.session_state.voice_feedback_generated = False
            st.session_state.voice_next_question = ""
            st.session_state.voice_complete = False

            st.rerun()

# =====================================================
# WEBCAM ANALYSIS
# =====================================================
elif page == "📹 Webcam Analysis":
    
    if "current_emotion" not in st.session_state:
        st.session_state.current_emotion = "neutral"

    st.header("📹 AI Webcam Analysis")

    start = st.button("Start Webcam")

    FRAME_WINDOW = st.image([])

    emotion_box = st.empty()
    analysis_box = st.empty()

    if start:

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        while True:

            ret, frame = cap.read()

            if not ret:
                st.error("Camera not found")
                break

            try:

                small_frame = cv2.resize(frame, (320, 240))

                result = DeepFace.analyze(
                    small_frame,
                    actions=["emotion"],
                    enforce_detection=False,
                    detector_backend="opencv",
                    silent=True
                )

                emotion = result[0]["dominant_emotion"]

                st.session_state.current_emotion = emotion

                confidence_map = {
                    "happy": "8/10",
                    "neutral": "7/10",
                    "surprise": "6/10",
                    "fear": "4/10",
                    "sad": "4/10",
                    "angry": "3/10",
                    "disgust": "3/10"
                }

                confidence = confidence_map.get(emotion, "5/10")

                cv2.putText(
                    frame,
                    f"Emotion: {emotion}",
                    (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Confidence: {confidence}",
                    (20,80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255,0,0),
                    2
                )

            except:
                pass

            FRAME_WINDOW.image(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            )
            

            emotion_box.success(f"Detected Emotion: {emotion}")

            if emotion == "happy":
                analysis_box.info("""
            Confidence Level: 8/10

            Communication: Positive and engaging

            Interview Impression: Strong

            Suggestion: Maintain professionalism
            """)

            elif emotion == "fear":
                analysis_box.warning("""
            Confidence Level: 4/10

            Communication: Nervous

            Interview Impression: Lacks confidence

            Suggestion: Relax and maintain eye contact
            """)

            elif emotion == "neutral":
                analysis_box.info("""
            Confidence Level: 7/10

            Communication: Professional

            Interview Impression: Balanced

            Suggestion: Show more enthusiasm
            """)
        cap.release()
                
# =====================================================
# CODING ROUND
# =====================================================
elif page == "💻 Coding Round":

    st.header("💻 AI Coding Interview")

    coding_mode = st.selectbox(
        "Select Coding Round",
        [
            "Python",
            "SQL"
        ]
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    if st.session_state.coding_question == "":

        if st.button("🚀 Start Coding Round"):

            prompt = f"""
            Generate ONE {difficulty}
            {coding_mode}
            coding interview question.

            Rules:
            - Do not repeat previous questions
            - Ask a different question
            - Ask only the question
            """

            response = (
                client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
            )

            question = (
                response.choices[0]
                .message.content
            )

            st.session_state.coding_question = (
                question
            )

            st.rerun()

    if (
        st.session_state.coding_question != ""
        and not st.session_state.coding_complete
    ):

        st.subheader(
            f"Coding Question {st.session_state.coding_question_number} / {TOTAL_QUESTIONS}"
        )

        st.info(
            st.session_state.coding_question
        )

        if len(st.session_state.scores) > 0:
    
                avg_score = (
                    sum(st.session_state.scores)
                    / len(st.session_state.scores)
                )

                st.metric(
                    "Current Average Score",
                    f"{avg_score:.1f}/10"
                )

        code_answer = st.text_area(
            "Write Your Code",
            height=300,
            key=f"coding_answer_{st.session_state.coding_question_number}"
        )

        if not st.session_state.coding_feedback_generated:

            if st.button("Evaluate Code"):

                eval_prompt = f"""
                IMPORTANT:

                Start with:

                SCORE: X/10

                Then give ONLY:

                Strengths:
                - point 1
                - point 2

                Weaknesses:
                - point 1
                - point 2

                Improvement:
                - one specific suggestion

                Keep the entire response under 120 words.

                Question:
                {st.session_state.coding_question}

                Answer:
                {code_answer}

                IMPORTANT:

                Start your response with:

                SCORE: X/10

                Then provide:

                Strengths
                Weaknesses
                Improvements
                """

                response = (
                    client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "user",
                                "content":
                                    eval_prompt
                            }
                        ]
                    )
                )

                feedback = (
                    response.choices[0]
                    .message.content
                )

                score = 0

                match = re.search(
                    r"SCORE:\s*(\d+)/10",
                    feedback,
                    re.IGNORECASE
                )

                if match:
                    score = int(match.group(1))

                st.session_state.coding_scores.append(
                    score
                )

                st.session_state.coding_history.append({
                    "question":
                        st.session_state.coding_question,

                    "answer":
                        code_answer,

                    "feedback":
                        feedback,

                    "score":
                        score
                })

                next_prompt = f"""
                Generate ONE new
                {difficulty}
                {coding_mode}
                coding interview question.

                Rules:
                - Do not repeat previous questions
                - Ask a different question
                - Ask only the question
                """

                next_response = (
                    client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "user",
                                "content":
                                    next_prompt
                            }
                        ]
                    )
                )

                next_question = (
                    next_response
                    .choices[0]
                    .message.content
                )

                st.session_state.next_coding_question = (
                    next_question
                )

                st.session_state.coding_feedback_generated = True

                st.rerun()

        if st.session_state.coding_feedback_generated:

            latest = (
                st.session_state.coding_history[-1]
            )

            st.subheader("📊 AI Code Review")

            st.write(
                latest["feedback"]
            )

            st.success(
                f"Score: {latest['score']}/10"
            )

            if (
                st.session_state.coding_question_number >= 5
            ):

                st.session_state.coding_complete = True

                st.rerun()

            else:

                if st.button(
                    "➡️ Next Coding Question"
                ):

                    st.session_state.coding_question = (
                        st.session_state.next_coding_question
                    )

                    st.session_state.coding_question_number += 1

                    st.session_state.coding_feedback_generated = False

                    st.rerun()

    # =================================================
    # FINAL CODING REPORT
    # =================================================
    if st.session_state.coding_complete:

        st.header("📈 Coding Round Report")

        avg_score = (
            sum(st.session_state.coding_scores)
            / len(st.session_state.coding_scores)
        )

        st.metric(
            "Average Coding Score",
            f"{avg_score:.1f}/10"
        )

        if avg_score >= 8:
            st.success("🔥 Excellent Coding Skills")

        elif avg_score >= 6:
            st.info("👍 Good Coding Skills")

        else:
            st.warning("⚠️ Needs More Coding Practice")

        chart_data = pd.DataFrame({
            "Question": [
                f"Q{i+1}"
                for i in range(
                    len(st.session_state.coding_scores)
                )
            ],
            "Score":
                st.session_state.coding_scores
        })

        st.bar_chart(
            chart_data.set_index("Question")
        )

# =====================================================
# REPORTS
# =====================================================
elif page == "📈 Reports":

    st.header("📈 Reports Dashboard")

    st.caption(
    f"📅 Report Generated: {datetime.now().strftime('%d %B %Y | %I:%M %p')}"
    )

    if len(st.session_state.scores) > 0:

        avg_score = (
            sum(st.session_state.scores)
            / len(st.session_state.scores)
        )

        st.metric(
            "Average Interview Score",
            f"{avg_score:.1f}/10"
        )
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Questions Attempted",
                len(st.session_state.scores)
            )

        with col2:
            st.metric(
                "Highest Score",
                max(st.session_state.scores)
            )

        with col3:
            st.metric(
                "Lowest Score",
                min(st.session_state.scores)
            )
        if avg_score >= 8:
            rain(
                emoji="🎉",
                font_size=24,
                falling_speed=5,
                animation_length="4"
            )
            st.success("🏆 Interview Ready")

        elif avg_score >= 6:
            rain(
                emoji="📚",
                font_size=20,
                falling_speed=3,
                animation_length="3"
            )
            st.info("👍 Good Performance")

        else:
            st.warning("⚠️ Needs Improvement")

        st.subheader("🏅 Candidate Badge")

        if avg_score >= 8:
            rain(
                emoji="🎉",
                font_size=24,
                falling_speed=5,
                animation_length="4"
            )
            st.success("🥇 GOLD CANDIDATE")

        elif avg_score >= 6:
            rain(
                emoji="📚",
                font_size=20,
                falling_speed=3,
                animation_length="3"
            )
            st.info("🥈 SILVER CANDIDATE")

        else:
            st.warning("🥉 BRONZE CANDIDATE")

        st.subheader("📋 Interview Status")

        if avg_score >= 8:
            rain(
                emoji="🎉",
                font_size=24,
                falling_speed=5,
                animation_length="4"
            )
            st.success("Selected for Next Round")

        elif avg_score >= 6:
            rain(
                emoji="📚",
                font_size=20,
                falling_speed=3,
                animation_length="3"
            )
            st.info("Potential Candidate")

        else:
            st.warning("Needs More Preparation")

        chart_data = pd.DataFrame({
            "Question": [
                f"Q{i+1}"
                for i in range(
                    len(st.session_state.scores)
                )
            ],
            "Score":
                st.session_state.scores
        })

        chart = pd.DataFrame({
            "Question": list(range(1, len(st.session_state.scores)+1)),
            "Score": st.session_state.scores
        })

        fig = px.line(
            chart,
            x="Question",
            y="Score",
            markers=True,
            title="Interview Performance"
        )

        fig.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font_color="white",
            title_font_size=24,
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:

            fig = px.bar(
                chart,
                x="Question",
                y="Score",
                title="Question-wise Scores",
                color="Score",
                color_continuous_scale="Blues"
            )

            fig.update_layout(
                paper_bgcolor="#111827",
                plot_bgcolor="#111827",
                font_color="white"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:

            labels = [
                "Interview",
                "Coding",
                "Voice"
            ]

            values = [
                len(st.session_state.history),
                len(st.session_state.coding_history),
                len(st.session_state.voice_history)
            ]

            fig = px.pie(
                names=labels,
                values=values,
                hole=0.55,
                title="Practice Distribution"
            )

            fig.update_layout(
                paper_bgcolor="#111827",
                font_color="white"
            )

            st.plotly_chart(fig, use_container_width=True)

        if st.session_state.scores:
            avg = sum(st.session_state.scores) / len(st.session_state.scores)
        else:
            avg = 0

        fig = go.Figure(go.Indicator(

            mode="gauge+number",

            value=avg * 10,

            title={"text":"Interview Readiness"},

            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":"royalblue"},
                "steps":[
                    {"range":[0,40],"color":"#7f1d1d"},
                    {"range":[40,70],"color":"#854d0e"},
                    {"range":[70,100],"color":"#14532d"}
                ]
            }

        ))

        fig.update_layout(
            paper_bgcolor="#111827",
            font_color="white",
            height=420
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🕒 Recent Activity")

        activities = []

        for item in st.session_state.history[-5:]:
            activities.append(
                f"🎤 Interview Completed — {item['score']}/10"
            )

        for item in activities[::-1]:
            st.success(item)

        st.subheader("🤖 AI Recommendation")

        if avg_score >= 8:

            st.success("""
        Recommended Role:
        Junior AI/ML Engineer

        Interview Readiness:
        Excellent

        Hiring Recommendation:
        Strongly Recommended
        """)

        elif avg_score >= 6:

            st.info("""
        Recommended Role:
        Data Analyst / Python Developer

        Interview Readiness:
        Good

        Hiring Recommendation:
        Recommended with Training
        """)

        else:

            st.warning("""
        Recommended Role:
        Intern / Trainee

        Interview Readiness:
        Needs Improvement

        Hiring Recommendation:
        Not Yet Ready
        """)

        pdf_file = generate_pdf()

        with open(pdf_file, "rb") as file:

            st.download_button(
                label="📥 Download PDF Report",
                data=file,
                file_name="Interview_Report.pdf",
                mime="application/pdf"
            )

    else:

        st.info(
            "No reports available yet."
        )

    st.subheader("📋 Performance Summary")

    if avg_score >= 8:

        st.write("""
    Strengths:
    • Strong communication
    • Good interview responses
    • High confidence

    Weaknesses:
    • Minor improvements needed
    """)

    elif avg_score >= 6:

        st.write("""
    Strengths:
    • Decent communication
    • Good understanding

    Weaknesses:
    • More detailed answers needed
    • Improve confidence
    """)

    else:

        st.write("""
    Strengths:
    • Willingness to learn

    Weaknesses:
    • Communication skills
    • Technical depth
    • Confidence
    """)

# =====================================================
# RESTART
# =====================================================
if st.button("🔄 Restart"):

    st.session_state.clear()

    st.rerun()