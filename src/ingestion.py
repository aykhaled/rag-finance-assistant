import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")


def load_pdfs(data_dir: str = DATA_DIR):
    docs = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            filepath = os.path.join(data_dir, filename)
            loader = PyPDFLoader(filepath)
            loaded = loader.load()
            for doc in loaded:
                doc.metadata["source_file"] = filename
            docs.extend(loaded)
            print(f"✓ Loaded {filename} — {len(loaded)} pages")
    print(f"\nTotal pages loaded: {len(docs)}")
    return docs


def chunk_documents(docs, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def build_vectorstore(chunks, persist_dir: str = CHROMA_DIR):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    print(f"✓ Vector store built and saved to {persist_dir}")
    return vectorstore


if __name__ == "__main__":
    docs = load_pdfs()
    chunks = chunk_documents(docs)
    build_vectorstore(chunks)
    print("\n✅ Ingestion complete!")