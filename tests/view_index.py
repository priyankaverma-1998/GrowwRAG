import os
import sys
import logging
# pyrefly: ignore [missing-import]
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import FAISS

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import VECTOR_STORE_PATH, EMBEDDING_MODEL

def main():
    print("=========================================")
    print(f"Loading Embedding Model ({EMBEDDING_MODEL})...")
    print("=========================================")
    
    # Initialize the same embeddings model we used to generate the index
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print(f"Loading FAISS index from: {VECTOR_STORE_PATH}...")
    try:
        # Load the index
        # allow_dangerous_deserialization=True is required by FAISS >= 1.7 to load local pickle files safely.
        vectorstore = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        print(f"SUCCESS: Successfully loaded FAISS vector database with {vectorstore.index.ntotal} vectors!\n")
    except Exception as e:
        print(f"ERROR: Error loading index: {e}")
        return

    # Let's do a test query to see what it retrieves
    query = "What is the exit load for HDFC Large Cap Fund?"
    print("=========================================")
    print(f"Running Test Query: '{query}'")
    print("=========================================")
    
    # Perform similarity search (fetch top 1 most relevant chunk)
    results = vectorstore.similarity_search_with_score(query, k=1)
    
    for i, (doc, score) in enumerate(results):
        print(f"\n--- Result {i+1} (Distance Score: {score:.4f}) ---")
        print(doc.page_content)
        print("-" * 20)
        
    print("\n=========================================")
    print("Viewing the actual Numerical Embeddings!")
    print("=========================================")
    print("Converting the query into a mathematical vector...")
    vector = embeddings.embed_query(query)
    
    print(f"\nVector Dimensions: {len(vector)} (Because BGE-small uses 384 dimensions)")
    print(f"Raw Vector Array (Preview of first 10 numbers):")
    print(f"[{', '.join(f'{x:.5f}' for x in vector[:10])}, ... ]")
    
    print("\nScript completed successfully.")

if __name__ == "__main__":
    main()
