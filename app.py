import os
import shutil
from pathlib import Path
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv

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

load_dotenv()

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

agent = Agent(
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
    instructions="""
You are a PDF Chat Agent that can ONLY answer questions about the content of the PDF documents in your knowledge base.

IMPORTANT RULES:
1. ONLY answer questions that are directly related to the content of the PDF documents you have access to
2. If a question is not related to the PDF content, respond with: "I can only answer questions about the content of the PDF documents in my knowledge base. This question appears to be outside the scope of the available documents. Please ask me about the content of the uploaded PDF files."
3. If you cannot find relevant information in the PDF documents to answer a question, say: "I cannot find information about this topic in the available PDF documents. Please check if the relevant document has been uploaded or rephrase your question to focus on the content of the uploaded files."
4. Always base your answers on the actual content of the PDF documents, not on general knowledge
5. If asked about topics not covered in the PDFs, politely redirect the user to ask about the PDF content instead

Your responses should be helpful, accurate, and strictly based on the PDF content available to you.
""",
)

def chat_with_pdf():
    """Interactive chat interface for asking questions about PDF documents"""
    print("\n" + "="*60)
    print("📚 PDF Chat Interface")
    print("="*60)
    print("Ask questions about your PDF documents. Type 'quit' or 'exit' to end the chat.")
    print("Type 'help' for available commands and example questions.")
    print("Type 'list' to see available PDF documents.")
    print("Type 'refresh' to check for new PDF files.")
    print("-"*60)
    
    while True:
        try:
            # Get user input
            user_question = input("\n🤔 Your question: ").strip()
            
            # Check for exit commands
            if user_question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Thanks for using the PDF chat.")
                break
            
            # Check for help command
            if user_question.lower() == 'help':
                print("\n💡 Example questions you can ask:")
                print("• What are the main topics covered in the documents?")
                print("• Can you summarize the key points?")
                print("• What are the common failure modes for LLMs?")
                print("• Explain the concepts mentioned in the documents")
                print("• What are the best practices discussed?")
                print("• Can you provide examples from the documents?")
                print("\n🔧 Available commands:")
                print("• 'help' - Show this help message")
                print("• 'refresh' - Check for new PDF files")
                print("• 'list' or 'pdfs' - Show available PDF documents")
                print("• 'quit' or 'exit' - End the chat")
                continue
            
            # Check for refresh command
            if user_question.lower() == 'refresh':
                print("\n🔄 Checking for new PDF files...")
                if process_new_pdfs():
                    print("✅ Refresh completed!")
                else:
                    print("❌ Refresh failed!")
                continue
            
            # Check for list command
            if user_question.lower() in ['list', 'pdfs', 'files']:
                print("\n📄 Available PDF documents:")
                pdf_folder = Path("pdf/processed")
                if pdf_folder.exists():
                    pdf_files = list(pdf_folder.glob("*.pdf"))
                    if pdf_files:
                        for i, pdf_file in enumerate(pdf_files, 1):
                            print(f"   {i}. {pdf_file.name}")
                    else:
                        print("   No PDF files found in processed folder.")
                else:
                    print("   Processed folder does not exist.")
                continue
            
            # Skip empty questions
            if not user_question:
                print("❌ Please enter a question.")
                continue
            
            print("\n🤖 Generating response...")
            print("-"*40)
            
            # Get response from agent
            response = agent.run(user_question)
            
            print("📄 Response:")
            print(response.content)
            print("-"*40)
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try asking your question again.")

if __name__ == "__main__":
    chat_with_pdf()
