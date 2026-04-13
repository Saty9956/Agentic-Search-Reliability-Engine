# 🧠 Agentic Search Reliability Engine (BPSS Compliance RAG)

A backend-focused **Agentic RAG system** designed to interpret enterprise compliance policies, analyze candidate trackers, and cross-reference **structured and unstructured data** to determine **BPSS screening status** with high reliability and traceability.

This system avoids black-box agent frameworks and instead implements a **deterministic, multi-stage orchestration pipeline** for improved observability, reduced hallucinations, and enterprise-ready explainability.

---

# 🏗️ Architecture Overview

The system follows a **three-stage agentic pipeline**:

```
User Query
    ↓
Semantic Router (Intent Classification)
    ↓
Retrieval Layer
    ├── Vector DB (FAISS)
    └── Pandas DataFrames
    ↓
Synthesis Layer (Auditor LLM)
    ↓
Final Answer + Citations
```

### Routing → Retrieval → Synthesis

* **Routing** determines data source (docs / tabular / both)
* **Retrieval** gathers evidence from selected sources
* **Synthesis** cross-validates and generates final answer

This design improves determinism and reduces hallucination compared to ReAct-style agents.

---

# 🧩 Core Components

## 1. Semantic Router (Intent Classifier)

The first LLM call acts as a **gatekeeper**. It evaluates:

* user query
* conversation history
* compliance context

It then routes to:

* `DOCS` → Unstructured policy documents
* `TABULAR` → Candidate tracker dataframes
* `BOTH` → Cross-reference mode

This reduces token usage and prevents irrelevant retrieval.

---

## 2. Unstructured Data Pipeline

* Local **FAISS vector store**
* Embeddings: `all-MiniLM-L6-v2`
* Chunk overlap: **150 characters**
* Handles compliance documents and policy text

Provides semantic retrieval for policy interpretation.

---

## 3. Structured Data Pipeline

Uses:

* `pandas_dataframe_agent`
* dynamic dataframe querying
* code-based reasoning

The agent is explicitly instructed to return:

* dataset names
* row references
* citations

These are passed to the synthesis layer.

---

## 4. State Management

Implements **rolling memory window**:

* Last 3 interactions
* Context-aware follow-ups
* Conversational compliance evaluation

Memory is injected into:

* router
* synthesizer

---

# ⚖️ Contradiction Handling

The synthesis layer acts as an **auditor**:

* compares vector DB output
* compares pandas output
* detects conflicts
* flags inconsistencies

If data is missing:

```
"Insufficient evidence"
```

Temperature is pinned to **0** for deterministic output.

---

# 📂 Repository Structure

```
Agentic-Search-Reliability-Engine/
│
├── main.py                  # Main orchestration pipeline
├── check_data.py            # Dataset validation utility
├── requirements.txt         # Dependencies
├── example.env              # Environment template
├── Agent_Architecture.md    # Architecture explanation
├── README.md
└── Readme.md
```

---

# 🚀 Features

* Agentic RAG orchestration
* Semantic routing
* Hybrid retrieval (vector + tabular)
* FAISS vector database
* Pandas reasoning agent
* Conversation memory
* Conflict detection
* Deterministic outputs
* Enterprise compliance reasoning

---

# 🛠️ Tech Stack

* Python
* LangChain
* Groq LLM API
* FAISS
* HuggingFace Embeddings
* Pandas
* Pydantic (planned)
* LangGraph (future)

---

# ⚙️ Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/Saty9956/Agentic-Search-Reliability-Engine.git
cd Agentic-Search-Reliability-Engine
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install pandas python-dotenv langchain-community langchain-huggingface langchain-groq langchain-experimental faiss-cpu pypdf docx2txt openpyxl
```

---

## 4. Configure Environment

Create `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

---

## 5. Configure Dataset Path

Open `main.py` and update:

```
DATA_DIR = "bpss_agentic_dataset"
```

---

# ▶️ Run the System

```bash
python main.py
```

Example queries:

```
Is candidate John Doe BPSS compliant?
Which candidates failed address verification?
Compare employment gaps with policy rules
```

Type:

```
exit
```

to quit.

---

# ⚠️ Trade-offs & Limitations

### In-Memory Storage

* FAISS index stored locally
* Dataframes loaded in memory
* Not production scalable

### Pandas Agent Risk

Uses:

```
allow_dangerous_code=True
```

Not safe for production.

Production approach:

* SQL database
* read-only Text-to-SQL
* sandbox execution

### API Rate Limits

* Pandas agent generates iterative code
* May hit rate limits
* Handled via exponential backoff

---

# 🔮 Future Improvements

### Structured Output Enforcement

Use:

* Pydantic schema
* structured JSON responses
* validated citations

### LangGraph Migration

Replace Python flow with:

* state machine graph
* deterministic transitions
* better retry logic

### Production Deployment

* Managed vector DB
* SQL database
* Docker container
* API endpoint
* Observability logging

---

# 🎯 Use Cases

* BPSS compliance automation
* Background verification AI
* Policy reasoning assistant
* Enterprise compliance RAG
* Hybrid structured + unstructured QA
* Audit-friendly AI decisions

---

# 👨‍💻 Author

**Satyartha Shukla**
M.Tech AI — NIT Jalandhar
AI/ML | GenAI | Agentic RAG | LLM Systems

---

# ⭐ If you found this useful

Consider giving this repository a ⭐
