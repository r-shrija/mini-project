from flask import Flask, request, jsonify
from models import db, Question, UserPerformance
from ai_quiz import generate_question
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

# Start new quiz
@app.route("/quiz/start", methods=["GET"])
def start_quiz():
    user_id = request.args.get("user_id")
    first_question = Question.query.filter_by(difficulty="medium").first()
    return jsonify({
        "question_id": first_question.id,
        "question_text": first_question.question_text,
        "options": first_question.options,
        "difficulty": first_question.difficulty
    })

# Submit answer and get next question
@app.route("/quiz/answer", methods=["POST"])
def submit_answer():
    data = request.json
    user_id = data["user_id"]
    question_id = data["question_id"]
    user_answer = data["answer"]

    question = Question.query.get(question_id)
    correct = (user_answer == question.answer)

    # Save performance
    performance = UserPerformance(
        user_id=user_id,
        question_id=question_id,
        correct=correct,
        timestamp=datetime.now()
    )
    db.session.add(performance)
    db.session.commit()

    # Determine next difficulty
    if correct:
        next_difficulty = {"easy":"medium","medium":"hard","hard":"hard"}[question.difficulty]
    else:
        next_difficulty = {"easy":"easy","medium":"easy","hard":"medium"}[question.difficulty]

    # Fetch next question
    next_question = Question.query.filter_by(difficulty=next_difficulty, topic=question.topic).first()
    if not next_question:
        # fallback: generate with AI
        q = generate_question(question.topic, next_difficulty)
        if q:
            # Optionally store in DB
            next_question = Question(
                question_text=q["question"],
                options=q["options"],
                answer=q["answer"],
                topic=question.topic,
                difficulty=next_difficulty
            )
            db.session.add(next_question)
            db.session.commit()

    return jsonify({
        "question_id": next_question.id,
        "question_text": next_question.question_text,
        "options": next_question.options,
        "difficulty": next_question.difficulty,
        "correct": correct
    })