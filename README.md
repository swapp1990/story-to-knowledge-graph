# Story to Knowledge Graph API

This is a Flask-based API that converts story text into a knowledge graph using Neo4j. The API extracts entities, relationships, and properties from text to create a structured graph representation.

## Features

- Convert story text into knowledge graph nodes and relationships
- Neo4j graph database integration
- RESTful API endpoints for graph operations
- CORS enabled for cross-origin requests
- Test data generation with Alice in Wonderland example

## Prerequisites

- Python 3.9+
- Neo4j Database (local or cloud instance)
- Conda (recommended for environment management)

## Setup

1. Clone the repository:

```bash
git clone <your-repo-url>
cd story-to-knowledge-graph
```

2. Create a Conda environment:

```bash
conda create -n knowledge-graph python=3.9
conda activate knowledge-graph
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up Neo4j:

   - Install and start Neo4j (local) or create a cloud instance
   - Set the following environment variables:
     ```bash
     NEO4J_URI=bolt://localhost:7687  # or your cloud URI
     NEO4J_USER=neo4j
     NEO4J_PASSWORD=your-password
     ```

5. Run the application:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

- `POST /api/graph/create` - Create a new knowledge graph from text
- `GET /api/graph/test` - Generate a test knowledge graph (Alice in Wonderland example)
- `GET /api/graph/data` - Get all nodes and relationships in the current graph
- `DELETE /api/graph/clear` - Clear the entire graph database

## Development

To modify the API for your needs:

1. Extend the graph extraction logic in `services/graph_extractor.py`
2. Add new graph operations in `core/neo4j_graph_builder.py`
3. Add new API endpoints in `app.py`
4. Add additional dependencies to `requirements.txt`

## Example Usage

```python
# Create a test knowledge graph
curl -X GET http://localhost:5000/api/graph/test

# Create a knowledge graph from text
curl -X POST -H "Content-Type: application/json" \
  -d '{"text":"Your story text here"}' \
  http://localhost:5000/api/graph/create

# Get the current graph data
curl http://localhost:5000/api/graph/data

# Clear the graph
curl -X DELETE http://localhost:5000/api/graph/clear
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
