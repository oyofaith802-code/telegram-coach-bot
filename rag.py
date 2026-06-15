from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = []
index = None


# -------------------------
# LOAD BOTH BOOKS
# -------------------------
def load_book():
    text = ""

    files = [
        "book/book1.pdf",
        "book/book2.txt"
    ]

    for file in files:
        if not os.path.exists(file):
            print(f"⚠️ Missing file: {file}")
            continue

        if file.endswith(".pdf"):
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""

        elif file.endswith(".txt"):
            with open(file, "r", encoding="utf-8") as f:
                text += f.read()

    return text


# -------------------------
# SPLIT TEXT INTO CHUNKS
# -------------------------
def chunk(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]


# -------------------------
# BUILD VECTOR DATABASE
# -------------------------
def build():
    global texts, index

    print("Building RAG index...")

    text = load_book()
    texts = chunk(text)

    vectors = model.encode(texts)

    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(np.array(vectors).astype("float32"))

    print("RAG ready ✔")


# -------------------------
# SEARCH FUNCTION
# -------------------------
def search(query, k=3):
    global index

    if index is None:
        raise ValueError("RAG not built yet. Call build() first.")

    q_vec = model.encode([query])

    distances, I = index.search(
        np.array(q_vec).astype("float32"),
        k
    )

    return [texts[i] for i in I[0]], distances