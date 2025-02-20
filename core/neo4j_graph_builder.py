from typing import Dict, List, Any, Optional
import os
from neo4j import GraphDatabase
import logging

class Neo4jGraphBuilder:
    def __init__(self):
        """Initialize Neo4j connection using environment variables"""
        # Configure logging to suppress notifications
        logging.getLogger("neo4j").setLevel(logging.WARNING)
        logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)
        
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'your-password')
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        """Close the Neo4j driver connection"""
        self.driver.close()

    def test_connection(self) -> bool:
        """Test the Neo4j connection"""
        try:
            with self.driver.session() as session:
                result = session.run('RETURN "Connection successful!" as message')
                return bool(result.single())
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            return False

    def create_node(self, label: str, properties: Dict) -> Dict:
        """Create a node with the given label and properties"""
        with self.driver.session() as session:
            cypher = f"""
                CREATE (n:{label} $properties)
                RETURN {{ 
                    elementId: elementId(n),
                    properties: properties(n)
                }} as node
            """
            result = session.run(cypher, properties=properties)
            return result.single()['node']

    def create_relationship(self, from_node_id: int, to_node_id: int, 
                          relationship_type: str, properties: Dict = {}) -> Dict:
        """Create a relationship between two nodes"""
        with self.driver.session() as session:
            cypher = f"""
                MATCH (from), (to)
                WHERE elementId(from) = $from_id AND elementId(to) = $to_id
                CREATE (from)-[r:{relationship_type} $properties]->(to)
                RETURN r
            """
            result = session.run(cypher, 
                               from_id=from_node_id, 
                               to_id=to_node_id, 
                               properties=properties)
            return result.single()['r']

    def get_node_by_id(self, node_id: int) -> Optional[Dict]:
        """Get a node by its ID"""
        with self.driver.session() as session:
            cypher = """
                MATCH (n)
                WHERE elementId(n) = $node_id
                RETURN n
            """
            result = session.run(cypher, node_id=node_id)
            record = result.single()
            return record['n'] if record else None

    def get_nodes_by_label(self, label: str) -> List[Dict]:
        """Get all nodes with a specific label"""
        with self.driver.session() as session:
            cypher = f"""
                MATCH (n:{label})
                RETURN n
            """
            result = session.run(cypher)
            return [record['n'] for record in result]

    def get_relationships(self, from_node_id: int, to_node_id: int) -> List[Dict]:
        """Get relationships between two nodes"""
        with self.driver.session() as session:
            cypher = """
                MATCH (from)-[r]->(to)
                WHERE elementId(from) = $from_id AND elementId(to) = $to_id
                RETURN r
            """
            result = session.run(cypher, from_id=from_node_id, to_id=to_node_id)
            return [record['r'] for record in result]

    def delete_node(self, node_id: int) -> bool:
        """Delete a node and its relationships"""
        with self.driver.session() as session:
            cypher = """
                MATCH (n)
                WHERE elementId(n) = $node_id
                DETACH DELETE n
            """
            result = session.run(cypher, node_id=node_id)
            return result.consume().counters.nodes_deleted > 0

    def update_node(self, node_id: int, properties: Dict) -> Optional[Dict]:
        """Update node properties"""
        with self.driver.session() as session:
            cypher = """
                MATCH (n)
                WHERE elementId(n) = $node_id
                SET n += $properties
                RETURN n
            """
            result = session.run(cypher, node_id=node_id, properties=properties)
            record = result.single()
            return record['n'] if record else None

    def clear_database(self) -> bool:
        """Clear all nodes and relationships from the database"""
        with self.driver.session() as session:
            cypher = """
                MATCH (n)
                DETACH DELETE n
            """
            result = session.run(cypher)
            return result.consume().counters.nodes_deleted > 0

    def initialize_sample_graph(self) -> bool:
        """Initialize a sample knowledge graph"""
        try:
            self.clear_database()
            with self.driver.session() as session:
                cypher = """
                    // Create People
                    CREATE (alice:Person {name: 'Alice Smith', age: 30, occupation: 'Software Engineer'})
                    CREATE (bob:Person {name: 'Bob Johnson', age: 35, occupation: 'Data Scientist'})
                    CREATE (charlie:Person {name: 'Charlie Brown', age: 28, occupation: 'Project Manager'})
                    
                    // Create Companies
                    CREATE (techCorp:Company {name: 'TechCorp', industry: 'Technology', founded: 2010})
                    CREATE (dataInc:Company {name: 'DataInc', industry: 'Data Analytics', founded: 2015})
                    
                    // Create Projects
                    CREATE (webApp:Project {name: 'Web Application', status: 'In Progress', priority: 'High'})
                    CREATE (mlModel:Project {name: 'ML Model Development', status: 'Planning', priority: 'Medium'})
                    
                    // Create Relationships
                    CREATE (alice)-[:WORKS_AT {since: 2019}]->(techCorp)
                    CREATE (bob)-[:WORKS_AT {since: 2020}]->(dataInc)
                    CREATE (charlie)-[:WORKS_AT {since: 2018}]->(techCorp)
                    CREATE (alice)-[:MANAGES]->(webApp)
                    CREATE (bob)-[:MANAGES]->(mlModel)
                    CREATE (charlie)-[:COLLABORATES_WITH {project: 'Web Application'}]->(alice)
                    CREATE (alice)-[:COLLABORATES_WITH {project: 'ML Model'}]->(bob)
                """
                session.run(cypher)
                return True
        except Exception as e:
            print(f"Error initializing sample graph: {str(e)}")
            return False

    def get_graph_data(self) -> Dict[str, List[Dict]]:
        """Get all nodes and relationships in the graph"""
        with self.driver.session() as session:
            cypher = """
                MATCH (n)
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN COLLECT(DISTINCT {
                    id: elementId(n),
                    labels: labels(n),
                    properties: properties(n)
                }) as nodes,
                COLLECT(DISTINCT CASE WHEN r IS NOT NULL THEN {
                    source: elementId(startNode(r)),
                    target: elementId(endNode(r)),
                    type: type(r),
                    properties: properties(r)
                } END) as relationships
            """
            result = session.run(cypher)
            record = result.single()
            return {
                'nodes': [node for node in record['nodes'] if node],
                'relationships': [rel for rel in record['relationships'] if rel]
            } 