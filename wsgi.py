from flask import Flask
from flask.py import app  # Import the Flask app from your main file (replace 'your_flask_file' with your actual file name)

# Gunicorn will use this app instance to start the server
if __name__ == "__main__":
    app.run(debug=True)  # For local development only
