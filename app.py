from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Sample in-memory data store
todos = []

@app.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify(todos)

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    todo = {
        'id': len(todos) + 1,
        'title': data['title'],
        'completed': False
    }
    todos.append(todo)
    return jsonify(todo), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = next((todo for todo in todos if todo['id'] == todo_id), None)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    
    data = request.get_json()
    if 'completed' in data:
        todo['completed'] = data['completed']
    if 'title' in data:
        todo['title'] = data['title']
    return jsonify(todo)

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todo = next((todo for todo in todos if todo['id'] == todo_id), None)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    
    todos = [t for t in todos if t['id'] != todo_id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
