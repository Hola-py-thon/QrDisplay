import os
from flask import Flask

app = Flask(__name__)

# The app should listen on the port specified by the environment variable
port = int(os.environ.get("PORT", 5000))  # Default to 5000 if not set

if __name__ == "__main__":
    # Make sure the app listens on the right port
    app.run(host="0.0.0.0", port=port)
