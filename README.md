# Story to Knowledge Graph API

This is a Flask-based API that converts story text into a knowledge graph using Neo4j and LLM-powered extraction. The API uses schema-based prompts to extract entities, relationships, and properties from text to create a structured graph representation.

## Features

- LLM-powered text analysis for entity and relationship extraction
- Schema-based knowledge graph generation
- Neo4j graph database integration
- RESTful API endpoints for graph operations
- CORS enabled for cross-origin requests
- Test data generation with Alice in Wonderland example

## Prerequisites

- Python 3.9+
- Neo4j Database (local or cloud instance)
- Conda (recommended for environment management)
- Access to LLM API (configuration required)

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

5. Configure LLM:

   - Set up your LLM API credentials in environment variables
   - Ensure the schema files are present in `data/graph/`:
     - `nodes_schema.json`: Defines entity types and their properties
     - `relationships_schema.json`: Defines relationship types and their properties

6. Run the application:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

- `POST /api/graph/create` - Create a new knowledge graph from text using LLM extraction
- `GET /api/graph/test` - Generate a test knowledge graph
- `GET /api/graph/data` - Get all nodes and relationships in the current graph
- `DELETE /api/graph/clear` - Clear the entire graph database

## Development

To modify the API for your needs:

1. Customize the extraction schemas:

   - Modify `data/graph/nodes_schema.json` to define new entity types
   - Modify `data/graph/relationships_schema.json` to define new relationship types
   - Update prompts in the prompt manager for better extraction

2. Extend the core functionality:

   - Enhance graph extraction logic in `services/graph_extractor.py`
   - Add new graph operations in `core/neo4j_graph_builder.py`
   - Modify LLM integration in `core/llm_client.py`
   - Add new API endpoints in `app.py`

3. Add additional dependencies to `requirements.txt`

## Example Usage

```python
# Create a test knowledge graph
curl -X GET http://localhost:5000/api/graph/test

# Create a knowledge graph from text using LLM extraction
curl -X POST -H "Content-Type: application/json" \
  -d '{"text":"Alice followed the White Rabbit into a magical garden. The Cheshire Cat appeared and guided Alice with cryptic advice."}' \
  http://localhost:5000/api/graph/create

# Get the current graph data
curl http://localhost:5000/api/graph/data

# Clear the graph
curl -X DELETE http://localhost:5000/api/graph/clear
```

## Graph Schema

The knowledge graph structure is defined by JSON schemas:

### Node Types (Entity Types)

Defined in `nodes_schema.json`:

- Character: Represents story characters with properties like name, description, traits
- Location: Represents places with properties like name, description, features
- (Additional types can be defined in the schema)

### Relationship Types

Defined in `relationships_schema.json`:

- LOCATED_AT: Character to Location
- KNOWS: Character to Character
- POSSESSES: Character to Item
- PART_OF: Location to Location
- (Additional types can be defined in the schema)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
