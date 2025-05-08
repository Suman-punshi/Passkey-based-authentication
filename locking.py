from encrypted_private_key import lock_json_with_password

# Example usage
json_file_path = "dr_madiha_khalid_private_key.json"
zip_file_path = "locked_private_key.zip"
target_file = "private_key.json"
password = "405943"  # This would be your PIN

lock_json_with_password(json_file_path, zip_file_path, password)