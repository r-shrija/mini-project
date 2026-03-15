import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

def generate_question(topic, difficulty):
    prompt = f"Generate 1 multiple-choice question on {topic}, {difficulty} difficulty, 4 options, specify correct answer."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role":"user","content":prompt}]
    )
    text = response.choices[0].message.content
    # Example parsing logic (you can improve)
    # Assume AI returns JSON:
    # { "question": "...", "options": ["...","..."], "answer":"..." }
    import json
    try:
        question_data = json.loads(text)
    except:
        return None
    return question_data