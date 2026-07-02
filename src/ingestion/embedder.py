import os
import glob
import json
import logging
# pyrefly: ignore [missing-import]
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import FAISS
# pyrefly: ignore [missing-import]
from langchain_core.documents import Document

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROCESSED_DATA_PATH, VECTOR_STORE_PATH, EMBEDDING_MODEL

def main():
    logging.info(f"Initializing Embedding Model: {EMBEDDING_MODEL}")
    
    # Initialize the BGE embedding model
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    # Load all chunks from JSON files
    json_files = glob.glob(os.path.join(PROCESSED_DATA_PATH, "*_chunks.json"))
    logging.info(f"Found {len(json_files)} chunk files.")
    
    documents = []
    
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        for chunk in chunks:
            # Create a LangChain Document for each chunk
            doc = Document(
                page_content=chunk["content"],
                metadata={
                    "chunk_id": chunk["chunk_id"],
                    "scheme_name": chunk["scheme_name"],
                    "category": chunk["category"],
                    "source_url": chunk["source_url"],
                    "scrape_date": chunk["scrape_date"]
                }
            )
            documents.append(doc)
            
    if not documents:
        logging.error("No chunks found to embed! Exiting.")
        return
        
    logging.info(f"Generated {len(documents)} Document objects. Building FAISS index...")
    
    # Create the FAISS index
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # Save the vector store to disk
    vectorstore.save_local(VECTOR_STORE_PATH)
    
    logging.info(f"Successfully saved FAISS index with {len(documents)} vectors to {VECTOR_STORE_PATH}.")

if __name__ == "__main__":
    main()
