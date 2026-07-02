import logging
from src.ingestion import scraper, cleaner, chunker, embedder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting full Data Ingestion Pipeline...")
    
    try:
        logger.info("--- Step 1: Scraper ---")
        scraper.main()
        
        logger.info("--- Step 2: Cleaner ---")
        cleaner.main()
        
        logger.info("--- Step 3: Chunker ---")
        chunker.main()
        
        logger.info("--- Step 4: Embedder ---")
        embedder.main()
        
        logger.info("✅ Data Ingestion Pipeline completed successfully!")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
