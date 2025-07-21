import os
import shutil
from pathlib import Path
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv

def clear_tmp_directory():
    """Clear the tmp directory when the program starts"""
    tmp_path = Path("tmp")
    if tmp_path.exists():
        try:
            shutil.rmtree(tmp_path)
            print("✅ Cleared tmp directory")
        except Exception as e:
            print(f"⚠️ Warning: Could not clear tmp directory: {e}")
    else:
        print("ℹ️ tmp directory does not exist, creating fresh")

# Clear tmp directory on startup
clear_tmp_directory()

load_dotenv()

# Create Local PDF knowledge base
knowledge_base = PDFKnowledgeBase(
    path="pdf",
    vector_db=LanceDb(
        table_name="pdf_documents",
        uri="tmp/lancedb",
        search_type=SearchType.vector,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)
# Load the knowledge base: Comment after first run as the knowledge base is already loaded
knowledge_base.load()

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
   # reasoning_model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge_base,
    # Add a tool to search the knowledge base which enables agentic RAG.
    # This is enabled by default when `knowledge` is provided to the Agent.
    search_knowledge=True,
    show_tool_calls=True,
    markdown=True,
)
agent.print_response(
    "What are Common failure modes for LLMs?", stream=True
)
