import pyzipper
import json
import tkinter as tk
from tkinter import simpledialog

def lock_json_with_password(json_file_path, zip_file_path, password):
    # Open the zip file for writing with encryption
    with pyzipper.AESZipFile(zip_file_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zipf:
        zipf.setpassword(password.encode())  # Set password for the zip file
        zipf.write(json_file_path, arcname="private_key.json")  # Add the JSON file to the zip

    print(f"File {json_file_path} locked and saved as {zip_file_path}.")


def read_from_locked_zip(zip_file_path, target_file="private_key.json"):
    root = tk.Tk()
    root.withdraw()
    
    pin = None
    
    def on_submit():
        nonlocal pin
        pin = entry.get()
        popup.destroy()
    
    popup = tk.Toplevel(root)
    popup.title("Unlock Private Key")
    
    tk.Label(popup, text="Enter your PIN:").pack(padx=20, pady=5)
    entry = tk.Entry(popup, show="*")
    entry.pack(padx=20, pady=5)
    
    tk.Button(popup, text="Unlock", command=on_submit).pack(pady=10)
    
    popup.wait_window()
    
    if not pin:
        raise ValueError("PIN required")
    
    try:
        with pyzipper.AESZipFile(zip_file_path, 'r') as zipf:
            zipf.setpassword(pin.encode())
            with zipf.open(target_file) as file:
                return json.load(file)
    finally:
        root.destroy()



def lock_modified_json(zip_file_path, json_content, target_file="private_key.json"):
    # Create a hidden root window (required for Tkinter dialogs)
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Show PIN dialog
    pin = simpledialog.askstring(
        title="PIN Required",
        prompt="Enter your PIN:",
        show='*'  # Mask input with *
    )

    if not pin:  # User clicked Cancel or closed the dialog
        raise ValueError("PIN entry cancelled")

    # Debug: Show what you're saving
    print("🔐 Saving updated JSON content:")
    print(f"➡ Writing to file '{target_file}' inside ZIP: {zip_file_path}")

    # Proceed with ZIP encryption
    with pyzipper.AESZipFile(
        zip_file_path,
        'w',
        compression=pyzipper.ZIP_DEFLATED,
        encryption=pyzipper.WZ_AES
    ) as zipf:
        zipf.setpassword(pin.encode())
        with zipf.open(target_file, 'w') as file:
            file.write(json.dumps(json_content).encode('utf-8'))

    # Debug: Confirm file contents in ZIP
    with pyzipper.AESZipFile(zip_file_path, 'r') as zipf:
        zipf.setpassword(pin.encode())
        print("ZIP now contains:", zipf.namelist())

    root.destroy()



# Example usage
json_file_path = "arham_haroon_private_key.json"
zip_file_path = "locked_private_key.zip"
target_file = "private_key.json"
password = "405943"  # This would be your PIN