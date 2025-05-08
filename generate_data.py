import base64
import pymongo
import os
import json
from Crypto_utils import generate_keyPair

# Define NUST members and CMS IDs
members_info = [
    
    ("Dr. Madiha Khalid", "123456", "faculty")
]

def generate_nust_members():
    db_entries = []
    suman_private_key = None  # store your private key temporarily

    for full_name, cms_id, role in members_info:
        public_key, private_key = generate_keyPair()

        # Base64-encode for storage
        pub_b64 = base64.b64encode(public_key).decode('utf-8')
        priv_b64 = base64.b64encode(private_key).decode('utf-8')

        # Prepare database entry
        member_record = {
            "full_name": full_name,
            "cms_id": cms_id,
            "role": role,
            "public_key": pub_b64
        }
        db_entries.append(member_record)

        # Store only Suman Kumari's private key locally
        if full_name.lower() == "dr. madiha khalid":
            suman_private_key = {
                "cms_id": cms_id,
                "private_key": priv_b64
            }

    return db_entries, suman_private_key

# Insert into MongoDB (public data only)
connection_string = "mongodb+srv://suman:suman123@passkeycluster.xvjufnq.mongodb.net/?retryWrites=true&w=majority&appName=PasskeyCluster"
client = pymongo.MongoClient(connection_string)
db = client["Passkeys_data"]
collection = db["Nust_database"]

members, suman_key = generate_nust_members()
collection.insert_many(members)
print(f"Inserted {len(members)} NUST members (public keys only) into database.")

# Save only Suman's private key to a local file
if suman_key:
    json_filename = "dr_madiha_khalid_private_key.json"
    with open(json_filename, "w") as f:
        json.dump(suman_key, f, indent=4)
    print(f"[+] Saved *your* private key locally to: {json_filename}")

client.close()