import streamlit as st

st.title("🤖 AI Interviewer")

st.write("🤖 Interviewer: Hello, I’ll be conducting your interview today. Let’s begin.")
# 🔹 Questions
questions = [
    "Tell me about yourself",
    "What projects have you worked on?",
    "What technologies do you know?",
    "Why should we hire you?"
]

# 🔹 Session state
if "chat" not in st.session_state:
    st.session_state.chat = []
    st.session_state.q_index = 0

if "follow_up" not in st.session_state:
    st.session_state.follow_up = False

# 🔹 AI response logic (simulated)
import random

def evaluate_answer(user_input):
    score = 0
    text = user_input.lower()

    if len(text) > 30:
        score += 3
    if len(text) > 80:
        score += 2
    if "project" in text:
        score += 2
    if "experience" in text or "learned" in text:
        score += 2
    if "i" in text:
        score += 1

    return min(score, 10)


def ai_response(user_input):
    text = user_input.lower()

    # 🔥 Score
    score = evaluate_answer(user_input)

    # 🔥 Feedback based on score
    if score >= 8:
        feedback = "Strong answer. Clear and well explained."
    elif score >= 5:
        feedback = "Decent answer, but try to be more specific."
    else:
        feedback = "Weak answer. Add more detail and examples."

    # 🔥 Follow-up questions
    if "project" in text:
        follow = random.choice([
            "What challenges did you face?",
            "What was your role in the project?",
            "What technologies did you use?"
        ])
    elif "ml" in text or "python" in text:
        follow = random.choice([
            "Where have you applied these skills?",
            "How confident are you in them?",
        ])
    else:
        follow = random.choice([
            "Can you explain more?",
            "Can you give an example?",
        ])

    if "scores" not in st.session_state:
        st.session_state.scores = []

        st.session_state.scores.append(score)

    return f"Score: {score}/10\nFeedback: {feedback}\n\nFollow-up: {follow}"
# 🔹 Show previous chat
for msg in st.session_state.chat:
    if "You:" in msg:
        st.markdown(f"""
        <div style='text-align: right; background-color: #262730; padding: 10px; border-radius: 10px; margin: 5px'>
            {msg}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='text-align: left; background-color: #1f77b4; padding: 10px; border-radius: 10px; margin: 5px'>
            {msg}
        </div>
        """, unsafe_allow_html=True)

# 🔹 Ask question safely
if st.session_state.q_index < len(questions):

    progress = (st.session_state.q_index) / len(questions)
    st.progress(progress)

    current_q = questions[st.session_state.q_index]
    st.write(f"🤖 Interviewer: {current_q}")
    st.write(f"Question {st.session_state.q_index + 1} of {len(questions)}")

else:
    st.progress(1.0)
    st.success("🎉 Interview Completed!")

    # 🔹 Normal question input
# 🔹 NORMAL QUESTION MODE
if not st.session_state.follow_up:
    
    user_input = st.text_input("Your Answer:", key="answer_input")

    if st.button("Submit", key="submit_btn"):
        if user_input.strip() != "":
            st.session_state.chat.append(f"🧑 You: {user_input}")

            response = ai_response(user_input)
            st.session_state.chat.append(f"🤖 Interviewer: {response}")

            if st.session_state.q_index == len(questions) - 1:
                st.session_state.follow_up = True
            else:
                st.session_state.q_index += 1

            st.rerun()

else:

    user_input = st.text_input("Your Follow-up Answer:", key="followup_input")

    if st.button("Submit Follow-up", key="follow_btn"):
        if user_input.strip() != "":
            st.session_state.chat.append(f"🧑 You: {user_input}")

            response = ai_response(user_input)
            st.session_state.chat.append(f"🤖 Interviewer: {response}")

            st.session_state.follow_up = False
            st.session_state.q_index += 1

            st.rerun()
# 🔹 Final Report
if st.session_state.q_index >= len(questions) and not st.session_state.follow_up:

    st.write("---")
    st.success("🎉 Interview Completed!")

    if "scores" in st.session_state:
        avg_score = sum(st.session_state.scores) / len(st.session_state.scores)

        st.write("## 📊 Final Performance")
        st.write(f"Average Score: {round(avg_score,2)} / 10")

        if avg_score >= 8:
            st.write("🔥 Excellent performance!")
        elif avg_score >= 5:
            st.write("👍 Good, but room for improvement.")
        else:
            st.write("⚠️ Needs improvement. Practice more.")