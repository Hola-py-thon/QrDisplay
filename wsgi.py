from flask import app  # Import the Flask app object

# Gunicorn will use this app instance to start the server
if __name__ == "__main__":
    app.run(debug=True)  # Only for local development, Gunicorn will handle it in production
