from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import logging

from core.neo4j_graph_builder import Neo4jGraphBuilder
from services.graph_extractor import GraphExtractor
from api.routes import api, init_routes


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

neo4j_builder = Neo4jGraphBuilder()
graph_extractor = GraphExtractor(neo4j_builder)

init_routes(api, graph_extractor)
app.register_blueprint(api)

if __name__ == "__main__":
    print("Starting server...")
    app.run(host="0.0.0.0", debug=True, threaded=True)
