from typing import Dict, List, Any
import json
import os

# from core.prompt_manager import PromptManager
# from core.llm_client import LLMClient
from core.neo4j_graph_builder import Neo4jGraphBuilder
from core.llm_client import LLMClient
from services.prompt_manager import PromptManager

class GraphExtractor:
    def __init__(self, neo4j_builder: Neo4jGraphBuilder, llm_client=LLMClient):
        # llm_client is optional for now
        self.neo4j_builder = neo4j_builder
        self.llm_client = llm_client

    def create_test_knowledge_graph(self) -> Dict[str, Any]:
        """
        Creates a test knowledge graph in Neo4j using hard-coded data.
        Returns a structured response with metadata and graph data.
        
        Returns:
            Dict with the following structure:
            {
                "metadata": {
                    "version": "1.0",
                    "description": "Test knowledge graph from Alice in Wonderland",
                    "node_count": int,
                    "relationship_count": int,
                    "node_types": List[str],
                    "relationship_types": List[str]
                },
                "graph_data": {
                    "nodes": List[Dict],
                    "relationships": List[Dict]
                },
                "status": {
                    "success": bool,
                    "message": str
                }
            }
        """
        if not self.neo4j_builder:
            return {
                "status": {
                    "success": False,
                    "message": "Neo4j builder not initialized"
                }
            }

        try:
            print("Creating test knowledge graph")
            # Clear existing data
            self.neo4j_builder.clear_database()
            
            # Create nodes
            nodes = [
                {
                    "label": "Character",
                    "properties": {
                        "name": "Alice",
                        "description": "A curious adventurer in Wonderland",
                        "age": 12,
                        "traits": ["curious", "brave", "intelligent"]
                    }
                },
                {
                    "label": "Character",
                    "properties": {
                        "name": "White Rabbit",
                        "description": "A peculiar character always in a hurry",
                        "occupation": "Royal Herald",
                        "traits": ["anxious", "punctual"]
                    }
                },
                {
                    "label": "Character",
                    "properties": {
                        "name": "Cheshire Cat",
                        "description": "Known for its enigmatic smile",
                        "magical_abilities": ["invisibility", "teleportation"],
                        "traits": ["mysterious", "intelligent"]
                    }
                },
                {
                    "label": "Location",
                    "properties": {
                        "name": "Wonderland Garden",
                        "description": "A magical garden with talking flowers",
                        "features": ["talking flowers", "maze"],
                        "size": "vast"
                    }
                }
            ]

            # Create nodes and store their IDs
            node_ids = {}
            for node_data in nodes:
                node = self.neo4j_builder.create_node(node_data["label"], node_data["properties"])
                node_ids[node_data["properties"]["name"]] = node["elementId"]

            # Create relationships
            relationships = [
                {
                    "from_node": "Alice",
                    "to_node": "Wonderland Garden",
                    "type": "VISITS",
                    "properties": {
                        "duration": "2 hours",
                        "activities": ["talking to flowers", "exploring"]
                    }
                },
                {
                    "from_node": "Alice",
                    "to_node": "White Rabbit",
                    "type": "FOLLOWS",
                    "properties": {
                        "reason": "curiosity",
                        "distance": "long"
                    }
                },
                {
                    "from_node": "Cheshire Cat",
                    "to_node": "Alice",
                    "type": "GUIDES",
                    "properties": {
                        "advice_given": ["all paths lead somewhere", "we're all mad here"],
                        "manner": "cryptic"
                    }
                }
            ]

            # Create relationships in Neo4j
            created_relationships = []
            for rel_data in relationships:
                from_id = node_ids[rel_data["from_node"]]
                to_id = node_ids[rel_data["to_node"]]
                rel = self.neo4j_builder.create_relationship(
                    from_id,
                    to_id,
                    rel_data["type"],
                    rel_data["properties"]
                )
                created_relationships.append(rel)

            # Get the complete graph data
            graph_data = self.neo4j_builder.get_graph_data()

            # Extract unique node and relationship types
            node_types = list(set(node["label"] for node in nodes))
            relationship_types = list(set(rel["type"] for rel in relationships))

            return {
                "metadata": {
                    "version": "1.0",
                    "description": "Test knowledge graph from Alice in Wonderland",
                    "node_count": len(graph_data["nodes"]),
                    "relationship_count": len(graph_data["relationships"]),
                    "node_types": node_types,
                    "relationship_types": relationship_types
                },
                "graph_data": graph_data,
                "status": {
                    "success": True,
                    "message": "Knowledge graph created successfully"
                }
            }

        except Exception as e:
            return {
                "status": {
                    "success": False,
                    "message": f"Error creating knowledge graph: {str(e)}"
                }
            }

    def extract_graph_nodes(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract nodes and relationships from text using predefined patterns.
        Returns a dictionary containing nodes and relationships.
        
        Note: This is a placeholder implementation. The actual LLM-based implementation
        will be added later.
        """
        # Placeholder implementation without LLM
        return {
            "metadata": {
                "version": "1.0",
                "description": "Knowledge graph from input text (placeholder)",
                "node_count": 0,
                "relationship_count": 0,
                "node_types": [],
                "relationship_types": []
            },
            "graph_data": {
                "nodes": [],
                "relationships": []
            },
            "status": {
                "success": True,
                "message": "LLM implementation pending"
            }
        }

    def extract_graph_relations(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract relationships from text using predefined patterns.
        Returns a dictionary containing relationships.
        
        Note: This is a placeholder implementation. The actual LLM-based implementation
        will be added later.
        """
        # Placeholder implementation without LLM
        return {
            "metadata": {
                "version": "1.0",
                "description": "Knowledge graph from input text (placeholder)",
                "node_count": 0,
                "relationship_count": 0,
                "node_types": [],
                "relationship_types": []
            },
            "graph_data": {
                "nodes": [],
                "relationships": []
            },
            "status": {
                "success": True,
                "message": "LLM implementation pending"
            }
        }

    def extract_graph_nodes_and_relations(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract both nodes and relationships from text using predefined patterns.
        Returns a dictionary containing nodes and relationships.
        
        Note: This is a placeholder implementation. The actual LLM-based implementation
        will be added later.
        """
        GRAPH_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'graph')
        try:
            with open(os.path.join(GRAPH_DIR, 'nodes_schema.json'), 'r') as f:
                schema_json = json.load(f)
            schema_json = json.dumps(schema_json)
            # Get the system and user prompts
            system_prompt_nodes = PromptManager.get_prompt("system", "GRAPH_NODE_EXTRACTOR")
            user_prompt_nodes = PromptManager.get_prompt("user", "GRAPH_NODE_EXTRACTOR", text=text, schema_json=schema_json)
            # print("--------------------------------")
            # print(system_prompt_nodes)
            # print("--------------------------------")
            # print("--------------------------------")
            # print(user_prompt_nodes)
            # print("--------------------------------")

        except Exception as e:
            print(f"Error loading prompts: {e}")
            return {
                "status": {
                    "success": False,
                    "message": f"Error loading prompts: {e}"
                }
            }
        
        try:
            response = self.llm_client.generate_json(
                    prompt=user_prompt_nodes,
                    system_prompt=system_prompt_nodes,
                    nsfw=False
            )

            extracted_data = json.loads(response)
        except Exception as e:
            print(f"Error generating LLM Response: {e}")
            return {
                "status": {
                    "success": False,
                    "message": f"Error generating LLM Response: {e}"
                }
            }
        
        try:
            nodes = extracted_data.get("nodes", [])
            self.neo4j_builder.clear_database()
            node_ids = {}
            for node_data in nodes:
                properties = node_data["properties"]
                # Ensure required properties exist and clean properties
                if "name" not in node_data["properties"]:
                    continue
                    
                node = self.neo4j_builder.create_node(node_data["type"], properties)
                node_ids[properties["name"]] = node["elementId"]
                # Get the complete graph data
            graph_data = self.neo4j_builder.get_graph_data()
            graphdb_nodes = graph_data["nodes"]
            node_types = list(set(node["type"] for node in nodes))
        except Exception as e:
            print(f"Error creating graph nodes: {e}")
            return {
                "status": {
                    "success": False,
                    "message": f"Error creating graph nodes: {e}"
                }
            }
        
        try:
            with open(os.path.join(GRAPH_DIR, 'relationships_schema.json'), 'r') as f:
                schema_json = json.load(f)
            schema_json = json.dumps(schema_json)
            # Get the system and user prompts
            system_prompt_relations = PromptManager.get_prompt("system", "GRAPH_RELATIONSHIP_EXTRACTOR")
            user_prompt_relations = PromptManager.get_prompt("user", "GRAPH_RELATIONSHIP_EXTRACTOR", text=text, schema_json=schema_json, nodes_list=graphdb_nodes)
            # print("--------------------------------")
            # print(system_prompt_relations)
            # print("--------------------------------")
            # print("--------------------------------")
            # print(user_prompt_relations)
            # print("--------------------------------")
        except Exception as e:
            print(f"Error loading relationship prompts: {e}")
            return {
                "status": {
                    "success": False,
                    "message": f"Error loading relationship prompts: {e}"
                }
            }
        
        try:
            response = self.llm_client.generate_json(
                    prompt=user_prompt_relations,
                    system_prompt=system_prompt_relations,
                    nsfw=False
            )

            extracted_data = json.loads(response)
            relationships = extracted_data.get("relationships", [])

            #add relationships to neo4j
            for rel in relationships:
                from_id = rel["source_node"]
                to_id = rel["target_node"]
                properties = rel["properties"]
                self.neo4j_builder.create_relationship(from_id, to_id, rel["type"], rel["properties"])
            
            relationship_types = list(set(rel["type"] for rel in extracted_data["relationships"]))
            graph_data = self.neo4j_builder.get_graph_data()
        except Exception as e:
            print(f"Error creating graph relationships: {e}")
            return {
                "status": {
                    "success": False,
                    "message": f"Error creating graph relationships: {e}"
                }
            }
        
        return {
                "metadata": {
                    "version": "1.0",
                    "description": "Knowledge graph from input text",
                    "node_count": len(graph_data["nodes"]),
                    "relationship_count": len(graph_data["relationships"]),
                    "node_types": node_types,
                    "relationship_types": relationship_types
                },
                "graph_data": graph_data,
                "status": {
                    "success": True,
                    "message": "Knowledge graph created successfully"
                }
            }


