import os
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="PDF Chat API",
    description="A simple API to chat with your PDF documents",
    version="1.0.0"
)

# Global agent variable
pdf_agent = None

def setup_pdf_folders():
    """Setup PDF folders and move processed files"""
    pdf_folder = Path("pdf")
    processed_folder = pdf_folder / "processed"
    
    # Create folders if they don't exist
    pdf_folder.mkdir(exist_ok=True)
    processed_folder.mkdir(exist_ok=True)
    
    print(f"📁 PDF folder: {pdf_folder}")
    print(f"📁 Processed folder: {processed_folder}")
    
    return pdf_folder, processed_folder

def get_unprocessed_pdfs(pdf_folder, processed_folder):
    """Get list of PDF files that haven't been processed yet"""
    all_pdfs = list(pdf_folder.glob("*.pdf"))
    processed_pdfs = {f.name for f in processed_folder.glob("*.pdf")}
    
    unprocessed = [pdf for pdf in all_pdfs if pdf.name not in processed_pdfs]
    
    if unprocessed:
        print(f"📄 Found {len(unprocessed)} new PDF(s) to process:")
        for pdf in unprocessed:
            print(f"   • {pdf.name}")
    else:
        print("✅ All PDFs have been processed already")
    
    return unprocessed

def move_to_processed(pdf_file, processed_folder):
    """Move a PDF file to the processed folder"""
    try:
        destination = processed_folder / pdf_file.name
        shutil.move(str(pdf_file), str(destination))
        print(f"✅ Moved {pdf_file.name} to processed folder")
        return True
    except Exception as e:
        print(f"⚠️ Warning: Could not move {pdf_file.name}: {e}")
        return False

def process_new_pdfs():
    """Process only new PDF files and move them to processed folder"""
    pdf_folder, processed_folder = setup_pdf_folders()
    unprocessed_pdfs = get_unprocessed_pdfs(pdf_folder, processed_folder)
    
    if not unprocessed_pdfs:
        return True
    
    print("\n🔄 Processing new PDF files...")
    
    # Create a temporary folder for new PDFs
    temp_pdf_folder = Path("temp_pdf_processing")
    temp_pdf_folder.mkdir(exist_ok=True)
    
    try:
        # Copy unprocessed PDFs to temp folder
        for pdf_file in unprocessed_pdfs:
            shutil.copy2(pdf_file, temp_pdf_folder / pdf_file.name)
        
        # Create knowledge base with only new PDFs
        new_knowledge_base = PDFKnowledgeBase(
            path=str(temp_pdf_folder),
            vector_db=LanceDb(
                table_name="pdf_documents",
                uri="tmp/lancedb",
                search_type=SearchType.vector,
                embedder=OpenAIEmbedder(id="text-embedding-3-small"),
            ),
        )
        
        # Load the new knowledge base
        print("📚 Loading new PDF documents into knowledge base...")
        new_knowledge_base.load()
        print("✅ New PDFs processed successfully!")
        
        # Move processed PDFs to processed folder
        for pdf_file in unprocessed_pdfs:
            move_to_processed(pdf_file, processed_folder)
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing PDFs: {e}")
        return False
    finally:
        # Clean up temp folder
        if temp_pdf_folder.exists():
            shutil.rmtree(temp_pdf_folder)

def initialize_agent():
    """Initialize the PDF agent"""
    global pdf_agent
    
    # Process new PDFs if any
    process_new_pdfs()
    
    # Create knowledge base for all processed PDFs
    knowledge_base = PDFKnowledgeBase(
        path="pdf/processed",
        vector_db=LanceDb(
            table_name="pdf_documents",
            uri="tmp/lancedb",
            search_type=SearchType.vector,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
    )
    
    # Load the knowledge base
    print("📚 Loading all processed PDF documents into knowledge base...")
    knowledge_base.load()
    print("✅ Knowledge base loaded successfully!")
    
    # Create the PDF chat agent
    pdf_agent = Agent(
        name="PDF Chat Agent",
        model=OpenAIChat(id="gpt-4o"),
        reasoning_model=OpenAIChat(id="gpt-4o"),
        knowledge=knowledge_base,
        search_knowledge=True,
        show_tool_calls=True,
        markdown=True,
        add_history_to_messages=True,
        num_history_responses=3,
        add_datetime_to_instructions=True,
    )
    
    print("✅ Agent initialized successfully!")

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: str | None = None

# Initialize agent on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting PDF Chat API...")
    initialize_agent()

# API endpoints
@app.get("/")
async def root():
    return {"message": "PDF Chat API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "agent_ready": pdf_agent is not None}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Simple chat endpoint"""
    if pdf_agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Get response from agent
        response = pdf_agent.run(request.message)
        
        return ChatResponse(
            response=response.content,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/docs")
async def docs():
    """Redirect to Swagger UI"""
    return {"message": "Visit /docs for interactive API documentation"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting PDF Chat API server...")
    print("📖 Available endpoints:")
    print("   • POST /chat - Send a message to the agent")
    print("   • GET /health - Health check")
    print("   • GET /docs - API documentation (Swagger UI)")
    print(f"🌐 Server will be available at: http://localhost:8001")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8001) 