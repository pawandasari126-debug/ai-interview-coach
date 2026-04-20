import streamlit as st
import time

st.set_page_config(page_title="AI Interview Simulator", page_icon="🎯")

st.title("🎯 AI Interview Simulator")
st.write("Practice different types of interviews")

# 🔥 Mode Selection
mode = st.selectbox("Select Interview Type:", ["HR", "Technical", "AI/ML"])

# 🔹 Questions
if mode == "HR":
    questions = [
        "Tell me about yourself",
        "Why should we hire you?",
        "What are your strengths?",
        "Where do you see yourself in 5 years?"
    ]
elif mode == "Technical":
    questions = [
        "Explain Python basics",
        "What is a loop?",
        "Explain OOP concepts",
        "What is a database?"
    ]
else:
    questions = [
        "What is Machine Learning?",
        "Supervised vs Unsupervised learning",
        "What is overfitting?",
        "Explain one ML project"
    ]

# 🔹 Session State
if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "answers" not in st.session_state:
    st.session_state.answers = []

if "feedback_list" not in st.session_state:
    st.session_state.feedback_list = []

if "scores_list" not in st.session_state:
    st.session_state.scores_list = []

if "answered" not in st.session_state:
    st.session_state.answered = False

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()


# 🔹 Feedback Logic
def get_feedback(ans):
    if len(ans) < 20:
        return "⚠️ Answer is too short."
    if "project" in ans.lower():
        return "✅ Good! Add results and impact."
    if "skill" in ans.lower():
        return "👍 Add examples."
    return "🙂 Improve structure."


# 🔹 Score Logic
def get_score(ans):
    score = 0
    if len(ans) > 30:
        score += 3
    if len(ans) > 80:
        score += 2
    if "project" in ans.lower():
        score += 2
    if "skill" in ans.lower():
        score += 2
    if "i" in ans.lower():
        score += 1
    return min(score, 10)


# 🔥 MAIN FLOW
if st.session_state.q_index < len(questions):

    # 🔥 TIMER (stable)
    time_limit = 60
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = time_limit - elapsed

    st.markdown(f"### ⏱️ Time left: {max(remaining,0)} sec")

    # ⏰ Auto next if time ends
    if remaining <= 0:
        st.warning("⏰ Time's up! Moving to next question...")

        st.session_state.answers.append("No answer (Time up)")
        st.session_state.feedback_list.append("No feedback")
        st.session_state.scores_list.append(0)

        st.session_state.q_index += 1
        st.session_state.answered = False
        st.session_state.start_time = time.time()

        st.rerun()

    # 🔹 Question
    q = questions[st.session_state.q_index]
    st.subheader(f"Question {st.session_state.q_index + 1}")
    st.write(q)

    answer = st.text_area("Your Answer:", key="answer")

    # 🔹 Submit
    if not st.session_state.answered:
        if st.button("Submit Answer"):
            if answer.strip() == "":
                st.warning("Please enter your answer!")
            else:
                feedback = get_feedback(answer)
                score = get_score(answer)

                st.write("### Result")
                st.write("**Score:**", score, "/10")
                st.write("**Feedback:**", feedback)

                st.session_state.answers.append(answer)
                st.session_state.feedback_list.append(feedback)
                st.session_state.scores_list.append(score)

                st.session_state.answered = True
                st.session_state.start_time = time.time()

    else:
        if st.button("Next Question"):
            st.session_state.q_index += 1
            st.session_state.answered = False
            st.session_state.start_time = time.time()
            st.rerun()

# 🔁 Auto refresh every 1 second (safe)
if st.session_state.q_index < len(questions) and not st.session_state.get("completed", False):
    time.sleep(1)
    st.rerun()

# 🔹 FINAL REPORT
    st.session_state.completed = True
else:
    st.success(f"🎉 {mode} Interview Completed!")

    if len(st.session_state.scores_list) > 0:
        final_score = sum(st.session_state.scores_list) / len(st.session_state.scores_list)
    else:
        final_score = 0

st.write("## 📊 Final Report")
# 🔥 Chart
import pandas as pd

data = pd.DataFrame({
    "Question": [f"Q{i+1}" for i in range(len(st.session_state.scores_list))],
    "Score": st.session_state.scores_list
})

st.write("### 📊 Performance Chart")
st.bar_chart(data.set_index("Question"))

# 🔥 Overall Score
st.write("### Overall Score:", round(final_score, 2), "/10")

# 🔥 Detailed Report
for i in range(len(st.session_state.answers)):
    st.write(f"### Question {i+1}")
    st.write("**Q:**", questions[i])
    st.write("**Your Answer:**", st.session_state.answers[i])
    st.write("**Score:**", st.session_state.scores_list[i], "/10")
    st.write("**Feedback:**", st.session_state.feedback_list[i])
    st.write("---")

    for i in range(len(st.session_state.answers)):
        st.write(f"### Question {i+1}")
        st.write("**Q:**", questions[i])
        st.write("**Your Answer:**", st.session_state.answers[i])
        st.write("**Score:**", st.session_state.scores_list[i], "/10")
        st.write("**Feedback:**", st.session_state.feedback_list[i])
        st.write("---")

    if st.button("Restart", key="restart_btn"):
        st.session_state.clear()
    st.rerun()