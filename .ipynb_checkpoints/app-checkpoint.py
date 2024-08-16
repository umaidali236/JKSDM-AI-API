from flask import Flask, jsonify, request

# Create a Flask application instance
app = Flask(__name__)

# Define a route for the root URL
@app.route('/')
def home():
    return "<h2>Welcome to the Flask API!</h2>"

# Define a route for a simple API endpoint
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})

# Define a route that takes a parameter
@app.route('/api/greet', methods=['GET'])
def greet():
    name = request.args.get('name', 'Stranger')  # Get 'name' from query string or default to 'Stranger'
    return jsonify({"message": f"Hello, {name}!"})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
