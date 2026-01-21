"""Script to load documents into the vector database knowledge base."""
import logging
from database.vector_db import VectorDB
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def load_nscc_data():
    """Load NSCC knowledge base (primary data)."""
    from nscc_data import (
        nscc_pages_documents, nscc_pages_metadata,
        nscc_faq_documents, nscc_faq_metadata,
        events_documents, events_metadata
    )
    
    db = VectorDB(collection_name="documents")
    
    # Generate unique IDs for pages
    page_ids = [f"nscc_page_{i}" for i in range(len(nscc_pages_documents))]
    logger.info(f"Adding {len(nscc_pages_documents)} NSCC website documents...")
    db.add_documents(nscc_pages_documents, metadata=nscc_pages_metadata, ids=page_ids)
    
    # Generate unique IDs for FAQ
    faq_ids = [f"nscc_faq_{i}" for i in range(len(nscc_faq_documents))]
    logger.info(f"Adding {len(nscc_faq_documents)} NSCC FAQ documents...")
    db.add_documents(nscc_faq_documents, metadata=nscc_faq_metadata, ids=faq_ids)
    
    # Generate unique IDs for events
    event_ids = [f"event_{i+1}" for i in range(len(events_documents))]
    logger.info(f"Adding {len(events_documents)} campus event documents...")
    db.add_documents(events_documents, metadata=events_metadata, ids=event_ids)
    
    info = db.get_collection_info()
    logger.info(f"Knowledge base now contains {info['document_count']} documents")
    print(f"✓ NSCC knowledge base loaded successfully! ({info['document_count']} documents)")


def load_sample_documents():
    """Load sample documents into the vector database (BACKUP/LEGACY)."""
    
    # Initialize vector DB
    db = VectorDB(collection_name="documents")
    
    # Sample documents - replace with your actual website content
    documents = [
        # Example 1: Product information
        """Our AI-powered chatbot helps businesses automate customer support. 
        It integrates with existing systems and provides 24/7 assistance to customers 
        with natural language understanding.""",
        
        # Example 2: Features
        """Key features include: real-time responses, multi-language support, 
        sentiment analysis, conversation history tracking, and seamless integration 
        with popular CRM platforms like Salesforce and HubSpot.""",
        
        # Example 3: Pricing
        """We offer three pricing tiers: Starter ($29/month) for small businesses, 
        Professional ($99/month) for growing teams, and Enterprise (custom pricing) 
        for large organizations with advanced needs.""",
        
        # Example 4: Technical specs
        """The system uses state-of-the-art language models and can handle up to 
        10,000 concurrent conversations. API response time averages under 200ms 
        with 99.9% uptime SLA.""",
        
        # Example 5: Getting started
        """To get started, sign up for a free trial, configure your chatbot settings, 
        add your website URL, and embed the widget code on your site. Setup takes 
        about 5 minutes.""",
    ]
    
    # Optional: Add metadata for each document
    metadata = [
        {"source": "product_overview", "category": "general"},
        {"source": "features", "category": "technical"},
        {"source": "pricing", "category": "sales"},
        {"source": "technical_specs", "category": "technical"},
        {"source": "getting_started", "category": "onboarding"},
    ]
    
    # Add documents to vector DB
    logger.info(f"Adding {len(documents)} documents to knowledge base...")
    db.add_documents(documents, metadata=metadata)
    
    # Verify the documents were added
    info = db.get_collection_info()
    logger.info(f"Knowledge base now contains {info['document_count']} documents")
    
    # Test a search
    logger.info("\nTesting search functionality...")
    results = db.search("How much does it cost?", top_k=2)
    
    logger.info(f"\nTop search result:")
    logger.info(f"Text: {results[0]['text'][:100]}...")
    logger.info(f"Relevance: {1 - results[0]['distance']:.2%}")
    logger.info(f"Metadata: {results[0]['metadata']}")
    
    print("\n✓ Knowledge base loaded successfully!")


def load_from_text_file(file_path: str, chunk_size: int = 500):
    """
    Load documents from a text file, splitting into chunks.
    
    Args:
        file_path: Path to text file
        chunk_size: Size of each chunk in characters
    """
    db = VectorDB(collection_name="documents")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into chunks
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    # Create metadata for each chunk
    metadata = [{"source": file_path, "chunk_index": i} for i in range(len(chunks))]
    
    logger.info(f"Adding {len(chunks)} chunks from {file_path}...")
    db.add_documents(chunks, metadata=metadata)
    
    info = db.get_collection_info()
    logger.info(f"Knowledge base now contains {info['document_count']} documents")


def load_from_directory(directory_path: str):
    """
    Load all .txt files from a directory.
    
    Args:
        directory_path: Path to directory containing text files
    """
    import os
    
    db = VectorDB(collection_name="documents")
    documents = []
    metadata = []
    
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append(content)
                metadata.append({"source": filename, "file_path": file_path})
    
    logger.info(f"Adding {len(documents)} documents from {directory_path}...")
    db.add_documents(documents, metadata=metadata)
    
    info = db.get_collection_info()
    logger.info(f"Knowledge base now contains {info['document_count']} documents")


def clear_knowledge_base():
    """Clear all documents from the knowledge base."""
    db = VectorDB(collection_name="documents")
    db.clear_collection()
    logger.info("Knowledge base cleared")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load knowledge base")
    parser.add_argument(
        "--mode",
        choices=["nscc", "sample", "file", "directory", "clear"],
        default="nscc",
        help="Mode: 'nscc' (default - NSCC data), 'sample' (legacy dummy data), 'file', 'directory', or 'clear'"
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Path to file or directory (required for file/directory modes)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "nscc":
        load_nscc_data()
    elif args.mode == "sample":
        load_sample_documents()
    elif args.mode == "file":
        if not args.path:
            print("Error: --path required for file mode")
        else:
            load_from_text_file(args.path)
    elif args.mode == "directory":
        if not args.path:
            print("Error: --path required for directory mode")
        else:
            load_from_directory(args.path)
    elif args.mode == "clear":
        clear_knowledge_base()
