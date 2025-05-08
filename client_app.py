import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import threading
import time

SERVER_URL = "http://localhost:5000/login"

class ServiceProviderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Service Provider Login")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#f0f0f0")

        self.primary_color = "#4CAF50"
        self.secondary_color = "#e0f2f7"
        self.accent_faculty = "#e07a5f"
        self.accent_student = "#81b29a"
        self.text_color = "#333333"

        self.loading_flag = False

        self.center_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.center_frame.pack(expand=True)

        self.show_main_screen()

        # Exit Fullscreen Button
        tk.Button(root, text="Exit Fullscreen", command=self.exit_fullscreen,
                  font=("Arial", 10), bg="#cccccc", fg=self.text_color).pack(side=tk.BOTTOM, pady=10)

    def show_main_screen(self):
        self.clear_frame()

        title = tk.Label(self.center_frame, text="Welcome to the Service Provider",
                         font=("Helvetica", 28, "bold"), bg="#f0f0f0", fg=self.primary_color)
        title.pack(pady=(50, 20))

        self.loading_label = tk.Label(self.center_frame, text="", font=("Arial", 12), bg="#f0f0f0", fg="#007bff")
        self.loading_label.pack(pady=5)

        login_button = tk.Button(self.center_frame, text="Sign in through Identity Provider",
                                 command=self.start_signin_thread, font=("Arial", 14, "bold"),
                                 bg="#3498db", fg="white", padx=20, pady=10, relief="raised")
        login_button.pack(pady=10)

        self.result_label = tk.Label(self.center_frame, text="", font=("Arial", 14), bg="#f0f0f0", fg=self.text_color)
        self.result_label.pack(pady=20)

    def clear_frame(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()

    def start_signin_thread(self):
        self.loading_flag = True
        threading.Thread(target=self.animate_loading, daemon=True).start()
        threading.Thread(target=self.sign_in_with_idp).start()

    def animate_loading(self):
        dots = ["", ".", "..", "..."]
        i = 0
        while self.loading_flag:
            self.loading_label.config(text=f"Signing in{dots[i % 4]}")
            time.sleep(0.5)
            i += 1

    def sign_in_with_idp(self):
        try:
            with open("session.jwt", "r") as f:
                token = f.read().strip()
            if not token:
                self.show_error("No session token found. Login to IdP first")
                self.loading_flag = False
                self.loading_label.config(text="")
                return

            response = requests.post(SERVER_URL, json={'JWT': token})
            self.loading_flag = False
            self.loading_label.config(text="")

            if response.status_code in (200, 201):
                user_data = response.json()
                self.result_label.config(text=f"Welcome {user_data['name']} (CMS ID: {user_data['cms_id']})")
                role = user_data.get("role", "").lower()
                self.root.after(1500, lambda: self.show_dashboard(user_data['name'], user_data['cms_id'], role))
            else:
                self.show_error(response.json().get("error", "Unknown error"))

        except Exception as e:
            self.loading_flag = False
            self.loading_label.config(text="")
            self.show_error(f"Request failed: {str(e)}")

    def show_error(self, msg):
        self.result_label.config(text=msg, fg="#dc3545")

    def show_dashboard(self, name, cms_id, role):
        self.clear_frame()
        # title_font = ("Helvetica", 24, "bold")
        # label_font = ("Arial", 14)
        # text_color = "#333333"
        # card_bg = "#f9f5e7"
        # title_font = ('Helvetica', 24, 'bold')
        # label_font = ('Arial', 14)
        # text_color = '#333333'
        # text_font = ('Arial', 12)
        # primary_color = '#28A745'  # Green for Student
        # button_font = ('Helvetica', 16, 'bold')
        # card_bg = '#f9f5e7'

        # title_text = f"{role.capitalize()} Dashboard"
        # accent_color = self.accent_faculty if role == "faculty" else self.accent_student

        # title_label = tk.Label(self.center_frame, text=title_text, font=title_font, bg="#f4f1de", fg=accent_color)
        # title_label.pack(pady=(50, 20))

        # info_frame = tk.Frame(self.center_frame, bg=card_bg, padx=30, pady=20, bd=2, relief="groove")
        # info_frame.pack(pady=20, padx=50, fill="x")

        # tk.Label(info_frame, text=f"Name: {name}", font=("Open Sans", 18, "bold"),
        #          bg=card_bg, fg=text_color, anchor="w").pack(fill="x", pady=5)
        # tk.Label(info_frame, text=f"CMS ID: {cms_id}", font=("Open Sans", 18, "bold"),
        #          bg=card_bg, fg=text_color, anchor="w").pack(fill="x", pady=5)

        if role == "faculty":
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

        else:
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

        # back_btn = tk.Button(self.center_frame, text="← Back to Login", command=self.show_main_screen,
        #                      font=("Arial", 12), bg="#d62839", fg="white", padx=15, pady=8)
        # back_btn.pack(pady=20)

    def exit_fullscreen(self):
        self.root.attributes('-fullscreen', False)

# Run App
if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceProviderApp(root)
    root.mainloop()