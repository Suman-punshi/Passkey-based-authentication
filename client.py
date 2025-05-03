# import requests
# import base64
# import json
# import os    
# from Crypto_utils import decrypt_with_pr, generate_keyPair
# from encrypted_private_key import read_from_locked_zip, lock_modified_json

# SERVER_URL = "http://localhost:5000"
# KEY_FILE = "locked_private_key.zip"


# # === MAIN USER FLOW ===

# def run_user_flow():
#     full_name = input("Enter full name: ")
#     cms_id = input("Enter CMS ID: ")

#     # Step 1: Register (initiate challenge)
#     resp = requests.post(f"{SERVER_URL}/register", json={
#         "full_name": full_name,
#         "cms_id": cms_id
#     })
#     if resp.status_code != 200:
#         print(resp.json())
#         return

#     challenge_b64 = resp.json()["challenge"]
#     cipher = base64.b64decode(challenge_b64)
#     content = read_from_locked_zip(KEY_FILE)
#     private_key_b64 = content["private_key_nust"]
#     private_key = base64.b64decode(private_key_b64)
    
#     shared_secret = decrypt_with_pr(private_key, cipher)
    
#     # Step 3: Send decrypted shared secret to server
#     secret_b64 = base64.b64encode(shared_secret).decode()
#     verify_resp = requests.post(f"{SERVER_URL}/verify", json={
#         "cms_id": cms_id,
#         "decrypted_message": secret_b64
#     })
#     if verify_resp.status_code != 200:
#         print(verify_resp.json())
#         return

#     print("Identity verified!")

#     new_public, new_secret_key = generate_keyPair()

#     new_pub_b64 = base64.b64encode(new_public).decode()

#     finalize_resp = requests.post(f"{SERVER_URL}/finalize", json={
#         "cms_id": cms_id,
#         "full_name": full_name,
#         "public_key_webA": new_pub_b64
#     })

#     if finalize_resp.status_code == 200:
#         print("🎉 Registration complete.")

#         content["private_key_appA"] = base64.b64encode(new_secret_key).decode()
#         lock_modified_json(KEY_FILE, content)
#     else:
#         print(finalize_resp.json())

# if __name__ == "__main__":
#     run_user_flow()




import tkinter as tk
from tkinter import messagebox
import requests
import base64
from Crypto_utils import decrypt_with_pr, generate_keyPair
from encrypted_private_key import read_from_locked_zip, lock_modified_json

SERVER_URL = "http://localhost:5000"  # Your Flask backend
KEY_FILE = "locked_private_key.zip"

class PasskeyApp:
    def __init__(self, root):
        self.root = root
        root.title("Passkey Registration")

        # Input fields
        tk.Label(root, text="Full Name:").grid(row=0, column=0, padx=10, pady=5)
        self.full_name_entry = tk.Entry(root)
        self.full_name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(root, text="CMS ID:").grid(row=1, column=0, padx=10, pady=5)
        self.cms_id_entry = tk.Entry(root)
        self.cms_id_entry.grid(row=1, column=1, padx=10, pady=5)

        # Buttons
        tk.Button(root, text="Register", command=self.register).grid(row=2, column=0, columnspan=2, pady=10)

    def register(self):
        full_name = self.full_name_entry.get()
        cms_id = self.cms_id_entry.get()
        print("9")

        try:
            # Step 1: Get challenge from Flask backend
            response = requests.post(
                f"{SERVER_URL}/register",
                json={"full_name": full_name, "cms_id": cms_id}
            )
            if response.status_code != 200:
                messagebox.showerror("Error", response.json().get("message", "Registration failed"))
                return

            print("10")
            # Step 2: Decrypt challenge locally
            challenge_b64 = response.json()["challenge"]
            cipher = base64.b64decode(challenge_b64)
            content = read_from_locked_zip(KEY_FILE)
            private_key = base64.b64decode(content["private_key_nust"])
            shared_secret = decrypt_with_pr(private_key, cipher)

            print("11")
            # Step 3: Verify with backend
            secret_b64 = base64.b64encode(shared_secret).decode()
            verify_response = requests.post(
                f"{SERVER_URL}/verify",
                json={"cms_id": cms_id, "decrypted_message": secret_b64}
            )
            if verify_response.status_code != 200:
                messagebox.showerror("Error", verify_response.json().get("message", "Verification failed"))
                return

            # Step 4: Generate new keys and finalize
            new_public, new_private = generate_keyPair()
            new_pub_b64 = base64.b64encode(new_public).decode()

            print("12")
            finalize_response = requests.post(
                f"{SERVER_URL}/finalize",
                json={"cms_id": cms_id, "full_name": full_name, "new_public_key": new_pub_b64}
            )
            if finalize_response.status_code == 200:
                # Save new private key
                content["private_key_appA"] = base64.b64encode(new_private).decode()
                lock_modified_json(KEY_FILE, content)
                print("13")
                messagebox.showinfo("Success", "🎉 Registration complete!")
            else:
                messagebox.showerror("Error", finalize_response.json().get("message", "Finalization failed"))

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasskeyApp(root)
    root.mainloop()