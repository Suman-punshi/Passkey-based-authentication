from flask import Flask, request, jsonify
from pymongo import MongoClient
import jwt
from datetime import datetime, timezone

app = Flask(__name__)


# MongoDB Setup
connection_string = "mongodb+srv://suman:suman123@passkeycluster.xvjufnq.mongodb.net/?retryWrites=true&w=majority&appName=PasskeyCluster"
client = MongoClient(connection_string)
IdP_database = client["Passkey_web_data"]
IdP_collection = IdP_database["web_database"]
App_database = client["passkey_web_data2"]
App_collection = App_database["passkey_web_database2"]

SERVER_SECRET = b"your-strong-secret-key-here" 


# JWT Secret Key
JWT_SECRET_KEY = "your-ultra-secure-secret"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 3600  # 1 hour expiration

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    token = data["JWT"]
    # Validate JWT token
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        idp_user = IdP_collection.find_one({'cms_id': decoded_token["cms_id"], 'full_name': decoded_token["name"], 'role': decoded_token["role"]})
        print("Decoded token role:", decoded_token['role'])
        if not idp_user:
            return jsonify({'error': 'User not found in IdP'}), 404
        if token != idp_user["Jwt_token"]:
            return jsonify({'error': 'Wrong JWT token'}), 401
        # Convert 'exp' timestamp to datetime
        exp_datetime = datetime.fromtimestamp(decoded_token['exp'], tz=timezone.utc)
        # Compare properly
        if datetime.now(timezone.utc) > exp_datetime:
            return jsonify({'error': 'JWT token expired'}), 401
        # Check if the user exists in service provider DB
        service_user = App_collection.find_one({'cms_id': idp_user['cms_id']})
        if service_user:
            return jsonify({'message': 'User logged in', 'name': service_user['name'],'role': service_user['role'],'cms_id': service_user['cms_id']}), 200
        else:
            # Register user if not found
            new_user = {
                'name': idp_user['full_name'],
                'cms_id': idp_user['cms_id'],
                'role': idp_user['role']  # Default role is 'Student'
            }
            print("roleeeeeee", idp_user['role'])
            App_collection.insert_one(new_user)
            return jsonify({'message': 'User registered and logged in', 'name': idp_user['full_name'], 'cms_id': idp_user['cms_id'], 'role' : idp_user['role']}), 201
    
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'JWT token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Run the server