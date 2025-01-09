from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# In-memory database
users = {
    "owner": {"password": generate_password_hash("ownerpass"), "role": "owner"},
}
sellers = {}

# Helper: Validate authentication
def authenticate(username, password):
    user = users.get(username)
    if user and check_password_hash(user["password"], password):
        return user["role"]
    return None

# Helper: Add new seller
def add_seller(name, balance):
    if name in sellers:
        return False, "Seller already exists"
    sellers[name] = {"balance": balance, "keys": []}
    return True, "Seller added successfully"

# Route: Home (Root Route)
@app.route('/')
def home():
    return "Flask API is running!"

# Route: Login
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = authenticate(username, password)
    if role:
        return jsonify({"success": True, "role": role})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# Route: Add seller (Owner only)
@app.route("/api/add_seller", methods=["POST"])
def add_seller_route():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    seller_name = data.get("seller_name")
    initial_balance = data.get("initial_balance")

    if authenticate(username, password) != "owner":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    success, message = add_seller(seller_name, initial_balance)
    return jsonify({"success": success, "message": message})

# Route: Generate Key
@app.route("/api/generate_key", methods=["POST"])
def generate_key():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    seller_name = data.get("seller_name")
    key_cost = data.get("key_cost")
    duration = data.get("duration")

    if authenticate(username, password) != "owner":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    seller = sellers.get(seller_name)
    if not seller:
        return jsonify({"success": False, "message": "Seller not found"}), 404

    if seller["balance"] < key_cost:
        return jsonify({"success": False, "message": "Insufficient balance"}), 400

    # Generate key and deduct balance
    generated_key = f"KEY-{datetime.now().strftime('%H%M%S')}-{seller_name[:3].upper()}"
    expiration_time = datetime.now() + timedelta(minutes=duration)
    seller["keys"].append({"key": generated_key, "expires_at": expiration_time})
    seller["balance"] -= key_cost

    return jsonify({
        "success": True,
        "key": generated_key,
        "expires_at": expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
    })

# Route: Validate Key
@app.route("/api/validate_key", methods=["POST"])
def validate_key():
    data = request.json
    key = data.get("key")
    for seller_name, seller_data in sellers.items():
        for key_data in seller_data["keys"]:
            if key_data["key"] == key:
                if datetime.now() < key_data["expires_at"]:
                    return jsonify({"success": True, "message": "Key is valid"})
                return jsonify({"success": False, "message": "Key has expired"})
    return jsonify({"success": False, "message": "Key not found"}), 404

# Route: Get Seller Details (Owner only)
@app.route("/api/seller_details", methods=["POST"])
def seller_details():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if authenticate(username, password) != "owner":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    return jsonify({"success": True, "sellers": sellers})

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
