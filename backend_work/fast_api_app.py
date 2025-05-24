from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from uuid import uuid4
import os
import shutil

from backend_qa import process_document, chat_with_knowledge

app = FastAPI()

# Enable CORS if needed for a frontend (e.g., React, Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend's origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session states
user_sessions = {}  # Format: {user_id: {"qna": [], "chat": []}}

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    num_questions: int = Form(...),
    user_id: str = Form(default_factory=lambda: str(uuid4()))
):
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in {"pdf", "docx"}:
        return JSONResponse(status_code=400, content={"error": "Unsupported file type"})

    # Save file temporarily
    tmp_dir = "tmp_uploads"
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"{uuid4()}.{file_ext}")
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Generate Q&A
        qna_results = process_document(tmp_path, file_ext, user_id, num_questions)
        user_sessions[user_id] = {
            "qna": qna_results,
            "chat": []
        }

        return {
            "user_id": user_id,
            "message": "Document processed and Q&A generated.",
            "qna": qna_results
        }
    finally:
        os.remove(tmp_path)


@app.get("/qna/")
async def get_generated_qna(user_id: str):
    session = user_sessions.get(user_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "User session not found"})
    return {"qna": session["qna"]}


@app.post("/chat/")
async def chat(
    user_id: str = Form(...),
    question: str = Form(...)
):
    session = user_sessions.get(user_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "User session not found"})

    chat_history = session["chat"]
    response = chat_with_knowledge(question, chat_history)
    chat_history.append(response)

    return {
        "question": response["question"],
        "answer": response["answer"],
        "chat_history": chat_history
    }
