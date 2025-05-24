import os
import uuid
from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from pydantic import PrivateAttr

from langchain_openai import ChatOpenAI

from typing import List, Dict

# --- Load Environment Variables ---
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in environment variables!")

# --- Initialize Pinecone ---
pc = Pinecone(api_key=PINECONE_API_KEY)

if "interview-question-creator" not in pc.list_indexes().names():
    pc.create_index(
        name="interview-question-creator",
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-west-2")
    )

index = pc.Index("interview-question-creator")

# --- Embedding Model ---
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # Dim = 384

# --- LLM via OpenRouter ---
llm = ChatOpenAI(
    model_name="mistralai/mixtral-8x7b-instruct",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
    max_tokens=1024
)

# --- Text Splitter ---
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)

# --- Custom Retriever Using Pinecone ---
class PineconeRetriever(BaseRetriever):
    _index: object = PrivateAttr()

    def __init__(self, index):
        super().__init__()
        self._index = index

    def _get_relevant_documents(self, query: str, *, top_k=4, **kwargs) -> List[Document]:
        embedding = embedding_model.encode(query).tolist()
        response = self._index.query(
            namespace="",
            top_k=top_k,
            include_metadata=True,
            include_values=False,
            vector=embedding
        )
        results = []
        for match in response["matches"]:
            text = match["metadata"].get("text", "")
            doc = Document(page_content=text, metadata=match["metadata"])
            results.append(doc)
        return results

    async def _aget_relevant_documents(self, query: str, *, top_k=4, **kwargs) -> List[Document]:
        return self._get_relevant_documents(query, top_k=top_k, **kwargs)

retriever = PineconeRetriever(index)

# --- Q&A Generation from Full Document ---
def generate_qna_from_document(full_text: str, num_questions=3) -> List[dict]:
    prompt = (
        f"Based on the following document, generate {num_questions} important interview-style questions "
        f"along with detailed answers in the format:\n"
        f"[{{\"question\": \"...\", \"answer\": \"...\"}}, ...]\n"
        f"Return a JSON array.\n\n"
        f"Document:\n{full_text}"
    )
    response = llm.invoke(prompt)

    try:
        import json
        return json.loads(response.content.strip())
    except Exception:
        # Fallback if response is not valid JSON
        raw_text = response.content.strip()
        qna_pairs = []
        lines = raw_text.splitlines()
        current_q = None
        current_a = None
        for line in lines:
            if line.startswith("Q") and ":" in line:
                if current_q and current_a:
                    qna_pairs.append({"question": current_q, "answer": current_a})
                current_q = line.split(":", 1)[1].strip()
                current_a = None
            elif line.startswith("A") and ":" in line:
                current_a = line.split(":", 1)[1].strip()
            elif current_a is not None:
                current_a += " " + line.strip()

        if current_q and current_a:
            qna_pairs.append({"question": current_q, "answer": current_a})

        return qna_pairs


# --- Process Document, Store Embeddings, and Generate Q&A ---
def process_document(file_path, file_type, user_id, num_questions=3) -> List[Dict[str, str]]:
    if file_type == "pdf":
        loader = PyPDFLoader(file_path)
    elif file_type == "docx":
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file type")

    documents = loader.load()
    chunks = text_splitter.split_documents(documents)

    full_text = ""
    vectors = []
    for doc in chunks:
        text = doc.page_content
        full_text += text + "\n"

        metadata = {
            "user_id": user_id,
            "document_id": str(uuid.uuid4()),
            "text": text
        }
        embedding = embedding_model.encode(text).tolist()
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": metadata
        })

    index.upsert(vectors=vectors)

    # Generate and return structured Q&A
    return generate_qna_from_document(full_text, num_questions)

# --- Conversational Retrieval Chain ---
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever
)

# --- Chat Interface Function ---
def chat_with_knowledge(user_question: str, chat_history=[]) -> Dict[str, str]:
    # Ensure chat history is in (question, answer) tuple format
    formatted_history = [(q, a) for q, a in chat_history]

    response = qa_chain({
        "question": user_question,
        "chat_history": formatted_history
    })
    return {
        "question": user_question,
        "answer": response.get("answer", "No answer available.")
    }

