import tkinter as tk
from tkinter import messagebox
import requests
import base64
from Crypto_utils import decrypt_with_pr, generate_keyPair, sign  # Assuming these are needed later
from encrypted_private_key import read_from_locked_zip, lock_modified_json  # Assuming these are needed later
from tkinter import ttk  # For Combobox (dropdown)
import jwt
from datetime import datetime, timezone, timedelta

SERVER_URL = "http://localhost:5000"
KEY_FILE = "locked_private_key.zip"

class PasskeyApp:
    def __init__(self, root):
        self.current_user = None
        self.auth_token = None
        self.root = root
        root.title("Welcome to Central identity provider: IdP")
        

        # Configure window to full screen
        root.attributes('-fullscreen', True)
        root.configure(bg='#f0f0f0')  # Light gray background
        # Local Fonts (check if these are available on your system)
        self.title_font = ('Noto Serif', 26, 'bold')
        self.header_font = ('Open Sans', 18, 'semibold')
        self.body_font = ('Lato', 14)
        self.accent_color_faculty = '#e07a5f'  # Burnt orange for Faculty
        self.accent_color_student = '#81b29a'  # Sage green for Student
        self.text_color = '#3d405b'  # Dark grayish blue
        self.card_bg = '#f9f5e7'    # Off-white card background
        # Custom fonts and colors
        title_font = ('Helvetica', 24, 'bold')
        label_font = ('Arial', 14)
        entry_font = ('Arial', 12)
        button_font = ('Helvetica', 16, 'bold')
        primary_color = '#4CAF50'  # Green
        secondary_color = '#e0f2f7' # Light blue/teal
        text_color = '#333333'      # Dark gray

        # Main container frame to center content
        self.center_frame = tk.Frame(root, bg='#f0f0f0')
        self.center_frame.pack(expand=True)

        # Title Label
        title_label = tk.Label(self.center_frame, text="Passkey Authentication", font=title_font, bg='#f0f0f0', fg=primary_color)
        title_label.pack(pady=(50, 30))

        # Buttons Frame
        buttons_frame = tk.Frame(self.center_frame, bg='#f0f0f0')
        buttons_frame.pack(pady=20)

        # Register Button
        register_button = tk.Button(buttons_frame, text="Register", command=self.show_register_page, font=button_font, bg=primary_color, fg='white', padx=20, pady=10, relief='raised', borderwidth=3)
        register_button.pack(side=tk.LEFT, padx=10)

        # Sign In Button
        signin_button = tk.Button(buttons_frame, text="Sign In", command=self.show_signin_page, font=button_font, bg='#007bff', fg='white', padx=20, pady=10, relief='raised', borderwidth=3)
        signin_button.pack(side=tk.LEFT, padx=10)

        # Exit Button (for development/testing in full screen)
        exit_button = tk.Button(root, text="Exit Fullscreen", command=self.exit_fullscreen, font=('Arial', 10), bg='#cccccc', fg=text_color, padx=10, pady=5)
        exit_button.pack(side=tk.BOTTOM, pady=10)

        res, data = self.restore_session()
        if res and data:
            if data["role"] == "Faculty":
                self.show_faculty_page(data["full_name"], data["cms_id"])
            else:
                self.show_student_page(data["full_name"], data["cms_id"])
        else:
            self.show_initial_page()

    def clear_center_frame(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()

    def show_initial_page(self):
        self.clear_center_frame()

        # Title Label
        title_font = ('Helvetica', 24, 'bold')
        primary_color = '#4CAF50'
        title_label = tk.Label(self.center_frame, text="Passkey Authentication", font=title_font, bg='#f0f0f0', fg=primary_color)
        title_label.pack(pady=(50, 30))

        # Buttons Frame
        buttons_frame = tk.Frame(self.center_frame, bg='#f0f0f0')
        buttons_frame.pack(pady=20)

        # Register Button
        register_button = tk.Button(buttons_frame, text="Register", command=self.show_register_page, font=('Helvetica', 16, 'bold'), bg='#4CAF50', fg='white', padx=20, pady=10, relief='raised', borderwidth=3)
        register_button.pack(side=tk.LEFT, padx=10)

        # Sign In Button
        signin_button = tk.Button(buttons_frame, text="Sign In", command=self.show_signin_page, font=('Helvetica', 16, 'bold'), bg='#007bff', fg='white', padx=20, pady=10, relief='raised', borderwidth=3)
        signin_button.pack(side=tk.LEFT, padx=10)

    def show_register_page(self):
        self.clear_center_frame()
        title_font = ('Helvetica', 24, 'bold')
        label_font = ('Arial', 14)
        entry_font = ('Arial', 12)
        primary_color = '#4CAF50'
        secondary_color = '#e0f2f7'
        text_color = '#333333'
        button_font = ('Helvetica', 16, 'bold')

        title_label = tk.Label(self.center_frame, text="Register", font=title_font, bg='#f0f0f0', fg=primary_color)
        title_label.pack(pady=(50, 30))

        # Full Name Input
        full_name_frame = tk.Frame(self.center_frame, bg='#f0f0f0')
        full_name_frame.pack(pady=15)
        full_name_label = tk.Label(full_name_frame, text="Full Name:", font=label_font, bg='#f0f0f0', fg=text_color, width=10, anchor='w')
        full_name_label.pack(side=tk.LEFT, padx=10)
        self.register_full_name_entry = tk.Entry(full_name_frame, font=entry_font, bg=secondary_color, relief='flat', width=30)
        self.register_full_name_entry.pack(side=tk.LEFT, padx=10)

        # CMS ID Input
        cms_id_frame = tk.Frame(self.center_frame, bg='#f0f0f0')
        cms_id_frame.pack(pady=15)
        cms_id_label = tk.Label(cms_id_frame, text="CMS ID:", font=label_font, bg='#f0f0f0', fg=text_color, width=10, anchor='w')
        cms_id_label.pack(side=tk.LEFT, padx=10)
        self.register_cms_id_entry = tk.Entry(cms_id_frame, font=entry_font, bg=secondary_color, relief='flat', width=30)
        self.register_cms_id_entry.pack(side=tk.LEFT, padx=10)

        # Role Selection
        role_frame = tk.Frame(self.center_frame, bg='#f0f0f0')
        role_frame.pack(pady=15)
        role_label = tk.Label(role_frame, text="Role:", font=label_font, bg='#f0f0f0', fg=text_color, width=10, anchor='w')
        role_label.pack(side=tk.LEFT, padx=10)
        self.register_role_var = tk.StringVar(self.center_frame)
        self.register_role_var.set("Student")  # Default value
        role_choices = ["Student", "Faculty"]
        role_dropdown = ttk.Combobox(role_frame, textvariable=self.register_role_var, values=role_choices, font=entry_font, width=28)
        role_dropdown.pack(side=tk.LEFT, padx=10)

        # Register Button
        register_button = tk.Button(self.center_frame, text="Register", command=self.register_user, font=button_font, bg=primary_color, fg='white', padx=20, pady=10, relief='raised', borderwidth=3)
        register_button.pack(pady=20)

        # Go to Sign In Page Button
        LogIn_button = tk.Button(self.center_frame, text="Go to Sign In Page", command=self.show_signin_page, font=button_font, bg='#007bff', fg='white', padx=20, pady=10, relief='raised', borderwidth=3)
        LogIn_button.pack(pady=10)

    def show_signin_page(self):
        self.clear_center_frame()
        title_font = ('Helvetica', 24, 'bold')
        label_font = ('Arial', 14)
        entry_font = ('Arial', 12)
        primary_color = '#007bff'  # Blue for Sign In
        secondary_color = '#e3f2fd'
        text_color = '#333333'
        button_font = ('Helvetica', 16, 'bold')

        title_label = tk.Label(self.center_frame, text="Sign In", font=title_font, bg='#f0f0f0', fg=primary_color)
        title_label.pack(pady=(50, 30))

        # Name Input
        name_frame = tk.Frame(self.center_frame, bg='#f0f0f0')
        name_frame.pack(pady=15)
        name_label = tk.Label(name_frame, text="Name:", font=label_font, bg='#f0f0f0', fg=text_color, width=10, anchor='w')
        name_label.pack(side=tk.LEFT, padx=10)
        self.signin_name_entry = tk.Entry(name_frame, font=entry_font, bg=secondary_color, relief='flat', width=30)
        self.signin_name_entry.pack(side=tk.LEFT, padx=10)

        # CMS ID Input
        cms_id_frame = tk.Frame(self.center_frame, bg='#f0f0f0')
        cms_id_frame.pack(pady=15)
        cms_id_label = tk.Label(cms_id_frame, text="CMS ID:", font=label_font, bg='#f0f0f0', fg=text_color, width=10, anchor='w')
        cms_id_label.pack(side=tk.LEFT, padx=10)
        self.signin_cms_id_entry = tk.Entry(cms_id_frame, font=entry_font, bg=secondary_color, relief='flat', width=30)
        self.signin_cms_id_entry.pack(side=tk.LEFT, padx=10)

        # Role Selection
        role_frame = tk.Frame(self.center_frame, bg='#f0f0f0')
        role_frame.pack(pady=15)
        role_label = tk.Label(role_frame, text="Role:", font=label_font, bg='#f0f0f0', fg=text_color, width=10, anchor='w')
        role_label.pack(side=tk.LEFT, padx=10)
        self.signin_role_var = tk.StringVar(self.center_frame)
        self.signin_role_var.set("Student")  # Default value
        role_choices = ["Student", "Faculty"]
        role_dropdown = ttk.Combobox(role_frame, textvariable=self.signin_role_var, values=role_choices, font=entry_font, width=28)
        role_dropdown.pack(side=tk.LEFT, padx=10)

        # Login Button (will now trigger the page display based on role)
        login_button = tk.Button(
        self.center_frame, 
        text="Log In", 
        command=self.login_user,  # Changed from process_login_for_page
        font=button_font, 
        bg=primary_color, 
        fg='white', 
        padx=20, 
        pady=10, 
        relief='raised', 
        borderwidth=3)
        login_button.pack(pady=20)
        # Go to Registration Page Button
        register_button = tk.Button(self.center_frame, text="Go to Registration Page", command=self.show_register_page, font=button_font, bg='#4CAF50', fg='white', padx=20, pady=10, relief='raised', borderwidth=3)
        register_button.pack(pady=10)
    
    def process_login_for_page(self):
        name = self.signin_name_entry.get()
        cms_id = self.signin_cms_id_entry.get()
        role = self.signin_role_var.get()

        if role == "Faculty":
            self.show_faculty_page(name, cms_id)
        elif role == "Student":
            self.show_student_page(name, cms_id)
        else:
            messagebox.showerror("Error", "Invalid role selected.")
    
    def show_faculty_page(self, name, cms_id, role):
     self.clear_center_frame()

    # Colors and Fonts
     title_font = ('Helvetica', 26, 'bold')
     label_font = ('Open Sans', 16)
     info_font = ('Open Sans', 18, 'bold')
     card_bg = '#f9f5e7'
     text_color = '#333333'
     primary_color = '#FFC107'  # Amber for faculty
     welcome_font = ('Lato', 14, 'italic')

    # Title
     title_label = tk.Label(self.center_frame, text="Faculty Dashboard", font=title_font, bg='#f4f1de', fg=primary_color)
     title_label.pack(pady=(40, 10))

    # Info Card Frame
     info_frame = tk.Frame(self.center_frame, bg=card_bg, padx=40, pady=30, bd=2, relief='ridge')
     info_frame.pack(pady=20, padx=50, fill='x')

    # Dynamic Info
     tk.Label(info_frame, text=f"👤 Name: {name}", font=info_font, bg=card_bg, fg=text_color, anchor='w').pack(fill='x', pady=5)
     tk.Label(info_frame, text=f"🆔 CMS ID: {cms_id}", font=info_font, bg=card_bg, fg=text_color, anchor='w').pack(fill='x', pady=5)
     tk.Label(info_frame, text=f"🎓 Role: {role.title()}", font=info_font, bg=card_bg, fg=text_color, anchor='w').pack(fill='x', pady=5)

    # Friendly Welcome Message
     welcome_msg = "Welcome to your personalized faculty dashboard!\nHere you can access everything you need to manage your courses, students, and research."
     tk.Label(self.center_frame, text=welcome_msg, font=welcome_font, bg='#f4f1de', fg='#555555', justify='center').pack(pady=(10, 30))

    # Button Frame (Back + Logout)
     button_frame = tk.Frame(self.center_frame, bg='#f4f1de')
     button_frame.pack(pady=20)

     back_button = tk.Button(
        button_frame,
        text="← Back to Sign In",
        command=self.show_signin_page,
        font=('Lato', 12, 'bold'),
        bg='#d62839',
        fg='white',
        padx=20,
        pady=10,
        relief='raised',
        bd=2
    )
     back_button.grid(row=0, column=0, padx=10)

     logout_button = tk.Button(
        button_frame,
        text="Logout",
        command=self.logout,
        font=('Lato', 12, 'bold'),
        bg='#ff4444',
        fg='white',
        padx=20,
        pady=10,
        relief='raised',
        bd=2
    )
     logout_button.grid(row=0, column=1, padx=10)


    def show_student_page(self, name, cms_id):
     self.clear_center_frame()
    
     title_font = ('Helvetica', 26, 'bold')
     label_font = ('Arial', 16)
     text_color = '#333333'
     primary_color = '#28A745'  # Green for Student
     card_bg = '#f0f7f4'
     border_color = '#cce5cc'

    # Title
     title_label = tk.Label(
    self.center_frame,
        text="🎓 Welcome to Your Student Dashboard",
        font=title_font,
        bg='#e8f5e9',
        fg=primary_color
    )
     title_label.pack(pady=(50, 20))

    # Info Card
     info_frame = tk.Frame(self.center_frame, bg=card_bg, padx=30, pady=20, bd=2, relief='groove', highlightbackground=border_color, highlightthickness=2)
     info_frame.pack(pady=20, padx=60, fill='x')

     tk.Label(info_frame, text=f"👤 Name: {name}", font=label_font, bg=card_bg, fg=text_color, anchor='w').pack(fill='x', pady=5)
     tk.Label(info_frame, text=f"🆔 CMS ID: {cms_id}", font=label_font, bg=card_bg, fg=text_color, anchor='w').pack(fill='x', pady=5)

    # Message Frame
     message_frame = tk.Frame(self.center_frame, bg='#ffffff', padx=30, pady=25, bd=2, relief='ridge')
     message_frame.pack(pady=20, padx=60, fill='x')

     message = (
        "Hi there! 👋\n\n"
        "We're glad to have you here. Explore your dashboard to manage courses, track assignments, "
        "and stay updated with your academic journey.\n\n"
        "Wishing you a productive and successful semester ahead!"
    )
     tk.Label(message_frame, text=message, font=('Lato', 14), bg='#ffffff', fg=text_color, justify='left', anchor='w', wraplength=500).pack()

    # Buttons
     btn_frame = tk.Frame(self.center_frame, bg='#f4f1de')
     btn_frame.pack(pady=30)

     back_button = tk.Button(
        btn_frame,
        text="Back",
        command=self.show_signin_page,
        font=('Lato', 12, 'bold'),
        bg='#d62839',
        fg='white',
        padx=20,
        pady=10
    )
     back_button.grid(row=0, column=0, padx=10)

     logout_button = tk.Button(
        btn_frame,
        text="Logout",
        command=self.logout,
        font=('Lato', 12, 'bold'),
        bg='#ff4444',
        fg='white',
        padx=20,
        pady=10
    )
     logout_button.grid(row=0, column=1, padx=10)

    
    def exit_fullscreen(self):
        self.root.attributes('-fullscreen', False)

    def register_user(self):
        full_name = self.register_full_name_entry.get()
        cms_id = self.register_cms_id_entry.get()
        role = self.register_role_var.get()
        print("Registering:", full_name, cms_id, role)
        # Implement your registration logic here, including sending the role to the backend
        try:
            # Step 1: Get challenge from Flask backend
            response = requests.post(
                f"{SERVER_URL}/register",
                json={"full_name": full_name, "cms_id": cms_id, "role": role} # Include role
            )
            if response.status_code != 200:
                messagebox.showerror("Error", response.json().get("message", "Registration failed"))
                return

            print("10")
            # Step 2: Decrypt challenge locally
            challenge_b64 = response.json()["challenge"]
            cipher = base64.b64decode(challenge_b64)
            content = read_from_locked_zip(KEY_FILE)
            private_key = base64.b64decode(content["private_key"])
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
                json={"cms_id": cms_id, "full_name": full_name, "new_public_key": new_pub_b64, "role": role} # Include role
            )
            if finalize_response.status_code == 200:
                # Save new private key
                content["private_key_appA"] = base64.b64encode(new_private).decode()
                lock_modified_json(KEY_FILE, content)
                print("13")
                messagebox.showinfo("Success", "🎉 Registration complete!")
                self.show_initial_page() # Go back to the initial page after registration
            else:
                messagebox.showerror("Error", finalize_response.json().get("message", "Finalization failed"))

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    
    def restore_session(self):
        try:
            print("i came here")
            with open("session.jwt", "r") as f:
                print("now i am here")
                token = f.read().strip()
            if not token:
                return False, False
            # Send token to server for verification
            response = requests.post(f"{SERVER_URL}/restore_session", json = {"tok": token})
            print("Yaar bas hogyi")
        
            if response.status_code == 200:
                data = response.json()
                if data["role"] == "Faculty":
                    print("yaar kahan ja kay maron")
                    self.show_faculty_page(data["full_name"], data["cms_id"])
                else:
                    print("yahan kyu nyi arha bhai")
                    self.show_student_page(data["full_name"], data["cms_id"])

                return True, data
            else:
                print("Token invalid")
                return False, False

        except FileNotFoundError:
            print("khuda ka wasta chal ja bhai")
            return False, False




    def login_user(self):
        name = self.signin_name_entry.get()
        cms_id = self.signin_cms_id_entry.get()
        role = self.signin_role_var.get()
    
        print("login 1")
        if not name or not cms_id:
            messagebox.showerror("Error", "Name and CMS ID are required")
            return

        try:
            # Step 1: Request login challenge from server
            response = requests.post(
                f"{SERVER_URL}/login",
                json={"full_name": name, "cms_id": cms_id, "role": role}
            )
            print("login 2")
        
            if response.status_code != 200:
                messagebox.showerror("Error", response.json().get("message", "Login failed"))
                return

            print("login 3")
            # Step 2: Decrypt challenge with private key from locked file
            challenge_b64 = response.json()["challenge"]
            challenge = base64.b64decode(challenge_b64)

            print("login 4")
            # Access locked private key
            content = read_from_locked_zip(KEY_FILE)
            print("zindagi azaab")
            private_key_b64 = content["private_key_appA"]  # Or "private_key_appA" if using new key
            print("login: i am gonna die")
            private_key = base64.b64decode(private_key_b64)
        

            print("Challenge type:", type(challenge))
            print("Challenge length:", len(challenge))
            print("private key type:", type(private_key))
            print("private key length:", len(private_key))
            print("login 5")
            # Decrypt the challenge
            #signature = sign(private_key, challenge)
            shared_secret = decrypt_with_pr(private_key, challenge)
        

            print("login 6")
            # Step 3: Send decrypted response back to server
            signature_b64 = base64.b64encode(shared_secret).decode()
            verify_response = requests.post(
                f"{SERVER_URL}/verify_login",
                json={
                "full_name": name,
                "cms_id": cms_id,
                "signature_message": signature_b64,
                "role": role
                }
            )
        
            print("login 7")
            if verify_response.status_code != 200:
                messagebox.showerror("Error", verify_response.json().get("message", "Login verification failed"))
                return
            
            data = verify_response.json()
            self.auth_token = data['token']
            with open("session.jwt", "w") as f:
                f.write(self.auth_token)
            self.current_user = data['user']
            print(self.current_user)
            
            print("login 8")

            # Step 4: Successful login - show appropriate dashboard
            messagebox.showinfo("Success", "Login successful!")
            if role == "Faculty":
                self.show_faculty_page(name, cms_id)
            else:
                self.show_student_page(name, cms_id)

        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")


    def logout(self):
        response = requests.post(
                f"{SERVER_URL}/logout",
                json = self.current_user
            )
        with open("session.jwt", "w") as f:
            f.write("")  # This clears the file
        self.current_user = None
        self.auth_token = None
        print("i am here")
        self.show_initial_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasskeyApp(root)
    root.mainloop()