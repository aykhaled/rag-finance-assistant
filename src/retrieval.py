import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

PROMPT_TEMPLATE = """You are a financial analyst assistant. Use the following excerpts from SEC 10-K filings to answer the question. 
If the answer isn't in the provided context, say "I don't have enough information from the filings to answer that."
Always cite which company's filing you're referencing.

Context:
{context}

Question: {question}

Answer:"""


def get_retrieval_chain():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    return chain


if __name__ == "__main__":
    chain = get_retrieval_chain()
    result = chain.invoke({"query": "Compare Tesla and Microsoft revenue in their latest fiscal year."})
    print(result["result"])
    print("\n--- Sources ---")
    for doc in result["source_documents"]:
        print(f"  • {doc.metadata['source_file']} (page {doc.metadata.get('page', '?')})")