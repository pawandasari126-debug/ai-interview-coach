from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

def get_feedback(answer):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Evaluate this interview answer and give feedback: {answer}"}
        ]
    )
    return response.choices[0].message.content


questions = [
    "Tell me about yourself",
    "Why should we hire you?",
    "What are your strengths?",
    "Explain one of your projects"
]

print("=== AI Interview Simulator ===")

for q in questions:
    print("\nQuestion:", q)
    answer = input("Your answer: ")

    if len(answer) < 20:
        feedback = "Answer is too short. Try to explain more."
    elif "project" in answer.lower():
        feedback = "Good, you mentioned project. Try adding more details and results."
    elif "skill" in answer.lower():
        feedback = "Nice, but explain with examples."
    else:
        feedback = "Decent answer, but improve clarity and structure."

    print("AI Feedback:", feedback)

print("\nInterview Completed!")