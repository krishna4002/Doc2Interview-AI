# --- streamlit_app.py ---
import streamlit as st
from tempfile import NamedTemporaryFile
from uuid import uuid4
from backend_qa import process_document, chat_with_knowledge

# --- Initialize Session State ---
if "generated_qna" not in st.session_state:
    st.session_state.generated_qna = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid4())

st.title("Interview Q&A Generator")

# --- Upload Document ---
st.subheader("1. Upload Document")
uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])

# --- Set Number of Questions ---
st.subheader("2. Set Number of Questions")
num_questions = st.number_input(
    "How many questions should be generated for the entire document?",
    min_value=1, max_value=10, value=3, step=1
)

# --- Process Document and Generate Q&A ---
if uploaded_file is not None:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    with NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    with st.spinner("Processing document and generating Q&A..."):
        qna_results = process_document(tmp_path, file_ext, st.session_state.user_id, num_questions)
        st.session_state.generated_qna = qna_results

    st.success("Document processed and Q&A generated!")

# --- Display Generated Q&A ---
if st.session_state.generated_qna:
    st.subheader("\U0001F4C4 Generated Interview Questions & Answers")
    for i, qa in enumerate(st.session_state.generated_qna):
        st.markdown(f"**Q{i+1}:** {qa['question']}")
        st.markdown(f"**A{i+1}:** {qa['answer']}")
        st.markdown("---")

# --- Chat Section ---
st.subheader("\U0001F4AC Ask a Custom Question About the Document")
user_input = st.text_input("Ask a question:")

if st.button("Ask"):
    if user_input.strip():
        response = chat_with_knowledge(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append(response)

# --- Display Chat History ---
if st.session_state.chat_history:
    st.subheader("\U0001F9E0 Conversational Q&A")
    for i, chat in enumerate(st.session_state.chat_history):
        st.markdown(f"**You ({i+1}):** {chat['question']}")
        st.markdown(f"**AI ({i+1}):** {chat['answer']}")
        st.markdown("---")
