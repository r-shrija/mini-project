from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500))
    options = db.Column(db.PickleType)  # list of options
    answer = db.Column(db.String(100))
    topic = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))  # easy, medium, hard

class UserPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    question_id = db.Column(db.Integer)
    correct = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)