import logging
from src.pipeline import query_guard
from src.pipeline.retriever import Retriever
from src.pipeline.generator import Generator
from src.pipeline import formatter

logger = logging.getLogger(__name__)

# Initialize singletons for retriever and generator to avoid reloading models/clients per query
try:
    retriever_instance = Retriever()
except Exception as e:
    logger.error(f"Failed to initialize Retriever: {e}")
    retriever_instance = None

try:
    generator_instance = Generator()
except Exception as e:
    logger.error(f"Failed to initialize Generator: {e}")
    generator_instance = None


def answer_query(query: str) -> dict:
    """
    Orchestrates the full query-to-response flow:
    1. Query Guard
    2. Retriever
    3. Generator
    4. Formatter
    """
    logger.info(f"Processing query: '{query}'")

    # 1. Check intent
    guard_result = query_guard.classify(query)
    if guard_result.is_refused:
        logger.info(f"Query refused. Intent: {guard_result.intent}")
        return formatter.format_refusal(guard_result)

    # Validate pipeline readiness
    if not retriever_instance or not generator_instance:
        return formatter.format_general_error("Pipeline components are not fully initialized.")

    # 2. Retrieve chunks
    logger.info("Retrieving chunks...")
    retrieved_chunks = retriever_instance.retrieve(query)
    
    if not retrieved_chunks:
        logger.info("No relevant chunks found. Marking as out of scope.")
        return formatter.format_answer({"text": "I don't have this information in my current sources.", "error": None}, [])

    # 3. Generate answer
    logger.info("Generating response from LLM...")
    llm_response = generator_instance.generate_answer(retrieved_chunks, query)

    # 4. Format response
    logger.info("Formatting response...")
    final_response = formatter.format_answer(llm_response, retrieved_chunks)
    
    return final_response
