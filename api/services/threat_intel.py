import os

from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

VECTOR_STORE_PATH = "vector_store/faiss_index"
embeddings = OpenAIEmbeddings()


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


def query_threat_intel(query: str) -> dict:
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    if not os.path.exists(VECTOR_STORE_PATH):
        return {
            "answer": "No threat intelligence data has been ingested yet. "
            "Please ingest a document first.",
            "source_found": False,
        }

    vector_store = FAISS.load_local(
        VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True
    )
    retriever = vector_store.as_retriever()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
    )

    result = qa_chain.invoke({"query": query})

    return {"answer": result["result"], "source_found": True}
