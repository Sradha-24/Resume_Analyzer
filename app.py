from flask import Flask, request, jsonify, render_template
import spacy, re

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

SKILLS = ["python","java","sql","machine learning","flask","django","html","css"]

def extract_name(text):
    match = re.search(r"(?:my name is|i am|name is)\s+([A-Za-z ]+?)(?:\s+and|,|\.)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Not found"

def extract_skills(text):
    skills_found = []
    text = text.lower()
    for skill in SKILLS:
        if skill in text:
            skills_found.append(skill)
    return skills_found

def extract_experience(text):
    text = text.lower()

    # Pattern: "experience is 3 years" or "3 years of experience"
    match = re.search(r"(\d+)\s+years?\s+of\s+experience", text)
    if match:
        return match.group(1)

    match = re.search(r"experience\s+(is|:)?\s*(\d+)\s+years?", text)
    if match:
        return match.group(2)

    return "Not mentioned"



# ---- UI Route ----
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        resume_text = request.form["resume_text"]

        result = {
            "candidate_name": extract_name(resume_text),
            "skills": extract_skills(resume_text),
            "years_of_experience": extract_experience(resume_text)
        }
    return render_template("index.html", result=result)


# ---- Webhook API Route ----
@app.route("/resume-webhook", methods=["POST"])
def resume_webhook():
    data = request.get_json()
    
    # Safety Check
    if not data or "resume_text" not in data:
        return jsonify({"error": "Missing resume_text in JSON body"}), 400

    resume_text = data.get("resume_text")

    return jsonify({
        "candidate_name": extract_name(resume_text),
        "skills": extract_skills(resume_text),
        "years_of_experience": extract_experience(resume_text)
    })


if __name__ == "__main__":
    app.run(debug=True)
