# Architecture Note: BPSS Agentic System

## Approach & Design Philosophy
For this exercise, I opted to build a custom Agentic RAG orchestrator rather than relying entirely on standard framework wrappers like LangChain's built-in AgentExecutor. In an enterprise compliance setting, tracing exactly why an LLM made a decision is critical. Standard ReAct agents can sometimes get stuck in loops or hallucinate when dealing with strict policy constraints. 

By breaking the pipeline into distinct, hardcoded phases (Routing -> Retrieval -> Synthesis), the system gains high observability and determinism.

## Core Components
1. The Semantic Router (Intent Classification): The first LLM call acts as a gatekeeper. It evaluates the user's question alongside the conversation history to decide if we need to search unstructured text (DOCS), tabular data (TABULAR), or both (BOTH). This isolates the search space, saving tokens and preventing the LLM from getting confused by irrelevant tabular data during policy questions.

2. Unstructured Data Pipeline: Handled via a local FAISS vector store. I used HuggingFace's all-MiniLM-L6-v2 embeddings for fast, local inference. Text is split with a 150-character overlap to prevent cutting off crucial policy context mid-sentence.

3. Structured Data Pipeline: I utilized the experimental pandas_dataframe_agent. To ensure strict citations, the agent is prompted with the exact keys/filenames of the loaded dataframes so it can pass those citations up to the final layer.

4. State Management: The system implements a rolling memory window representing the last 3 interactions. This state is injected into both the router and the final synthesizer, allowing the evaluator to ask natural, context-dependent follow-up questions.

## Handling Contradictions & Missing Data
The system relies on strict prompt engineering at the Synthesis layer to handle edge cases. By explicitly instructing the LLM to look for conflicts between the Pandas output and the Vector DB output, it acts as an auditor rather than just a summarizer. Furthermore, the temperature is pinned to 0 to enforce factual responses, and the agent is instructed to state "Insufficient evidence" rather than guessing when data is missing.

## Trade-offs & Limitations
- Local In-Memory Storage: Currently, the dataframes and vector index live in memory. In a real-world scenario, the documents would live in a managed Vector DB and the tabular data would likely be queried directly via SQL from a relational database, rather than loading static CSVs into Pandas.

- API Rate Limits and Execution: Because the Pandas Agent writes and executes Python code iteratively, it can sometimes hit API rate limits on free-tier LLM endpoints. The current setup relies on LangChain's built-in exponential backoff to handle this gracefully. Additionally, using allow_dangerous_code=True was necessary for this local demonstration, but it is an unacceptable enterprise risk. Production tabular data would be stored in a relational database and queried via a strict, read-only Text-to-SQL pipeline.

## Future Enhancements for Production
1. Citation Enforcement: Prompt-based citations can be brittle. In production, I would use LangChain's with_structured_output and Pydantic to force the LLM to return a strict JSON schema containing the answer and the verified sources.

2. LangGraph Migration: I would migrate the control flow to a stateful LangGraph architecture. A graph-based state machine handles routing and looping much more robustly than standard Python conditional statements.