import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

VECTOR_STORE_PATH = "vector_store/faiss_index"


def ingest_text(text: str) -> dict:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_text(text=text)

    embeddings = OpenAIEmbeddings()

    if os.path.exists(VECTOR_STORE_PATH):
        vector_store = FAISS.load_local(
            VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
        )
        vector_store.add_texts(texts=chunks)
    else:
        vector_store = FAISS.from_texts(texts=chunks, embedding=embeddings)

    vector_store.save_local(VECTOR_STORE_PATH)

    return {"status": "success", "chunks_added": len(chunks)}
