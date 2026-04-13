# BPSS Agentic AI System

A backend-focused Agentic RAG system built to interpret enterprise compliance policies, analyze candidate trackers, and cross-reference structured and unstructured data to determine BPSS screening statuses.

## Design Overview
Instead of relying on a standard black-box agent framework, this system utilizes a Custom Semantic Router. It evaluates the user's intent to dynamically decide whether to query unstructured text, execute Pandas dataframe operations, or cross-reference both. This ensures deterministic outputs, reduces token costs, and severely limits hallucination.

## Prerequisites
- Python 3.9+
- A valid Groq API Key

## Setup Instructions

1. Environment Setup:
Clone the repository and navigate to the project directory. Create and activate a virtual environment:
python -m venv .venv
source .venv/bin/activate

2. Install Dependencies:
Install the required libraries for local vector processing and tabular analysis:
pip install pandas python-dotenv langchain-community langchain-huggingface langchain-groq langchain-experimental faiss-cpu pypdf docx2txt openpyxl

3. Configure Environment Variables:
Create a .env file in the root directory and add your Groq API key:
GROQ_API_KEY=your_api_key_here

4. Verify Dataset Path:
Open the main python script and ensure the DATA_DIR variable points to your local bpss_agentic_dataset folder.

## How to Run

Execute the main script via the command line:
python main.py

Type your questions at the prompt. The system maintains conversation history, so you can ask follow-up questions referencing previous answers. Type exit to quit.