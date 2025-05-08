from flask import Flask, request, jsonify
from flask_cors import CORS  # For cross-origin requests
import base64
import pymongo
from Crypto_utils import encrypt_with_pub, unsign
import time
import os
import hmac
import hashlib
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
CORS(app)  # Enable if Tkinter runs on a different port

# Initialize Limiter for rate limiting
limiter = Limiter(get_remote_address, app=app)

#configs
app.config['JWT_SECRET_KEY'] = 'your-ultra-secure-secret'  
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_EXPIRATION'] = timedelta(hours=1)  # Token expires in 1 hour

# MongoDB Setup
connection_string = "mongodb+srv://suman:suman123@passkeycluster.xvjufnq.mongodb.net/?retryWrites=true&w=majority&appName=PasskeyCluster"
client = pymongo.MongoClient(connection_string)
db_web = client["Passkey_web_data"]
db_nust = client["Passkeys_data"]
nust_collection = db_nust["Nust_database"]
registered_collection = db_web["web_database"]
SERVER_SECRET = b"your-strong-secret-key-here" 


# Temporary in-memory challenge store
server_nonce_store = {}
server_nonce_store_login = {}

@app.route("/register", methods=["POST"])
@limiter.limit("5 per minute")  # Allow a maximum of 5 requests per minute per client IP
def register():
    data = request.get_json()
    if not data or "full_name" not in data or "cms_id" not in data:
        return jsonify({"status": "error", "message": "Missing full_name or cms_id"}), 400

    full_name = data["full_name"]
    cms_id = data["cms_id"] 

    user = nust_collection.find_one({"full_name": full_name, "cms_id": cms_id})
    
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    try:
        public_key = base64.b64decode(user["public_key"])
        cipher, secret = encrypt_with_pub(public_key)
        cipher_b64 = base64.b64encode(cipher).decode()
        
        server_nonce_store[cms_id] = {
            "shared_secret": secret,
            "timestamp": time.time()
        }

        return jsonify({
            "status": "ok",
            "cms_id": cms_id,
            "challenge": cipher_b64
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

@app.route("/verify", methods=["POST"])
@limiter.limit("5 per minute")  # Keep your rate limiting
def verify_identity():
    data = request.get_json()
    if not data or "cms_id" not in data or "decrypted_message" not in data:
        return jsonify({"status": "error", "message": "Missing cms_id or decrypted_message"}), 400

    cms_id = data["cms_id"]
    entry = server_nonce_store.get(cms_id)
    
    # Existing checks
    if not entry:
        return jsonify({"status": "error", "message": "No challenge issued for this CMS"}), 400

    # Keep your 60-second expiration
    if time.time() - entry["timestamp"] > 60:
        del server_nonce_store[cms_id]
        return jsonify({"status": "error", "message": "Challenge expired"}), 403

    try:
        received_secret = base64.b64decode(data["decrypted_message"])
        if received_secret != entry["shared_secret"]:
            return jsonify({"status": "error", "message": "Identity verification failed"}), 401

        # Generate and store verification token
        session_token = hmac.new(
        SERVER_SECRET,
        msg=f"{cms_id}:{entry['shared_secret']}".encode(),
        digestmod=hashlib.sha256
        ).hexdigest()
        server_nonce_store[cms_id]["session_token"] = session_token
        return jsonify({
            "status": "verified",
            "message": "Identity confirmed. Send new public key."
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/finalize", methods=["POST"])
def finalize_registration():
    data = request.get_json()
    if not data or "cms_id" not in data or "full_name" not in data or "new_public_key" not in data or "role" not in data:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    cms_id = data["cms_id"]
    entry = server_nonce_store.get(cms_id)

    # Server regenerates the expected token
    expected_token = hmac.new(
        SERVER_SECRET,
        msg=f"{cms_id}:{server_nonce_store[cms_id]['shared_secret']}".encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Cryptographic verification (no client-provided token)
    if not hmac.compare_digest(
        expected_token,
        server_nonce_store.get(cms_id, {}).get("session_token", "")
    ):
        return jsonify({"status": "error", "message": "Invalid session state"}), 401

    try:
        registered_collection.insert_one({
            "full_name": data["full_name"],
            "cms_id": data["cms_id"],
            "public_key": data["new_public_key"],
            "role": data["role"],
            "Jwt_token": False
        })
        
        # Cleanup - crucial to prevent token reuse
        del server_nonce_store[cms_id]


        
        return jsonify({"status": "success", "message": "Registration complete."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


    
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "full_name" not in data or "cms_id" not in data:
        return jsonify({"status": "error", "message": "Missing full_name or cms_id"}), 400

    user = registered_collection.find_one({"full_name": data["full_name"], "cms_id": data["cms_id"]})
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    try:
        public_key = base64.b64decode(user["public_key"])
        cipher, secret = encrypt_with_pub(public_key)
        cipher_b64 = base64.b64encode(cipher).decode()
        
        server_nonce_store_login[data["cms_id"]] = {
            "shared_message": secret,
            "role": data.get("role", "Student")
        }
        return jsonify({
            "status": "ok",
            "challenge": cipher_b64
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/verify_login", methods=["POST"])
def verify_login():
    data = request.get_json()
    if not data or "cms_id" not in data or "signature_message" not in data:
        return jsonify({"status": "error", "message": "Missing cms_id or decrypted_message"}), 400

    if data["cms_id"] not in server_nonce_store_login:
        return jsonify({"status": "error", "message": "No challenge issued for this CMS"}), 400
    try:
        user = registered_collection.find_one({"full_name": data["full_name"], "cms_id": data["cms_id"]})
        received_signature = base64.b64decode(data["signature_message"])
        expected_secret = server_nonce_store_login[data["cms_id"]]["shared_message"]
        
        
        if received_signature != expected_secret:
            return jsonify({"status": "error", "message": "Login verification failed"}), 401
        

        role = server_nonce_store_login[data["cms_id"]].get("role", "Student")
        token = jwt.encode({
        'cms_id': user["cms_id"],
        'name': user['full_name'],
        'role': user["role"],
        'exp': datetime.now(timezone.utc) + app.config['JWT_EXPIRATION']
        }, app.config['JWT_SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])

        # Update a specific field in a document (column modification equivalent)
        result = registered_collection.update_one(
            {"full_name": data["full_name"], "cms_id": data["cms_id"], "role": data["role"]},  # Find the document you want to modify
            {'$set': {'Jwt_token': token}}  # Set the new value for the field
            )
        

        del server_nonce_store_login[data["cms_id"]]
        
        return jsonify({
        "status": "verified",
        "token": token,
        "user": {
            "cms" : user['cms_id'],
            "name": user['full_name'],
            "role": user["role"]
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

@app.route("/restore_session", methods=["POST"])
def verify_token():
    data = request.get_json()
    token = data["tok"]
    try:
        decoded_token = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=[app.config['JWT_ALGORITHM']])
        user = registered_collection.find_one({"full_name": decoded_token["name"], "cms_id": decoded_token["cms_id"], "role": decoded_token["role"]})
        if not user:
            return jsonify({'error': 'User not Found'}), 401
        # Convert 'exp' timestamp to datetime
        exp_datetime = datetime.fromtimestamp(decoded_token['exp'], tz=timezone.utc)

        # Compare properly
        if datetime.now(timezone.utc) > exp_datetime:
            return jsonify({'error': 'JWT token expired'}), 401
        # You can also check if token exists in DB if you're tracking it
        return jsonify({"status": "ok", "full_name": user["full_name"], "cms_id": user["cms_id"], "role": user["role"]}), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


@app.route("/logout", methods=["POST"])
def logout_user():
    data = request.get_json()
    print(data)
    data_reg = registered_collection.find_one({"full_name": data["name"], "cms_id": data["cms"], "role": data["role"]})
    print('data')
    print(data_reg)

    result = registered_collection.update_one(
            {"full_name": data["name"], "cms_id": data["cms"], "role": data["role"]},  # Find the document you want to modify
            {'$set': {'Jwt_token': False}}  # Set the new value for the field
            )
    if result.modified_count > 0:
        return jsonify({"success": True, "message": "User logged out"}), 200
    else:
        return jsonify({"success": False, "message": "Logout failed"}), 500
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)