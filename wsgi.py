from flask import Flask
from flask import jsonify
from flask import request

# Import the Flask app from flask.py (or whatever your main file is named)
from flask import app

# Gunicorn will use this app instance to start the server
if __name__ == "__main__":
    app.run(debug=True)
