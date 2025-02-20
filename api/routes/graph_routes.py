from flask import Blueprint, request, jsonify

def register_routes(api, graph_extractor):
    @api.route("/graph/test", methods=["POST"])
    def test_graph():
        #Use create_test_knowledge_graph
        graph_data = graph_extractor.create_test_knowledge_graph()
        return jsonify(graph_data), 200
    
    @api.route("/graph/extract", methods=["POST"])
    def extract_graph_nodes_and_relations():
        """
        Extract a knowledge graph from the provided text.
        Expected JSON body: {
            "text": "The text to analyze"
        }
        """
        try:
            data = request.get_json()
            if not data or "text" not in data:
                return jsonify({"error": "No text provided"}), 400
                
            text = data["text"]
            graph_data = graph_extractor.extract_graph_nodes_and_relations(text)
            
            return jsonify(graph_data), 200
            
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 500