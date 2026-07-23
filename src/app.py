import streamlit as st
from retrieval import get_retrieval_chain

st.set_page_config(
    page_title="10-K Financial Analyst",
    page_icon="📊",
    layout="wide",
)

st.title("📊 10-K Financial Analyst")
st.caption("Chat with SEC 10-K filings from Microsoft, JPMorgan Chase, Tesla, Amazon & Walmart")

st.sidebar.header("About")
st.sidebar.markdown(
    """
    This tool uses **RAG (Retrieval-Augmented Generation)** to answer 
    questions about company financials using their official SEC 10-K filings.
    
    **How it works:**
    1. PDFs are chunked and embedded into a vector database
    2. Your question retrieves the most relevant chunks
    3. An LLM generates an answer grounded in the filings
    
    **Tech stack:** LangChain · ChromaDB · OpenAI · Streamlit
    """
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Sample questions:**")
st.sidebar.markdown("- Compare Tesla and Amazon revenue")
st.sidebar.markdown("- What are JPMorgan's biggest risk factors?")
st.sidebar.markdown("- How much did Microsoft spend on R&D?")
st.sidebar.markdown("- What is Walmart's employee count?")


@st.cache_resource
def load_chain():
    return get_retrieval_chain()


chain = load_chain()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask a question about the 10-K filings..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching filings..."):
            result = chain.invoke({"query": question})
            answer = result["result"]
            sources = result["source_documents"]

            st.markdown(answer)

            with st.expander("📄 Sources"):
                for doc in sources:
                    filename = doc.metadata.get("source_file", "Unknown")
                    page = doc.metadata.get("page", "?")
                    st.markdown(f"**{filename}** — Page {page}")
                    st.caption(doc.page_content[:300] + "...")
                    st.markdown("---")

    st.session_state.messages.append({"role": "assistant", "content": answer})