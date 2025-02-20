# Simple Flask Todo API

This is a simple, open-source REST API built with Flask that provides basic CRUD operations for a todo list. It's designed to be easy to understand, modify, and deploy.

## Features

- RESTful API endpoints for todo items
- CORS enabled for cross-origin requests
- Simple in-memory data storage (can be easily modified to use a database)
- JSON response format

## API Endpoints

- `GET /api/todos` - Get all todos
- `POST /api/todos` - Create a new todo
- `PUT /api/todos/<id>` - Update a todo
- `DELETE /api/todos/<id>` - Delete a todo

## Setup

1. Clone the repository:

```bash
git clone <your-repo-url>
cd <repo-name>
```

2. Create a Conda environment:

```bash
conda create -n todo-api python=3.9
conda activate todo-api
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Development

To modify the API for your needs:

1. Add new routes in `app.py`
2. Modify the data model (currently using a simple list)
3. Add additional dependencies to `requirements.txt`

## Deployment

This API can be deployed to various platforms:
TBD

## Example Usage

```python
# Create a new todo
curl -X POST -H "Content-Type: application/json" -d '{"title":"Buy groceries"}' http://localhost:5000/api/todos

# Get all todos
curl http://localhost:5000/api/todos

# Update a todo
curl -X PUT -H "Content-Type: application/json" -d '{"completed":true}' http://localhost:5000/api/todos/1

# Delete a todo
curl -X DELETE http://localhost:5000/api/todos/1
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
