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

import tkinter as tk
import random

class AnimatedBackground:
    def __init__(self, canvas, colors):
        self.canvas = canvas
        self.colors = colors
        self.shapes = []
        self.max_shapes = 35
        self.emojis = {'lock': "🔒", 'shield': "🛡️", 'key': "🔑"}
        self.canvas.after(200, self.setup)  # Slight delay to ensure canvas is ready

    def setup(self):
        # Ensure canvas dimensions are available
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            self.canvas.after(100, self.setup)  # Retry after a short delay
            return

        self.create_shapes(width, height)
        self.animate()

    def create_shapes(self, width, height):
        for _ in range(self.max_shapes):
            emoji = random.choice(list(self.emojis.values()))
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(20, 40)
            color = random.choice(self.colors)
            dx = random.uniform(-0.7, 0.7)
            dy = random.uniform(-0.7, 0.7)

            # Avoid zero speed
            if dx == 0: dx = 0.5
            if dy == 0: dy = 0.5

            text_id = self.canvas.create_text(x, y, text=emoji, font=("Arial", size), fill=color)
            self.shapes.append((text_id, dx, dy))

    def animate(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        for i, (text_id, dx, dy) in enumerate(self.shapes):
            self.canvas.move(text_id, dx, dy)
            coords = self.canvas.bbox(text_id)

            if coords:
                x1, y1, x2, y2 = coords
                # Bounce off the walls
                if x1 <= 0 or x2 >= width:
                    dx = -dx
                if y1 <= 0 or y2 >= height:
                    dy = -dy
                self.shapes[i] = (text_id, dx, dy)

        self.canvas.after(30, self.animate)


import tkinter as tk

class PasskeyApp:
    def __init__(self, root):
        self.current_user = None
        self.auth_token = None
        self.root = root
        root.title("Welcome to Central identity provider: IdP")
        root.configure(bg='#1e1e2f')

        # Fullscreen and responsive setup
        root.attributes('-fullscreen', True)
        root.bind("<Configure>", self.on_resize)  # Bind resize event

        # Fonts and Colors
        title_font = ('Helvetica', 24, 'bold')
        button_font = ('Helvetica', 16, 'bold')
        primary_color = '#4CAF50'

        self.bg_color = "#1e1e2f"
        self.text_color = "#f5f6fa"
        self.accent_color = "#6c5ce7"
        self.student_color = "#00cec9"
        self.faculty_color = "#ffeaa7"

        # Canvas
        self.canvas = tk.Canvas(root, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Content Frame on Canvas
        self.center_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.canvas_window = self.canvas.create_window(
            0, 0, window=self.center_frame, anchor="center"
        )

        # Animated Background Stub (you should define AnimatedBackground elsewhere)
        self.anim_bg = AnimatedBackground(self.canvas, [self.accent_color, self.student_color, self.faculty_color])

        # Title
        title_label = tk.Label(self.center_frame, text="Passkey Authentication", font=title_font,
                               bg='#f0f0f0', fg=primary_color)
        title_label.pack(pady=(50, 30))

        # Buttons
        buttons_frame = tk.Frame(self.center_frame, bg='#f0f0f0')
        buttons_frame.pack(pady=20)

        tk.Button(buttons_frame, text="Register", command=self.show_register_page, font=button_font,
                  bg=primary_color, fg='white', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

        tk.Button(buttons_frame, text="Sign In", command=self.show_signin_page, font=button_font,
                  bg='#007bff', fg='white', padx=20, pady=10).pack(side=tk.LEFT, padx=10)

        # Exit Fullscreen Button
        tk.Button(self.root, text="Exit Fullscreen", command=self.exit_fullscreen,
                  font=("Arial", 10), bg="#444", fg="white").place(relx=0.01, rely=0.95)

        # Restore session or show initial
        res, data = self.restore_session()
        if res and data:
            if data["role"] == "Faculty":
                self.show_faculty_page(data["full_name"], data["cms_id"], data["role"])
            else:
                self.show_student_page(data["full_name"], data["cms_id"],data["role"])
        else:
            self.show_initial_page()

    def on_resize(self, event):
        """Handles dynamic centering and resizing on root or canvas changes."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.coords(self.canvas_window, width // 2, height // 2)

    def clear_center_frame(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()
    def exit_fullscreen(self):
     self.root.attributes('-fullscreen', False)
     self.root.geometry("1024x600")  # Optional: set a default size
     self.root.update_idletasks()    # Force UI update
     self.on_resize(None)            # Manually trigger resize logic

    

    def show_initial_page(self):
        self.clear_center_frame()

        # Title Label
        title_font = ('Helvetica', 24, 'bold')
        primary_color = '#4CAF50'
        title_label = tk.Label(self.center_frame, text="Passkey Authentication", font=title_font, bg=self.bg_color, fg=primary_color)
        title_label.pack(pady=(50, 30))

        # Buttons Frame
        buttons_frame = tk.Frame(self.center_frame, bg=self.bg_color)
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

        title_label = tk.Label(self.center_frame, text="Register", font=title_font, bg=self.bg_color, fg=primary_color)
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

        title_label = tk.Label(self.center_frame, text="Sign In", font=title_font, bg=self.bg_color, fg=primary_color)
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
            self.show_faculty_page(name, cms_id,role)
        elif role == "Student":
            self.show_student_page(name, cms_id,role)
        else:
            messagebox.showerror("Error", "Invalid role selected.")
    
    def show_faculty_page(self, name, cms_id, role):
     self.clear_center_frame()

    # Colors and Fonts
     title_font = ('Helvetica', 26, 'bold')
     label_font = ('Open Sans', 16)
     info_font = ('Open Sans', 18, 'bold')
     card_bg = '#2c2c3e'
     text_color = '#f5f6fa'
     primary_color = '#FFC107'  # Amber for faculty
     welcome_font = ('Lato', 14, 'italic')
     bg_color = self.bg_color 

    # Title
     title_label = tk.Label(self.center_frame, text="Faculty Dashboard", font=title_font, bg=self.bg_color, fg=primary_color)
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
     tk.Label(self.center_frame, text=welcome_msg, font=welcome_font, bg=bg_color, fg="#f5f6fa", justify='center').pack(pady=(10, 30))

    # Button Frame (Back + Logout)
     button_frame = tk.Frame(self.center_frame, bg=bg_color)
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


    def show_student_page(self, name, cms_id,role):
     self.clear_center_frame()
    
     title_font = ('Helvetica', 26, 'bold')
     label_font = ('Arial', 16)
     text_color = '#f5f6fa'
     primary_color = '#28A745'  # Green for Student
     card_bg = '#2c2c3e'
     border_color = '#cce5cc'
     bg_color = self.bg_color 

    # Title
     title_label = tk.Label(
    self.center_frame,
        text="🎓 Welcome to Your Student Dashboard",
        font=title_font,
        bg=self.bg_color,
        fg=primary_color
    )
     title_label.pack(pady=(50, 20))

    # Info Card
     info_frame = tk.Frame(self.center_frame, bg=card_bg, padx=30, pady=20, bd=2, relief='groove', highlightbackground=border_color, highlightthickness=2)
     info_frame.pack(pady=20, padx=60, fill='x')

     tk.Label(info_frame, text=f"👤 Name: {name}", font=label_font, bg=card_bg, fg=text_color, anchor='w').pack(fill='x', pady=5)
     tk.Label(info_frame, text=f"🆔 CMS ID: {cms_id}", font=label_font, bg=card_bg, fg=text_color, anchor='w').pack(fill='x', pady=5)
     tk.Label(info_frame, text=f"🎓 Role: {role.title()}", font=label_font, bg=card_bg, fg=text_color, anchor='w').pack(fill='x', pady=5)

    # Message Frame
     message_frame = tk.Frame(self.center_frame, bg='#ffffff', padx=30, pady=25, bd=2, relief='ridge')
     message_frame.pack(pady=20, padx=60, fill='x')

     message = (
        "Hi there! 👋\n\n"
        "We're glad to have you here. Explore your dashboard to manage courses, track assignments, "
        "and stay updated with your academic journey.\n\n"
        "Wishing you a productive and successful semester ahead!"
    )
     tk.Label(message_frame, text=message, font=('Lato', 14), bg=bg_color, fg="#f5f6fa", justify='left', anchor='w', wraplength=500).pack()

    # Buttons
     btn_frame = tk.Frame(self.center_frame, bg=bg_color)
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
                    self.show_faculty_page(data["full_name"], data["cms_id"],data["role"])
                else:
                    print("yahan kyu nyi arha bhai")
                    self.show_student_page(data["full_name"], data["cms_id"],data["role"])

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
                self.show_faculty_page(name, cms_id,role)
            else:
                self.show_student_page(name, cms_id,role)

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