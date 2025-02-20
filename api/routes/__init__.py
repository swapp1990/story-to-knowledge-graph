from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api/v1')

def init_routes(api, graph_extractor):
	from .graph_routes import register_routes
	register_routes(api, graph_extractor)
