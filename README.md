# 📊 10-K Financial Analyst

> Chat with SEC 10-K filings using Retrieval-Augmented Generation (RAG). Ask natural-language questions about company financials and get answers grounded in official filings, with source citations.

**[🔗 Live Demo](https://aykhaled-rag-finance-assistant.streamlit.app/)**

---

## The Problem

Financial analysts, investors, and researchers regularly need to extract specific information from SEC 10-K filings — documents that routinely run 100–400 pages each. Finding a single figure (R&D spend, employee count, a named risk factor) means manually scanning hundreds of pages across multiple companies.

This tool turns that hours-long task into a conversation. Ask a question, get an answer grounded in the actual filings, with the source page cited so you can verify it.

## What It Does

- Ingests SEC 10-K annual reports from **Microsoft, JPMorgan Chase, Tesla, Amazon, and Walmart**
- Answers natural-language questions like *"Compare Tesla and Microsoft revenue"* or *"What are JPMorgan's biggest risk factors?"*
- Grounds every answer in the source documents and **cites the specific filing and page**
- Declines to answer when the filings don't contain the information — no hallucinated figures

## Architecture

```
PDFs (10-K filings)
      │
      ▼
[ Ingestion ]  ── PyPDF loads & parses ──► RecursiveCharacterTextSplitter
      │                                     (1000-char chunks, 200 overlap)
      ▼
[ Embeddings ]  ── HuggingFace all-MiniLM-L6-v2 (runs locally, no API) ──► vectors
      │
      ▼
[ Vector Store ]  ── ChromaDB (persisted to disk) ──► semantic search
      │
      ▼
[ Retrieval ]  ── top-5 relevant chunks ──► prompt context
      │
      ▼
[ LLM ]  ── OpenAI gpt-4o-mini generates grounded answer ──► answer + sources
      │
      ▼
[ Streamlit UI ]  ── chat interface with expandable source citations
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Local embeddings** (all-MiniLM-L6-v2) | Zero embedding cost, no rate limits, and demonstrates the model works fully offline — valuable for privacy-sensitive enterprise clients |
| **ChromaDB** | Lightweight, persists locally, no external DB to provision for a demo |
| **gpt-4o-mini** | Strong quality-to-cost ratio; the entire project runs on pennies |
| **Source citations** | Grounds trust — users can verify every answer against the original page |
| **Chunk size 1000 / overlap 200** | Balances retrieval precision with enough context to keep financial figures intact |

## Tech Stack

**LangChain** · **ChromaDB** · **OpenAI** · **HuggingFace Sentence Transformers** · **Streamlit** · **PyPDF**

## Running Locally

```bash
# Clone
git clone https://github.com/aykhaled/rag-finance-assistant.git
cd rag-finance-assistant

# Set up environment (using uv)
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Add your OpenAI key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Build the vector database from the PDFs in /data
python src/ingestion.py

# Launch the app
streamlit run src/app.py
```

## Project Structure

```
rag-finance-assistant/
├── data/                 # Source 10-K PDF filings
├── src/
│   ├── ingestion.py      # PDF parsing, chunking, embedding, vector store build
│   ├── retrieval.py      # RAG chain: retriever + LLM + prompt
│   └── app.py            # Streamlit chat interface
├── chroma_db/            # Persisted vector store
├── requirements.txt
└── README.md
```

## What I'd Do Differently at Scale

- **Hybrid search:** combine semantic retrieval with keyword/BM25 for exact figure lookups (financial numbers are where pure semantic search is weakest)
- **Metadata filtering:** let users scope queries to a specific company or fiscal year before retrieval
- **Table-aware parsing:** 10-Ks are dense with tables; a table-extraction layer (e.g. Unstructured, Camelot) would improve numeric accuracy
- **Evaluation harness:** a labeled Q&A set to measure retrieval precision and answer faithfulness as the corpus grows
- **Reranking:** a cross-encoder reranker on the retrieved chunks to push the most relevant context to the top

---

*Built as a demonstration of production-style RAG architecture — document ingestion, local embeddings, vector retrieval, and grounded generation with citations.*