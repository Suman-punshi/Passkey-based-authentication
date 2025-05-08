import tkinter as tk
import random
import time
import threading
import requests

SERVER_URL = "http://localhost:5000/login"

class AnimatedBackground:
    def __init__(self, canvas, colors):
        self.canvas = canvas
        self.colors = colors
        self.shapes = []
        self.canvas.after(100, self.create_shapes)  # Delay to allow layout
        self.animate()

    def create_shapes(self):
        emojis = {'lock': "🔒", 'shield': "🛡️", 'key': "🔑"}
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width == 1 or height == 1:
            # Canvas hasn't fully rendered yet, retry shortly
            self.canvas.after(100, self.create_shapes)
            return

        for _ in range(35):
            shape_type = random.choice(list(emojis.keys()))
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(20, 40)
            color = random.choice(self.colors)
            dx = random.choice([-1, 1]) * random.uniform(0.3, 0.6)
            dy = random.choice([-1, 1]) * random.uniform(0.3, 0.6)

            emoji = emojis[shape_type]
            text_item = self.canvas.create_text(x, y, text=emoji, font=("Arial", r), fill=color)
            self.shapes.append((text_item, dx, dy))

    def animate(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        for idx, (text_item, dx, dy) in enumerate(self.shapes):
            self.canvas.move(text_item, dx, dy)
            coords = self.canvas.bbox(text_item)
            if coords:
                if coords[0] <= 0 or coords[2] >= width:
                    dx = -dx
                if coords[1] <= 0 or coords[3] >= height:
                    dy = -dy
                self.shapes[idx] = (text_item, dx, dy)

        self.canvas.after(30, self.animate)


class ServiceProviderApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.title("🔐 Service Provider Login")
        self.root.geometry("1024x600")  # Initial size
        self.root.minsize(800, 500)

        self.bg_color = "#1e1e2f"
        self.fg_color = "#ffffff"
        self.accent_color = "#6c5ce7"
        self.student_color = "#00cec9"
        self.faculty_color = "#ffeaa7"
        self.text_color = "#f5f6fa"

        self.loading_flag = False

        self.canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.on_resize)

        self.center_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.canvas_window = self.canvas.create_window(0, 0, window=self.center_frame)

        self.anim_bg = AnimatedBackground(self.canvas, [self.accent_color, self.student_color, self.faculty_color])

        self.show_main_screen()

        tk.Button(self.root, text="Exit Fullscreen", command=self.exit_fullscreen,
                  font=("Arial", 10), bg="#444", fg="white").place(relx=0.01, rely=0.95)

    def on_resize(self, event):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.coords(self.canvas_window, width // 2, height // 2)

    def show_main_screen(self):
        self.clear_frame()

        title = tk.Label(self.center_frame, text="🌐 Service Provider Login",
                         font=("Helvetica", 26, "bold"), bg=self.bg_color, fg=self.accent_color)
        title.pack(pady=(50, 20))

        self.loading_label = tk.Label(self.center_frame, text="", font=("Arial", 12),
                                      bg=self.bg_color, fg=self.student_color)
        self.loading_label.pack(pady=5)

        login_btn = tk.Button(self.center_frame, text="Sign in via Identity Provider",
                              command=self.start_signin_thread,
                              font=("Arial", 14, "bold"), bg=self.accent_color, fg="white", padx=20, pady=10)
        login_btn.pack(pady=10)

        self.result_label = tk.Label(self.center_frame, text="", font=("Arial", 14),
                                     bg=self.bg_color, fg="white")
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
                return

            response = requests.post(SERVER_URL, json={'JWT': token})
            self.loading_flag = False

            if response.status_code in (200, 201):
                user_data = response.json()
                role = user_data.get("role", "").lower()
                self.result_label.config(text=f"Welcome {user_data['name']} (CMS ID: {user_data['cms_id']})")
                self.root.after(1500, lambda: self.show_dashboard(user_data['name'], user_data['cms_id'], role))
            else:
                self.show_error(response.json().get("error", "Unknown error"))

        except Exception as e:
            self.loading_flag = False
            self.show_error(f"Request failed: {str(e)}")

    def show_error(self, msg):
        self.result_label.config(text=msg, fg="#e74c3c")

    def show_dashboard(self, name, cms_id, role):
        self.clear_frame()
        color = self.faculty_color if role == "faculty" else self.student_color

        title = tk.Label(self.center_frame,
                         text=f"{'Faculty' if role == 'faculty' else 'Student'} Dashboard",
                         font=("Helvetica", 24, "bold"), bg=self.bg_color, fg=color)
        title.pack(pady=(50, 10))

        card_frame = tk.Frame(self.center_frame, bg="#2c2c3e", padx=40, pady=30)
        card_frame.pack(pady=20)

        def info(label, value):
            tk.Label(card_frame, text=f"{label}: {value}", font=("Arial", 16),
                     bg="#2c2c3e", fg=self.text_color, anchor='w').pack(fill='x', pady=5)

        info("👤 Name", name)
        info("🆔 CMS ID", cms_id)
        info("🎓 Role", role.title())

        if role == "faculty":
            welcome_text = (
                "Welcome to your personalized faculty dashboard!\n"
                "Here you can access everything you need to manage your courses, "
                "students, and research."
            )
        else:
            welcome_text = (
                "Hi there! 👋\n\n"
                "We're glad to have you here. Explore your dashboard to manage courses, "
                "track assignments, and stay updated with your academic journey.\n\n"
                "Wishing you a productive and successful semester ahead!"
            )

        tk.Label(self.center_frame, text=welcome_text, font=("Arial", 14, "italic"),
                 bg=self.bg_color, fg="#f5f6fa", wraplength=600, justify="left").pack(pady=(10, 30))

        back_btn = tk.Button(self.center_frame, text="← Back to Login",
                             command=self.show_main_screen, font=("Arial", 12),
                             bg="#e74c3c", fg="white", padx=15, pady=8)
        back_btn.pack(pady=20)

    def exit_fullscreen(self):
        self.root.attributes('-fullscreen', False)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceProviderApp(root)
    root.mainloop()
