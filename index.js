const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();
const port = process.env.PORT || 10000;

app.use(cors());  // Enable CORS
app.use(bodyParser.json());

// In-memory database
let users = {
  "owner": { "password": "ownerpass", "role": "owner", "balance": 1000 }  // Example balance for owner
};
let sellers = {};

// Helper: Validate authentication
function authenticate(username, password) {
  const user = users[username];
  if (user && user.password === password) {
    return user.role;
  }
  return null;
}

// Helper: Add new seller
function addSeller(name, balance) {
  if (sellers[name]) {
    return { success: false, message: "Seller already exists" };
  }
  sellers[name] = { balance, keys: [] };
  return { success: true, message: "Seller added successfully" };
}

// Route: Login
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  const role = authenticate(username, password);

  if (role) {
    return res.json({
      success: true,
      role,
      user: { 
        username,
        balance: users[username].balance,  // Include the user's balance
        role 
      }
    });
  }
  return res.status(401).json({ success: false, message: "Invalid credentials" });
});

// Route: Add seller (Owner only)
app.post('/api/add_seller', (req, res) => {
  const { username, password, seller_name, initial_balance } = req.body;

  if (authenticate(username, password) !== "owner") {
    return res.status(403).json({ success: false, message: "Unauthorized" });
  }

  const result = addSeller(seller_name, initial_balance);
  return res.json(result);
});

// Route: Generate Key (Owner only)
app.post('/api/generate_key', (req, res) => {
  const { username, password, seller_name, key_cost, duration } = req.body;

  if (authenticate(username, password) !== "owner") {
    return res.status(403).json({ success: false, message: "Unauthorized" });
  }

  const seller = sellers[seller_name];
  if (!seller) {
    return res.status(404).json({ success: false, message: "Seller not found" });
  }

  if (seller.balance < key_cost) {
    return res.status(400).json({ success: false, message: "Insufficient balance" });
  }

  // Generate key and deduct balance
  const generatedKey = `KEY-${new Date().toISOString().slice(11, 19).replace(/:/g, '')}-${seller_name.slice(0, 3).toUpperCase()}`;
  const expirationTime = new Date(Date.now() + duration * 60000);
  seller.keys.push({ key: generatedKey, expires_at: expirationTime });
  seller.balance -= key_cost;

  return res.json({
    success: true,
    key: generatedKey,
    expires_at: expirationTime.toISOString(),
  });
});

// Route: Validate Key
app.post('/api/validate_key', (req, res) => {
  const { key } = req.body;

  for (const seller_name in sellers) {
    const seller = sellers[seller_name];
    const keyData = seller.keys.find(k => k.key === key);

    if (keyData) {
      if (new Date() < new Date(keyData.expires_at)) {
        return res.json({ success: true, message: "Key is valid" });
      } else {
        return res.json({ success: false, message: "Key has expired" });
      }
    }
  }

  return res.status(404).json({ success: false, message: "Key not found" });
});

// Route: Get Seller Details (Owner only)
app.post('/api/seller_details', (req, res) => {
  const { username, password } = req.body;

  if (authenticate(username, password) !== "owner") {
    return res.status(403).json({ success: false, message: "Unauthorized" });
  }

  return res.json({ success: true, sellers });
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
