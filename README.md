# 📄 AI Interview Q&A Generator from Documents

This is a smart AI-powered app that can *read any PDF or DOCX document, understand the content, and **automatically generate important interview-style questions and fully explained answers. It also lets you **ask your own questions* and have a conversation with the document like you're talking to a teacher.

---

## What This App Can Do

Upload documents like notes, books, resumes, or articles  
Automatically generate interview Q&A based on the content  
Choose how many questions you want per section  
Chat with the document using your own questions  
Uses smart AI models from Hugging Face  
Works with Pinecone to store and search your documents  
Available via *Streamlit UI* and *FastAPI/Flask UI*  

---

## Who Is This For?

- Students preparing for interviews
- Teachers creating test questions
- HRs or recruiters checking resumes
- Researchers or developers exploring AI
- Anyone who wants to understand documents better!

---

## Project Structure


📁 interview-qna-generator/
│              
├── .env                        # API keys
├── requirements.txt            # All dependencies
│
├── streamlit_app.py            # Streamlit UI
│
├── backend_work/
│   ├── fast_api_app.py         # FastAPI endpoints
│   ├── backend_qa              # Core logic (shared across UIs)│   
│
├── frontend_work/
│   ├── frontend_flask.py                  # Flask app
│   ├── templates/              # HTML templates│   
│
└── README.md                   # Full documentation


---

## 🛠 Installation Guide

1. *Clone the project*:

bash
git clone https://github.com/your-username/interview-qna-generator.git
cd interview-qna-generator


2. *Install required Python packages*:

bash
pip install -r requirements.txt


---

## 🔐 Setup .env File

Create a file named .env and paste your keys:

env
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENV=your-pinecone-environment-name
HF_TOKEN=your-huggingface-api-key


> ⚠ Don’t share your keys publicly. These keep your app secure.

---

## ▶ How to Run

### 🚀 Streamlit UI

bash
streamlit run streamlit_app.py


### ⚡ FastAPI UI

bash
cd fastapi_app
uvicorn main:app --reload

Then open [http://localhost:8000](http://localhost:8000)

### 🌐 Flask UI

bash
cd flask_app
python app.py

Then open [http://localhost:5000](http://localhost:5000)

---

## 🧠 How the AI Thinks (Prompt Example)

This is what we ask the AI:


From the following document text, generate 3 important interview-style questions
and provide DETAILED, EXPLAINED answers for each:

[Document content here]

Format:
Q1: ...
A1: ...
Q2: ...
A2: ...


You can also change “3” to any number using a simple option in the app.

---

## 💡 What Makes It Special?

- You don’t need to write questions manually  
- Answers are explained in simple language  
- Very useful for learning and revision  
- Gives you control over how many Q&As you want  
- You can talk to the document like a chatbot  
- Runs with *Streamlit* for quick testing, and *FastAPI/Flask* for integration into products

---

## 🧠 Recommended AI Models

| Model Name                  | Description                       |
|----------------------------|-----------------------------------|
| google/flan-t5-base        | Fast and small, works well        |
| google/flan-t5-xl          | Bigger and more accurate          |
| tiiuae/falcon-7b-instruct  | Very detailed and accurate answers|
| mistralai/Mistral-7B-Instruct | Fast, free, and detailed         |

> You can switch between models by changing the name in the code.

---

## 📌 Real-Life Uses

- 🧪 Turn lecture notes into mock interview questions  
- 📄 Summarize and question business documents  
- 🧑‍🏫 Teachers generating quiz questions  
- 🤖 Create training material from manuals  
- 🧑‍💻 Developers building document chatbots  

---

## 📧 Contact

If you face any issues or want to contribute, please open an issue at:  
🔗 [GitHub Issues](https://github.com/your-username/interview-qna-generator/issues)

---

## 📝 License

This project is under the *MIT License* – Free for everyone to use, modify, and share.

---
