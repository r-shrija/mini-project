from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create Flask app
app = Flask(__name__)
CORS(app)


# Home route
@app.route("/")
def home():
    return "EduAssist Backend Running"


# Chatbot route
@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]

    # simple response
    response = "I am EduAssist. Ask me any academic question."

    return jsonify({"reply": response})


# Study Plan Route
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

        return jsonify({
            "plan": fallback_plan
        })


# Run server
if __name__ == "__main__":
    app.run(debug=True)