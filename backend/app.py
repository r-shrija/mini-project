from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

# Load environment variables
load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create Flask app
app = Flask(__name__)
CORS(app)

# -----------------------------
# In-memory storage for demo
# In production, use a DB (SQLite/Postgres)
# -----------------------------
questions_db = [
    {
        "id": 1,
        "question_text": "What is 2 + 2?",
        "options": ["2", "3", "4", "5"],
        "answer": "4",
        "topic": "Math",
        "difficulty": "easy"
    },
    {
        "id": 2,
        "question_text": "What is the capital of France?",
        "options": ["Paris", "Berlin", "London", "Rome"],
        "answer": "Paris",
        "topic": "Geography",
        "difficulty": "easy"
    }
]

user_progress = {}  # {user_id: {"last_difficulty": "medium", "asked_ids": []}}

# -----------------------------
# Home route
# -----------------------------
@app.route("/")
def home():
    return "EduAssist Backend Running"

# -----------------------------
# Chatbot route
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    # Simple response
    response = "I am EduAssist. Ask me any academic question."

    return jsonify({"reply": response})

# -----------------------------
# Study Plan route
# -----------------------------
@app.route("/study-plan", methods=["POST"])
def study_plan():
    data = request.json
    exam_date = data["exam_date"]
    subjects = data["subjects"]
    hours = int(data["hours"])

    try:
        prompt = f"""
Create a smart study plan.

Exam date: {exam_date}
Subjects: {subjects}
Study hours per day: {hours}

Generate a day-wise schedule with practice and revision.
"""
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI study planner for students."},
                {"role": "user", "content": prompt}
            ]
        )

        plan = ai_response.choices[0].message.content
        return jsonify({"plan": plan})

    except Exception as e:
        print("AI ERROR:", e)
        # fallback intelligent planner
        subjects_list = subjects.split(",")
        fallback_plan = ""
        day = 1
        for subject in subjects_list:
            study_time = int(hours * 0.7)
            practice_time = int(hours * 0.3)
            fallback_plan += f"Day {day}\n"
            fallback_plan += f"{subject.strip()} - {study_time} hours\n"
            fallback_plan += f"Practice Problems - {practice_time} hours\n\n"
            day += 1
        fallback_plan += f"Day {day}\n"
        fallback_plan += f"Revision of all subjects - {hours} hours\n"
        return jsonify({"plan": fallback_plan})

# -----------------------------
# Quiz Routes
# -----------------------------
def get_next_question(user_id, topic=None):
    """Select next question based on difficulty and previous progress."""
    if user_id not in user_progress:
        user_progress[user_id] = {"last_difficulty": "medium", "asked_ids": []}

    last_diff = user_progress[user_id]["last_difficulty"]
    asked = user_progress[user_id]["asked_ids"]

    # Filter questions by topic and not already asked
    available = [q for q in questions_db if q["id"] not in asked]
    if topic:
        available = [q for q in available if q["topic"] == topic]

    # Simple adaptive logic
    if last_diff == "easy":
        next_diff = "medium"
    elif last_diff == "medium":
        next_diff = "hard"
    else:
        next_diff = "hard"

    # Prefer question with matching difficulty
    candidates = [q for q in available if q["difficulty"] == next_diff]
    if not candidates:
        candidates = available  # fallback

    if not candidates:
        return None  # no more questions

    next_q = candidates[0]
    user_progress[user_id]["last_difficulty"] = next_q["difficulty"]
    user_progress[user_id]["asked_ids"].append(next_q["id"])
    return next_q

@app.route("/quiz/start", methods=["GET"])
def start_quiz():
    user_id = request.args.get("user_id", "guest")
    question = get_next_question(user_id)
    if not question:
        return jsonify({"message": "No questions available"})
    return jsonify({
        "question_id": question["id"],
        "question_text": question["question_text"],
        "options": question["options"],
        "difficulty": question["difficulty"]
    })

@app.route("/quiz/answer", methods=["POST"])
def submit_answer():
    data = request.json
    user_id = data["user_id"]
    question_id = data["question_id"]
    answer = data["answer"]

    # Find question
    question = next((q for q in questions_db if q["id"] == question_id), None)
    if not question:
        return jsonify({"error": "Question not found"}), 404

    correct = (answer == question["answer"])
    # Adjust next difficulty based on answer
    if correct:
        user_progress[user_id]["last_difficulty"] = {
            "easy": "medium",
            "medium": "hard",
            "hard": "hard"
        }[question["difficulty"]]
    else:
        user_progress[user_id]["last_difficulty"] = {
            "easy": "easy",
            "medium": "easy",
            "hard": "medium"
        }[question["difficulty"]]

    # Get next question
    next_q = get_next_question(user_id, topic=question["topic"])
    if not next_q:
        return jsonify({"message": "Quiz Completed", "correct": correct})

    return jsonify({
        "question_id": next_q["id"],
        "question_text": next_q["question_text"],
        "options": next_q["options"],
        "difficulty": next_q["difficulty"],
        "correct": correct
    })

# -----------------------------
# Run Flask app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)