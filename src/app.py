import os
import sys
import logging
from flask import Flask, render_template, request, jsonify

# Ensure the root directory is on the path so we can import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline.rag_chain import answer_query, retriever_instance

# Initialize Flask app
app = Flask(__name__)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/")
def index():
    """Render the main chat interface."""
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat queries and return RAG pipeline responses."""
    try:
        data = request.json
        if not data or "query" not in data:
            return jsonify({"status": "error", "message": "No query provided"}), 400

        query = data["query"]
        
        # Check system health
        if not retriever_instance or not retriever_instance.vectorstore:
            logger.warning("Retriever instance is degraded or offline.")
            # Can return a specific error if we want the frontend to show the error state
            # but let's let the pipeline attempt or return a known error format.
            # Actually, returning 503 Service Unavailable triggers the error state nicely
            return jsonify({"status": "error", "message": "System Offline - Retriever unavailable."}), 503

        # Process query with RAG pipeline
        response = answer_query(query)
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
