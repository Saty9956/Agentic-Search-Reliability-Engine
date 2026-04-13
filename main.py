import os
import logging
import json
import pandas as pd
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Configure Enterprise Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

DATA_DIR = r"C:\Users\Satyartha Shukla\Desktop\BPSS_Agentic_AI_Interview_Dataset\bpss_agentic_dataset"

class EnterpriseAIAgent:
    def __init__(self):
        logger.info("Initializing Stateful BPSS Agentic System...")
        self.llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0) 
        self.retriever = None
        self.pandas_agent = None
        
        self.chat_history = [] 
        self.max_history_turns = 3 
        
        self._prepare_data_tools()

    def _prepare_data_tools(self):
        unstructured_docs = []
        structured_dfs = {}

        logger.info(f"Scanning directory tree at: {DATA_DIR}")
        for root, dirs, files in os.walk(DATA_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                ext = file.lower()
                try:
                    if ext.endswith('.pdf'):
                        docs = PyPDFLoader(file_path).load()
                        for doc in docs: doc.metadata['source'] = file
                        unstructured_docs.extend(docs)
                    elif ext.endswith(('.docx', '.doc')):
                        docs = Docx2txtLoader(file_path).load()
                        for doc in docs: doc.metadata['source'] = file
                        unstructured_docs.extend(docs)
                    elif ext.endswith('.md'):
                        docs = TextLoader(file_path, encoding='utf-8').load()
                        for doc in docs: doc.metadata['source'] = file
                        unstructured_docs.extend(docs)
                    elif ext.endswith('.csv'):
                        structured_dfs[file] = pd.read_csv(file_path)
                    elif ext.endswith('.xlsx'):
                        structured_dfs[file] = pd.read_excel(file_path)
                except Exception as e:
                    logger.warning(f"Failed to process {file}: {str(e)}. Skipping.")

        # Build Vector Store for Unstructured Data
        if unstructured_docs:
            logger.info(f"Building Vector Index for {len(unstructured_docs)} document chunks...")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            splits = text_splitter.split_documents(unstructured_docs)
            
            for i, split in enumerate(splits):
                split.metadata['chunk_id'] = f"chunk_{i}"
                
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vectorstore = FAISS.from_documents(splits, embeddings)
            self.retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

        # Build Tabular Agent for Structured Data
        if structured_dfs:
            logger.info(f"Initializing Tabular Engine for {len(structured_dfs)} datasets...")
            df_list = list(structured_dfs.values())
            df_names = list(structured_dfs.keys())
            
            prefix = f"""You are analyzing these dataframes: {', '.join(df_names)}.
SECURITY RESTRICTION: You are only allowed to perform read-only analytical operations.
OUTPUT FORMAT: You MUST return your final answer strictly as a valid JSON object with the following keys:
{{{{
    "analysis": "your textual answer",
    "source_dataframe": "exact name of the file used",
    "rows_referenced": [list of integer row indices]
}}}}"""
            self.pandas_agent = create_pandas_dataframe_agent(
                self.llm, df_list, verbose=False, allow_dangerous_code=True, prefix=prefix, handle_parsing_errors=True, max_iterations=3
            )

    def _format_history(self) -> str:
        if not self.chat_history:
            return "No previous conversation history."
        
        history_text = ""
        for i, (q, a) in enumerate(self.chat_history):
            history_text += f"Turn {i+1}:\nUser: {q}\nAI: {a}\n\n"
        return history_text

    def query(self, user_question: str) -> str:
        logger.info(f"Analyzing Query: {user_question}")
        
        history_context = self._format_history()
        
        router_prompt = f"""Analyze this user question, keeping in mind the recent conversation history in case they use pronouns like 'he', 'it', or 'that'.
        
        --- RECENT CONVERSATION HISTORY ---
        {history_context}
        -----------------------------------
        
        Current User Question: "{user_question}"
        
        Does the current question require:
        1. Checking policies, text notes, candidate word docs, or PDFs (Reply exactly 'DOCS')
        2. Checking trackers, CSVs, or Excel tabular data (Reply exactly 'TABULAR')
        3. Cross-referencing both documents and tabular data (Reply exactly 'BOTH')
        
        Reply with JUST THE WORD and nothing else."""
        
        intent = self.llm.invoke(router_prompt).content.strip().upper()
        logger.info(f"Router Decision: {intent}")
        
        context = ""
        
        if "DOCS" in intent or "BOTH" in intent:
            if self.retriever:
                logger.info("Fetching unstructured evidence from Vector DB...")
                search_query = f"{user_question} (Context: {self.chat_history[-1][0] if self.chat_history else ''})"
                docs = self.retriever.invoke(search_query)
                context += "\n--- UNSTRUCTURED DOCUMENT EVIDENCE ---\n"
                for d in docs:
                    src = d.metadata.get('source', 'Unknown')
                    page = d.metadata.get('page', 'N/A')
                    chunk = d.metadata.get('chunk_id', 'Unknown')
                    context += f"Source: {src} | Page: {page} | Chunk ID: {chunk}\nContent: {d.page_content}\n\n"
            
        if "TABULAR" in intent or "BOTH" in intent:
            if self.pandas_agent:
                logger.info("Executing analytical queries on Tabular Data...")
                try:
                    tabular_raw = self.pandas_agent.invoke({"input": f"Given the context of our chat: {history_context}, answer this: {user_question}"}).get("output")
                    
                    try:
                        if "```json" in tabular_raw:
                            json_str = tabular_raw.split("```json")[1].split("```")[0].strip()
                        else:
                            json_str = tabular_raw
                            
                        tabular_json = json.loads(json_str)
                        context += f"\n--- STRUCTURED TABULAR EVIDENCE ---\n"
                        context += f"Analysis: {tabular_json.get('analysis', 'N/A')}\n"
                        context += f"Verified Source Table: {tabular_json.get('source_dataframe', 'N/A')}\n"
                        context += f"Verified Rows: {tabular_json.get('rows_referenced', 'N/A')}\n"
                    except json.JSONDecodeError:
                        logger.warning("Tabular agent failed strict JSON format. Using raw output.")
                        context += f"\n--- STRUCTURED TABULAR EVIDENCE (Raw) ---\n{tabular_raw}\n"
                except Exception as e:
                    logger.error(f"Tabular execution failed: {e}")
                    context += "\n--- STRUCTURED TABULAR EVIDENCE ---\nError retrieving tabular data.\n"

        logger.info("Synthesizing Final Answer...")
        synthesis_prompt = f"""You are an elite Enterprise Compliance AI answering queries for a BPSS screening audit.
        Answer the current question based STRICTLY AND ONLY on the provided evidence and the conversation history.
        
        CRITICAL RULES:
        1. STRUCTURAL CITATIONS: You MUST cite the exact 'Source' filename, 'Page', and 'Chunk ID' for documents. For tabular data, cite the 'Verified Source Table' and 'Verified Rows'.
        2. CONTRADICTIONS: If the structured data and unstructured data conflict, state the contradiction explicitly.
        3. MISSING DATA: If the provided evidence does not contain the answer, say "Insufficient evidence to answer this regarding [Topic]". DO NOT GUESS.
        
        --- RECENT CONVERSATION HISTORY ---
        {history_context}
        
        --- EVIDENCE CONTEXT ---
        {context}
        
        Current User Question: {user_question}
        """
        
        final_answer = self.llm.invoke(synthesis_prompt).content
        
        self.chat_history.append((user_question, final_answer))
        if len(self.chat_history) > self.max_history_turns:
            self.chat_history.pop(0) 
            
        return final_answer

if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        logger.critical("GROQ_API_KEY missing. Please check .env file.")
        exit(1)
        
    ai_system = EnterpriseAIAgent()
    
    print("\n" + "="*60)
    print(" 🚀 STATEFUL BPSS AGENTIC SCREENING SYSTEM READY")
    print("="*60)
    
    while True:
        user_input = input("\n[EY Evaluator] Ask a question: ")
        if not user_input.strip(): continue
        if user_input.lower() in ['exit', 'quit']: break
        
        response = ai_system.query(user_input)
        
        print("\n" + "-"*60)
        print("🤖 AI RESPONSE:")
        print("-" * 60)
        print(response)
        print("-" * 60 + "\n")