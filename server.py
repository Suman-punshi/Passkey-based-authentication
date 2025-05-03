from flask import Flask, request, jsonify
from flask_cors import CORS  # For cross-origin requests
import base64
import pymongo
from Crypto_utils import encrypt_with_pub

app = Flask(__name__)
CORS(app)  # Enable if Tkinter runs on a different port

# MongoDB Setup
connection_string = "mongodb+srv://suman:suman123@passkeycluster.xvjufnq.mongodb.net/?retryWrites=true&w=majority&appName=PasskeyCluster"
client = pymongo.MongoClient(connection_string)
db_web = client["Passkey_web_data"]
db_nust = client["Passkeys_data"]
nust_collection = db_nust["Nust_database"]
registered_collection = db_web["web_database"]

# Temporary in-memory challenge store
server_nonce_store = {}

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    print("Got request: step 1 done")
    if not data or "full_name" not in data or "cms_id" not in data:
        return jsonify({"status": "error", "message": "Missing full_name or cms_id"}), 400

    full_name = data["full_name"]
    cms_id = data["cms_id"]
    print("extracted info: step 2 done")

    user = nust_collection.find_one({"full_name": full_name, "cms_id": cms_id})
    print("user present in nust database:step 3 done")
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    try:
        public_key = base64.b64decode(user["public_key"])
        cipher, secret = encrypt_with_pub(public_key)
        cipher_b64 = base64.b64encode(cipher).decode()
        print("verification challenge sent: step 4 done")
        server_nonce_store[cms_id] = {"shared_secret": secret}

        return jsonify({
            "status": "ok",
            "cms_id": cms_id,
            "challenge": cipher_b64
        })

    except Exception as e:
        print("error occured here: 1")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/verify", methods=["POST"])
def verify_identity():
    data = request.get_json()
    if not data or "cms_id" not in data or "decrypted_message" not in data:
        return jsonify({"status": "error", "message": "Missing cms_id or decrypted_message"}), 400

    print("got request: step 5")
    cms_id = data["cms_id"]
    decrypted_message_b64 = data["decrypted_message"]

    if cms_id not in server_nonce_store:
        return jsonify({"status": "error", "message": "No challenge issued for this CMS"}), 400

    print("step 5")
    try:
        received_secret = base64.b64decode(decrypted_message_b64)
        expected_secret = server_nonce_store[cms_id]["shared_secret"]

        if received_secret != expected_secret:
            return jsonify({"status": "error", "message": "Identity verification failed"}), 401

        del server_nonce_store[cms_id]
        return jsonify({"status": "verified", "message": "Identity confirmed. Send new public key."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/finalize", methods=["POST"])
def finalize_registration():
    data = request.get_json()
    if not data or "cms_id" not in data or "full_name" not in data or "new_public_key" not in data or "platform" not in data:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    print("step 6")
    try:
        # Check if user already exists
        existing_user = registered_collection.find_one({"cms_id": data["cms_id"]})

        if existing_user:
            # If user exists, update their platform list if needed
            current_platforms = existing_user.get("platforms", [])
            if data["platform"] not in current_platforms:
                registered_collection.update_one(
                    {"cms_id": data["cms_id"]},
                    {"$addToSet": {"platforms": data["platform"]}}
                )
            return jsonify({
                "status": "already_registered",
                "message": f"User already registered. Platform '{data['platform']}' added if not present."
            })

        # If new user, insert all details
        registered_collection.insert_one({
            "full_name": data["full_name"],
            "cms_id": data["cms_id"],
            "public_key": data["new_public_key"],
            "platforms": [data["platform"]]
        })

        return jsonify({"status": "success", "message": "Registration complete."})

    except Exception as e:
        print("8")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)