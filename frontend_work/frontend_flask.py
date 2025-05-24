from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling

API_URL = "http://127.0.0.1:8000"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["document"]
        num_questions = int(request.form["num_questions"])

        if file and file.filename.split(".")[-1].lower() in ["pdf", "docx"]:
            files = {"file": (file.filename, file.stream, file.mimetype)}
            data = {"num_questions": num_questions}

            response = requests.post(f"{API_URL}/upload/", files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                session["user_id"] = result["user_id"]
                session["qna"] = result["qna"]
                session["chat_history"] = []
                return redirect(url_for("index"))
            else:
                return f"Error: {response.text}", 400

    qna = session.get("qna", [])
    chat_history = session.get("chat_history", [])
    return render_template("index.html", qna=qna, chat_history=chat_history)

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("index"))

    response = requests.post(f"{API_URL}/chat/", data={"user_id": user_id, "question": question})

    if response.status_code == 200:
        result = response.json()
        chat_history = session.get("chat_history", [])
        chat_history.append({"question": result["question"], "answer": result["answer"]})
        session["chat_history"] = chat_history
    else:
        return f"Error: {response.text}", 400

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
