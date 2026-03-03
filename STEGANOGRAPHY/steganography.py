"""
╔══════════════════════════════════════════════════════════════╗
║       CYBER STEGANOGRAPHY — Hide Secrets in Plain Sight     ║
║            LSB Image Steganography with Cyber Theme         ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import os
import random
import hashlib
import time
import threading

try:
    from stegano import lsb
except ImportError:
    print("Installing stegano... run: pip install stegano")
    raise

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COLOR PALETTE — Cyber/Hacker Theme
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COLORS = {
    "bg_darkest":     "#0a0a0f",
    "bg_dark":        "#0d1117",
    "bg_mid":         "#161b22",
    "bg_panel":       "#1a1f2e",
    "bg_input":       "#0f1923",
    "neon_cyan":      "#00ffcc",
    "neon_blue":      "#00aaff",
    "neon_green":     "#39ff14",
    "neon_purple":    "#bf00ff",
    "neon_pink":      "#ff006e",
    "neon_red":       "#ff3333",
    "text_primary":   "#c9d1d9",
    "text_secondary": "#8b949e",
    "text_dim":       "#484f58",
    "border_glow":    "#00ffcc",
    "border_dim":     "#1f2937",
    "success":        "#39ff14",
    "warning":        "#ffaa00",
    "error":          "#ff3333",
    "matrix_green":   "#00ff41",
}

# Matrix rain characters
MATRIX_CHARS = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MATRIX RAIN — Background Animation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class MatrixRain:
    """Creates a matrix-style falling characters animation on a canvas."""
    
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.columns = width // 14
        self.drops = [random.randint(-30, 0) for _ in range(self.columns)]
        self.speeds = [random.uniform(0.3, 1.2) for _ in range(self.columns)]
        self.chars_on_screen = []
        self.running = True
        self.frame_count = 0
    
    def update(self):
        if not self.running:
            return
        
        self.frame_count += 1
        
        # Only update every 3rd frame for performance
        if self.frame_count % 3 != 0:
            self.canvas.after(30, self.update)
            return
        
        # Remove old characters that have faded
        for item in self.chars_on_screen[:]:
            try:
                current_color = self.canvas.itemcget(item, "fill")
                if current_color == "#001a00" or current_color == "#000500":
                    self.canvas.delete(item)
                    self.chars_on_screen.remove(item)
                elif current_color == COLORS["matrix_green"]:
                    self.canvas.itemconfig(item, fill="#00aa22")
                elif current_color == "#00aa22":
                    self.canvas.itemconfig(item, fill="#005511")
                elif current_color == "#005511":
                    self.canvas.itemconfig(item, fill="#002a08")
                elif current_color == "#002a08":
                    self.canvas.itemconfig(item, fill="#001a00")
                elif current_color == "#001a00":
                    self.canvas.itemconfig(item, fill="#000500")
                else:
                    self.canvas.delete(item)
                    self.chars_on_screen.remove(item)
            except tk.TclError:
                if item in self.chars_on_screen:
                    self.chars_on_screen.remove(item)
        
        # Add new characters
        for i in range(self.columns):
            self.drops[i] += self.speeds[i]
            y = int(self.drops[i] * 16)
            x = i * 14
            
            if y > 0 and y < self.height:
                char = random.choice(MATRIX_CHARS)
                item = self.canvas.create_text(
                    x, y, text=char,
                    fill=COLORS["matrix_green"],
                    font=("Consolas", 9),
                    anchor="nw"
                )
                self.chars_on_screen.append(item)
            
            if self.drops[i] * 16 > self.height:
                if random.random() > 0.95:
                    self.drops[i] = random.randint(-10, 0)
                    self.speeds[i] = random.uniform(0.3, 1.2)
        
        # Keep character count manageable
        while len(self.chars_on_screen) > 600:
            old_item = self.chars_on_screen.pop(0)
            try:
                self.canvas.delete(old_item)
            except tk.TclError:
                pass
        
        self.canvas.after(30, self.update)
    
    def stop(self):
        self.running = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GLOWING BUTTON — Custom Neon Button Widget
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class GlowButton(tk.Canvas):
    """A custom button with neon glow hover effect."""
    
    def __init__(self, parent, text, command, color=COLORS["neon_cyan"],
                 width=160, height=42, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=COLORS["bg_darkest"], highlightthickness=0,
                        cursor="hand2", **kwargs)
        
        self.command = command
        self.color = color
        self.text = text
        self.w = width
        self.h = height
        self.hovered = False
        
        self._draw_normal()
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
    
    def _draw_normal(self):
        self.delete("all")
        # Border
        self.create_rectangle(
            1, 1, self.w - 1, self.h - 1,
            outline=self.color, width=1,
            fill=COLORS["bg_dark"],
            tags="border"
        )
        # Corner accents
        corner_len = 8
        for cx, cy, dx, dy in [(0, 0, 1, 1), (self.w, 0, -1, 1),
                                (0, self.h, 1, -1), (self.w, self.h, -1, -1)]:
            self.create_line(cx, cy, cx + corner_len * dx, cy,
                           fill=self.color, width=2, tags="corner")
            self.create_line(cx, cy, cx, cy + corner_len * dy,
                           fill=self.color, width=2, tags="corner")
        
        # Text
        self.create_text(
            self.w // 2, self.h // 2,
            text=self.text, fill=self.color,
            font=("Consolas", 11, "bold"),
            tags="text"
        )
    
    def _draw_hovered(self):
        self.delete("all")
        # Outer glow
        self.create_rectangle(
            0, 0, self.w, self.h,
            outline=self.color, width=2,
            fill="",
            tags="glow_outer"
        )
        # Filled background
        self.create_rectangle(
            2, 2, self.w - 2, self.h - 2,
            outline="", fill=self.color,
            tags="bg_fill"
        )
        # Text (dark on bright)
        self.create_text(
            self.w // 2, self.h // 2,
            text=self.text, fill=COLORS["bg_darkest"],
            font=("Consolas", 11, "bold"),
            tags="text"
        )
    
    def _on_enter(self, event):
        self.hovered = True
        self._draw_hovered()
    
    def _on_leave(self, event):
        self.hovered = False
        self._draw_normal()
    
    def _on_click(self, event):
        if self.command:
            self.command()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CYBER ALERT — Themed Popup Dialog
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class CyberAlert(tk.Toplevel):
    """A cyber/hacker-themed alert dialog."""
    
    def __init__(self, parent, title="ALERT", message="", alert_type="error"):
        super().__init__(parent)
        
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=COLORS["bg_darkest"])
        self.attributes("-topmost", True)
        self.grab_set()
        
        # Color scheme based on alert type
        color_map = {
            "error": COLORS["neon_red"],
            "warning": COLORS["warning"],
            "success": COLORS["neon_green"],
            "info": COLORS["neon_cyan"],
        }
        accent = color_map.get(alert_type, COLORS["neon_red"])
        
        icon_map = {
            "error": "✖",
            "warning": "⚠",
            "success": "✔",
            "info": "ℹ",
        }
        icon = icon_map.get(alert_type, "✖")
        
        # Calculate size based on message
        width = 480
        height = 260
        self.geometry(f"{width}x{height}")
        
        # Center on parent
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{px}+{py}")
        
        # Main frame with neon border
        border_frame = tk.Frame(self, bg=accent)
        border_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        inner = tk.Frame(border_frame, bg=COLORS["bg_dark"])
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Top bar
        top_bar = tk.Frame(inner, bg=COLORS["bg_mid"], height=36)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)
        
        tk.Label(
            top_bar,
            text=f"  {icon}  {title.upper()}",
            font=("Consolas", 11, "bold"),
            fg=accent,
            bg=COLORS["bg_mid"],
            anchor="w"
        ).pack(side="left", padx=5)
        
        # Decorative scan line
        scan = tk.Canvas(inner, height=2, bg=COLORS["bg_dark"], highlightthickness=0)
        scan.pack(fill="x")
        scan.create_line(0, 1, width, 1, fill=accent, width=1)
        
        # Message body
        msg_frame = tk.Frame(inner, bg=COLORS["bg_dark"])
        msg_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Icon
        tk.Label(
            msg_frame,
            text=icon,
            font=("Segoe UI", 36),
            fg=accent,
            bg=COLORS["bg_dark"]
        ).pack(pady=(0, 8))
        
        # Message text
        tk.Label(
            msg_frame,
            text=message,
            font=("Consolas", 10),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_dark"],
            wraplength=400,
            justify="center"
        ).pack()
        
        # OK Button
        btn_frame = tk.Frame(inner, bg=COLORS["bg_dark"])
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ok_btn = GlowButton(
            btn_frame, "[ ACKNOWLEDGED ]", self._close,
            color=accent, width=200, height=36
        )
        ok_btn.pack()
        
        # Bottom decorative line
        bottom_scan = tk.Canvas(inner, height=2, bg=COLORS["bg_dark"], highlightthickness=0)
        bottom_scan.pack(fill="x", side="bottom")
        bottom_scan.create_line(0, 1, width, 1, fill=accent, width=1, stipple="gray50")
        
        # Glitch animation on the icon
        self._glitch_icon(top_bar, accent, title, icon)
        
        self.bind("<Return>", lambda e: self._close())
        self.bind("<Escape>", lambda e: self._close())
        
        self.wait_window()
    
    def _glitch_icon(self, label_parent, color, title, icon):
        """Brief glitch flicker on the title."""
        children = label_parent.winfo_children()
        if not children:
            return
        title_lbl = children[0]
        glitch_chars = "@#$%&!?*"
        
        def flicker(count=0):
            if count >= 6:
                title_lbl.configure(text=f"  {icon}  {title.upper()}")
                return
            if count % 2 == 0:
                glitch = "".join(random.choice(glitch_chars) for _ in range(len(title)))
                title_lbl.configure(text=f"  {icon}  {glitch}", fg=COLORS["neon_red"])
            else:
                title_lbl.configure(text=f"  {icon}  {title.upper()}", fg=color)
            try:
                self.after(80, lambda: flicker(count + 1))
            except tk.TclError:
                pass
        
        self.after(100, flicker)
    
    def _close(self):
        self.grab_release()
        self.destroy()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CYBER STEGANOGRAPHY — Main Application
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class CyberSteganographyApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("CYBER STEGANOGRAPHY // v2.0")
        self.root.geometry("1050x720")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg_darkest"])
        
        # State
        self.filename = None
        self.secret_image = None
        self.original_image = None
        self.console_lines = []
        self.scan_animation_id = None
        
        # Try to set a dark title bar on Windows
        try:
            from ctypes import windll
            windll.dwmapi.DwmSetWindowAttribute(
                windll.user32.GetParent(self.root.winfo_id()),
                20, byref(c_int(2)), sizeof(c_int(2))
            )
        except:
            pass
        
        self._build_ui()
        self._log("SYSTEM", "Cyber Steganography initialized...")
        self._log("SYSTEM", "Ready. Select an image to begin.")
        self._animate_title_glow()
    
    # ──────────────────────────────────────────────────
    #  BUILD UI
    # ──────────────────────────────────────────────────
    def _build_ui(self):
        # ── BACKGROUND MATRIX CANVAS ──
        self.bg_canvas = tk.Canvas(
            self.root, width=1050, height=720,
            bg=COLORS["bg_darkest"], highlightthickness=0
        )
        self.bg_canvas.place(x=0, y=0)
        self.matrix = MatrixRain(self.bg_canvas, 1050, 720)
        self.matrix.update()
        
        # ── MAIN OVERLAY FRAME ──
        # Semi-transparent effect achieved by darkened panel on top of canvas
        self.main_frame = tk.Frame(
            self.root, bg=COLORS["bg_dark"],
            highlightbackground=COLORS["border_dim"],
            highlightthickness=1
        )
        self.main_frame.place(x=20, y=15, width=1010, height=690)
        
        # ── HEADER ──
        self._build_header()
        
        # ── LEFT PANEL — Image Preview ──
        self._build_image_panel()
        
        # ── RIGHT PANEL — Message / Controls ──
        self._build_message_panel()
        
        # ── BOTTOM — Console ──
        self._build_console()
        
        # ── ACTION BUTTONS BAR ──
        self._build_action_buttons()
    
    def _build_header(self):
        header = tk.Frame(self.main_frame, bg=COLORS["bg_dark"], height=65)
        header.pack(fill="x", padx=10, pady=(8, 0))
        header.pack_propagate(False)
        
        # Decorative left line
        tk.Canvas(
            header, width=60, height=2, bg=COLORS["neon_cyan"],
            highlightthickness=0
        ).place(x=0, y=32)
        
        # Title
        self.title_label = tk.Label(
            header,
            text="◈  CYBER STEGANOGRAPHY  ◈",
            font=("Consolas", 22, "bold"),
            fg=COLORS["neon_cyan"],
            bg=COLORS["bg_dark"]
        )
        self.title_label.place(x=75, y=8)
        
        # Subtitle
        tk.Label(
            header,
            text="HIDE  ·  ENCRYPT  ·  PROTECT  ·  LSB ENCODING  ·  v2.0",
            font=("Consolas", 9),
            fg=COLORS["text_dim"],
            bg=COLORS["bg_dark"]
        ).place(x=77, y=42)
        
        # Decorative right line
        tk.Canvas(
            header, width=200, height=2, bg=COLORS["neon_cyan"],
            highlightthickness=0
        ).place(x=780, y=32)
        
        # Status indicator dot
        self.status_dot = tk.Canvas(
            header, width=12, height=12,
            bg=COLORS["bg_dark"], highlightthickness=0
        )
        self.status_dot.place(x=975, y=28)
        self.status_dot.create_oval(2, 2, 10, 10, fill=COLORS["neon_green"], outline="")
        
        # Separator line below header
        sep = tk.Canvas(
            self.main_frame, height=1, bg=COLORS["bg_dark"],
            highlightthickness=0
        )
        sep.pack(fill="x", padx=15, pady=(0, 5))
        sep.create_line(0, 0, 1000, 0, fill=COLORS["border_dim"], width=1)
    
    def _build_image_panel(self):
        # Container for left side
        self.left_container = tk.Frame(
            self.main_frame, bg=COLORS["bg_dark"]
        )
        self.left_container.place(x=15, y=78, width=480, height=370)
        
        # Panel label
        tk.Label(
            self.left_container,
            text="┌─ IMAGE PREVIEW ──────────────────────────────────┐",
            font=("Consolas", 9),
            fg=COLORS["neon_cyan"],
            bg=COLORS["bg_dark"],
            anchor="w"
        ).place(x=0, y=0)
        
        # Image frame with neon border
        self.image_outer = tk.Frame(
            self.left_container,
            bg=COLORS["neon_cyan"],
            highlightthickness=0
        )
        self.image_outer.place(x=2, y=22, width=474, height=280)
        
        self.image_frame = tk.Frame(
            self.image_outer,
            bg=COLORS["bg_darkest"],
        )
        self.image_frame.place(x=1, y=1, width=472, height=278)
        
        # Image label (for displaying the loaded image)
        self.image_label = tk.Label(
            self.image_frame,
            bg=COLORS["bg_darkest"],
            fg=COLORS["text_dim"],
            text="[ NO IMAGE LOADED ]\n\nClick 'LOAD IMAGE' to select a file\nSupported: PNG, JPG, BMP",
            font=("Consolas", 10),
            justify="center",
            compound="center"
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Scan line effect canvas (overlaid on image)
        self.scan_canvas = tk.Canvas(
            self.image_frame, width=472, height=278,
            bg=COLORS["bg_darkest"], highlightthickness=0
        )
        
        # Info panel below image
        self.info_frame = tk.Frame(
            self.left_container, bg=COLORS["bg_panel"],
            highlightbackground=COLORS["border_dim"],
            highlightthickness=1
        )
        self.info_frame.place(x=2, y=308, width=474, height=58)
        
        # Info labels
        self.info_file = tk.Label(
            self.info_frame,
            text="FILE: —",
            font=("Consolas", 8),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_panel"],
            anchor="w"
        )
        self.info_file.place(x=8, y=4)
        
        self.info_size = tk.Label(
            self.info_frame,
            text="SIZE: —  |  RES: —",
            font=("Consolas", 8),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_panel"],
            anchor="w"
        )
        self.info_size.place(x=8, y=22)
        
        self.info_capacity = tk.Label(
            self.info_frame,
            text="CAPACITY: —",
            font=("Consolas", 8),
            fg=COLORS["neon_green"],
            bg=COLORS["bg_panel"],
            anchor="w"
        )
        self.info_capacity.place(x=8, y=40)
        
        # Bottom border label
        tk.Label(
            self.left_container,
            text="└──────────────────────────────────────────────────┘",
            font=("Consolas", 9),
            fg=COLORS["border_dim"],
            bg=COLORS["bg_dark"],
            anchor="w"
        ).place(x=0, y=368)
    
    def _build_message_panel(self):
        # Container for right side
        self.right_container = tk.Frame(
            self.main_frame, bg=COLORS["bg_dark"]
        )
        self.right_container.place(x=510, y=78, width=485, height=370)
        
        # Panel label
        tk.Label(
            self.right_container,
            text="┌─ SECRET MESSAGE ─────────────────────────────────┐",
            font=("Consolas", 9),
            fg=COLORS["neon_cyan"],
            bg=COLORS["bg_dark"],
            anchor="w"
        ).place(x=0, y=0)
        
        # Message text area with neon border
        text_outer = tk.Frame(
            self.right_container,
            bg=COLORS["neon_cyan"]
        )
        text_outer.place(x=2, y=22, width=479, height=230)
        
        text_inner = tk.Frame(text_outer, bg=COLORS["bg_input"])
        text_inner.place(x=1, y=1, width=477, height=228)
        
        self.message_text = tk.Text(
            text_inner,
            font=("Consolas", 11),
            bg=COLORS["bg_input"],
            fg=COLORS["neon_green"],
            insertbackground=COLORS["neon_cyan"],
            selectbackground=COLORS["neon_blue"],
            selectforeground=COLORS["bg_darkest"],
            relief="flat",
            wrap="word",
            padx=10,
            pady=8,
            highlightthickness=0
        )
        self.message_text.place(x=0, y=0, width=460, height=226)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(
            text_inner, command=self.message_text.yview,
            bg=COLORS["bg_mid"],
            troughcolor=COLORS["bg_darkest"],
            activebackground=COLORS["neon_cyan"]
        )
        scrollbar.place(x=460, y=0, width=15, height=226)
        self.message_text.configure(yscrollcommand=scrollbar.set)
        
        # Character count
        self.char_count_label = tk.Label(
            self.right_container,
            text="CHARS: 0",
            font=("Consolas", 8),
            fg=COLORS["text_dim"],
            bg=COLORS["bg_dark"],
            anchor="e"
        )
        self.char_count_label.place(x=380, y=255)
        self.message_text.bind("<KeyRelease>", self._update_char_count)
        
        # ── PASSWORD SECTION ──
        pw_frame = tk.Frame(
            self.right_container, bg=COLORS["bg_panel"],
            highlightbackground=COLORS["border_dim"],
            highlightthickness=1
        )
        pw_frame.place(x=2, y=275, width=479, height=55)
        
        tk.Label(
            pw_frame,
            text="🔒 PASSWORD (optional):",
            font=("Consolas", 9),
            fg=COLORS["neon_purple"],
            bg=COLORS["bg_panel"],
            anchor="w"
        ).place(x=8, y=4)
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            pw_frame,
            textvariable=self.password_var,
            show="●",
            font=("Consolas", 11),
            bg=COLORS["bg_input"],
            fg=COLORS["neon_purple"],
            insertbackground=COLORS["neon_purple"],
            relief="flat",
            highlightbackground=COLORS["border_dim"],
            highlightthickness=1
        )
        self.password_entry.place(x=8, y=26, width=340, height=24)
        
        # Toggle password visibility
        self.pw_visible = False
        self.pw_toggle_btn = tk.Label(
            pw_frame, text="👁", font=("Segoe UI", 11),
            fg=COLORS["text_dim"], bg=COLORS["bg_panel"],
            cursor="hand2"
        )
        self.pw_toggle_btn.place(x=358, y=24)
        self.pw_toggle_btn.bind("<Button-1>", self._toggle_password)
        
        # Copy decoded message button
        self.copy_btn = tk.Label(
            pw_frame, text="📋 COPY", font=("Consolas", 8, "bold"),
            fg=COLORS["neon_blue"], bg=COLORS["bg_panel"],
            cursor="hand2"
        )
        self.copy_btn.place(x=400, y=28)
        self.copy_btn.bind("<Button-1>", self._copy_message)
        
        # Mode indicator
        self.mode_label = tk.Label(
            self.right_container,
            text="MODE: STANDBY",
            font=("Consolas", 9, "bold"),
            fg=COLORS["text_dim"],
            bg=COLORS["bg_dark"],
            anchor="w"
        )
        self.mode_label.place(x=5, y=340)
        
        # Bottom border
        tk.Label(
            self.right_container,
            text="└──────────────────────────────────────────────────┘",
            font=("Consolas", 9),
            fg=COLORS["border_dim"],
            bg=COLORS["bg_dark"],
            anchor="w"
        ).place(x=0, y=355)
    
    def _build_console(self):
        # Console panel at bottom
        console_container = tk.Frame(
            self.main_frame, bg=COLORS["bg_dark"]
        )
        console_container.place(x=15, y=455, width=980, height=130)
        
        tk.Label(
            console_container,
            text="┌─ SYSTEM CONSOLE ─────────────────────────────────────────────────────────────────────────────────────────┐",
            font=("Consolas", 9),
            fg=COLORS["neon_green"],
            bg=COLORS["bg_dark"],
            anchor="w"
        ).place(x=0, y=0)
        
        console_outer = tk.Frame(
            console_container,
            bg=COLORS["neon_green"]
        )
        console_outer.place(x=2, y=18, width=974, height=95)
        
        console_inner = tk.Frame(console_outer, bg="#0a0f0a")
        console_inner.place(x=1, y=1, width=972, height=93)
        
        self.console_text = tk.Text(
            console_inner,
            font=("Consolas", 9),
            bg="#0a0f0a",
            fg=COLORS["neon_green"],
            relief="flat",
            wrap="word",
            padx=8,
            pady=5,
            highlightthickness=0,
            state="disabled",
            cursor="arrow"
        )
        self.console_text.place(x=0, y=0, width=955, height=91)
        
        console_sb = tk.Scrollbar(
            console_inner, command=self.console_text.yview,
            bg="#0a0f0a",
            troughcolor="#0a0f0a",
            activebackground=COLORS["neon_green"]
        )
        console_sb.place(x=955, y=0, width=15, height=91)
        self.console_text.configure(yscrollcommand=console_sb.set)
        
        # Configure text tags for colored output
        self.console_text.tag_config("system", foreground=COLORS["neon_cyan"])
        self.console_text.tag_config("success", foreground=COLORS["neon_green"])
        self.console_text.tag_config("error", foreground=COLORS["neon_red"])
        self.console_text.tag_config("warning", foreground=COLORS["warning"])
        self.console_text.tag_config("info", foreground=COLORS["text_secondary"])
        self.console_text.tag_config("crypto", foreground=COLORS["neon_purple"])
        self.console_text.tag_config("prompt", foreground=COLORS["neon_green"])
        
        tk.Label(
            console_container,
            text="└───────────────────────────────────────────────────────────────────────────────────────────────────────────┘",
            font=("Consolas", 9),
            fg=COLORS["border_dim"],
            bg=COLORS["bg_dark"],
            anchor="w"
        ).place(x=0, y=115)
    
    def _build_action_buttons(self):
        btn_bar = tk.Frame(
            self.main_frame, bg=COLORS["bg_dark"]
        )
        btn_bar.place(x=15, y=592, width=980, height=55)
        
        # Separator
        sep = tk.Canvas(
            btn_bar, height=1, bg=COLORS["bg_dark"],
            highlightthickness=0
        )
        sep.place(x=0, y=0, width=980)
        sep.create_line(0, 0, 980, 0, fill=COLORS["border_dim"])
        
        # Buttons
        buttons_data = [
            ("⟦ LOAD IMAGE ⟧", self._load_image, COLORS["neon_cyan"], 0),
            ("⟦ ENCODE ▶ ⟧", self._encode, COLORS["neon_green"], 175),
            ("⟦ DECODE ◀ ⟧", self._decode, COLORS["neon_blue"], 350),
            ("⟦ SAVE IMAGE ⟧", self._save_image, COLORS["neon_purple"], 525),
            ("⟦ CLEAR ALL ⟧", self._clear_all, COLORS["neon_pink"], 700),
            ("⟦ ABOUT ⟧", self._show_about, COLORS["text_dim"], 875),
        ]
        
        for text, cmd, color, x_pos in buttons_data:
            btn = GlowButton(btn_bar, text, cmd, color=color, width=155, height=42)
            btn.place(x=x_pos, y=8)
        
        # Progress bar
        self.progress_frame = tk.Frame(
            self.main_frame, bg=COLORS["bg_dark"]
        )
        self.progress_frame.place(x=15, y=650, width=980, height=8)
        
        self.progress_canvas = tk.Canvas(
            self.progress_frame, width=980, height=6,
            bg=COLORS["bg_darkest"], highlightthickness=0
        )
        self.progress_canvas.pack()
        self.progress_bar = None
    
    # ──────────────────────────────────────────────────
    #  ANIMATIONS
    # ──────────────────────────────────────────────────
    def _animate_title_glow(self):
        """Pulsing glow on the title between cyan shades."""
        colors_cycle = [
            "#00ffcc", "#00eebb", "#00ddaa", "#00cc99",
            "#00bb88", "#00cc99", "#00ddaa", "#00eebb"
        ]
        
        def pulse(idx=0):
            try:
                self.title_label.configure(fg=colors_cycle[idx % len(colors_cycle)])
                self.root.after(200, lambda: pulse(idx + 1))
            except tk.TclError:
                pass
        
        pulse()
    
    def _animate_progress(self, duration_ms=1500):
        """Animated progress bar sweep."""
        self.progress_canvas.delete("progress")
        steps = 30
        
        def step(i=0):
            if i > steps:
                self.progress_canvas.delete("progress")
                return
            width = int((i / steps) * 980)
            self.progress_canvas.delete("progress")
            # Gradient effect via multiple rects
            self.progress_canvas.create_rectangle(
                0, 0, width, 6,
                fill=COLORS["neon_cyan"], outline="",
                tags="progress"
            )
            # Bright tip
            if width > 5:
                self.progress_canvas.create_rectangle(
                    max(0, width - 40), 0, width, 6,
                    fill="#ffffff", outline="",
                    tags="progress"
                )
            self.root.after(duration_ms // steps, lambda: step(i + 1))
        
        step()
    
    def _animate_scan_line(self):
        """Scanning line over the image preview."""
        try:
            self.scan_canvas.place(x=0, y=0)
            self.scan_canvas.tkraise(self.image_label)
        except tk.TclError:
            # If raise fails, just place on top — still works visually
            pass
        
        def sweep(y=0):
            if y > 278:
                try:
                    self.scan_canvas.place_forget()
                except tk.TclError:
                    pass
                return
            self.scan_canvas.delete("scan")
            # Draw scan line
            self.scan_canvas.create_line(
                0, y, 472, y,
                fill=COLORS["neon_cyan"], width=2,
                tags="scan"
            )
            # Fading trail
            for offset in range(1, 15):
                try:
                    self.scan_canvas.create_line(
                        0, y - offset * 2, 472, y - offset * 2,
                        fill=COLORS["neon_cyan"], width=1,
                        stipple="gray25",
                        tags="scan"
                    )
                except:
                    pass
            self.scan_animation_id = self.root.after(8, lambda: sweep(y + 3))
        
        sweep()
    
    # ──────────────────────────────────────────────────
    #  CONSOLE LOGGING
    # ──────────────────────────────────────────────────
    def _log(self, tag, message):
        """Log a message to the hacker console."""
        timestamp = time.strftime("%H:%M:%S")
        tag_upper = tag.upper()
        
        tag_map = {
            "SYSTEM": "system",
            "SUCCESS": "success",
            "ERROR": "error",
            "WARNING": "warning",
            "INFO": "info",
            "CRYPTO": "crypto",
        }
        text_tag = tag_map.get(tag_upper, "prompt")
        
        self.console_text.configure(state="normal")
        self.console_text.insert(
            "end",
            f"[{timestamp}] ",
            "info"
        )
        self.console_text.insert(
            "end",
            f"<{tag_upper}> ",
            text_tag
        )
        self.console_text.insert(
            "end",
            f"{message}\n",
            text_tag
        )
        self.console_text.configure(state="disabled")
        self.console_text.see("end")
    
    # ──────────────────────────────────────────────────
    #  ENCRYPTION (XOR with password hash)
    # ──────────────────────────────────────────────────
    def _encrypt_message(self, message, password):
        """XOR encrypt with verification hash. Format: base64(hash_8_bytes + xor_encrypted_bytes)"""
        if not password:
            return message
        import base64
        key = hashlib.sha256(password.encode()).digest()
        msg_bytes = message.encode("utf-8")
        # Verification: first 8 bytes of SHA-256 of original message
        verify_hash = hashlib.sha256(msg_bytes).digest()[:8]
        encrypted_bytes = bytes([b ^ key[i % len(key)] for i, b in enumerate(msg_bytes)])
        # Prepend hash to encrypted data
        payload = verify_hash + encrypted_bytes
        return base64.b64encode(payload).decode("ascii")
    
    def _decrypt_message(self, encrypted_b64, password):
        """Decrypt and verify. Raises ValueError if password is wrong."""
        if not password:
            return encrypted_b64
        import base64
        key = hashlib.sha256(password.encode()).digest()
        payload = base64.b64decode(encrypted_b64.encode("ascii"))
        # Extract verification hash (first 8 bytes)
        stored_hash = payload[:8]
        encrypted_bytes = payload[8:]
        # Decrypt
        decrypted_bytes = bytes([b ^ key[i % len(key)] for i, b in enumerate(encrypted_bytes)])
        # Verify hash
        computed_hash = hashlib.sha256(decrypted_bytes).digest()[:8]
        if stored_hash != computed_hash:
            raise ValueError("DECRYPTION FAILED — Wrong password")
        return decrypted_bytes.decode("utf-8")
    
    # ──────────────────────────────────────────────────
    #  CORE FUNCTIONS
    # ──────────────────────────────────────────────────
    def _load_image(self):
        """Open and display an image file."""
        self._log("SYSTEM", "Opening file dialog...")
        
        filepath = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select Cover Image",
            filetypes=(
                ("Image Files", "*.png *.jpg *.jpeg *.bmp"),
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg *.jpeg"),
                ("BMP Files", "*.bmp"),
                ("All Files", "*.*"),
            )
        )
        
        if not filepath:
            self._log("WARNING", "No file selected. Operation cancelled.")
            return
        
        try:
            self.filename = filepath
            self.original_image = Image.open(filepath)
            
            # Display the image (scaled to fit)
            display_img = self.original_image.copy()
            display_img.thumbnail((468, 274), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(display_img)
            
            self.image_label.configure(
                image=self.tk_image,
                text=""
            )
            self.image_label.image = self.tk_image
            
            # Update file info
            file_size = os.path.getsize(filepath)
            file_name = os.path.basename(filepath)
            width, height = self.original_image.size
            
            # Capacity estimate: ~3 bits per pixel for RGB, 8 bits per char
            capacity = (width * height * 3) // 8
            
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024*1024):.1f} MB"
            else:
                size_str = f"{file_size / 1024:.1f} KB"
            
            self.info_file.configure(
                text=f"FILE: {file_name}"
            )
            self.info_size.configure(
                text=f"SIZE: {size_str}  |  RES: {width}×{height}px  |  MODE: {self.original_image.mode}"
            )
            self.info_capacity.configure(
                text=f"CAPACITY: ~{capacity:,} characters  ({capacity // 1024} KB)"
            )
            
            self.mode_label.configure(text="MODE: IMAGE LOADED", fg=COLORS["neon_cyan"])
            
            self._log("SUCCESS", f"Image loaded: {file_name}")
            self._log("INFO", f"  Resolution: {width}×{height}  |  Size: {size_str}  |  Mode: {self.original_image.mode}")
            self._log("INFO", f"  Estimated capacity: ~{capacity:,} chars")
            
            # Scan animation
            self._animate_scan_line()
            
        except Exception as e:
            self._log("ERROR", f"Failed to load image: {str(e)}")
            messagebox.showerror("Error", f"Could not open image:\n{str(e)}")
    
    def _encode(self):
        """Hide a message in the loaded image using LSB steganography."""
        if not self.filename:
            self._log("ERROR", "No image loaded! Load an image first.")
            messagebox.showwarning("No Image", "Please load an image first.")
            return
        
        message = self.message_text.get("1.0", "end-1c").strip()
        if not message:
            self._log("ERROR", "No message to encode! Enter a secret message.")
            messagebox.showwarning("No Message", "Please enter a secret message to hide.")
            return
        
        password = self.password_var.get()
        
        self._log("SYSTEM", "Starting encode operation...")
        self._log("INFO", f"  Message length: {len(message)} chars")
        self._animate_progress(2000)
        self.mode_label.configure(text="MODE: ENCODING...", fg=COLORS["neon_green"])
        self.root.update()
        
        try:
            # Encrypt if password provided
            if password:
                self._log("CRYPTO", f"Encrypting with password (SHA-256 XOR)...")
                message = self._encrypt_message(message, password)
                # Add a marker so we know it's encrypted
                message = "<<ENC>>" + message
                self._log("CRYPTO", "Message encrypted successfully.")
            
            self._log("SYSTEM", "Embedding message via LSB steganography...")
            self.secret_image = lsb.hide(self.filename, message, auto_convert_rgb=True)
            
            self._log("SUCCESS", "═══════════════════════════════════════")
            self._log("SUCCESS", "  MESSAGE ENCODED SUCCESSFULLY!")
            self._log("SUCCESS", "  Use 'SAVE IMAGE' to export the result.")
            self._log("SUCCESS", "═══════════════════════════════════════")
            
            self.mode_label.configure(text="MODE: ENCODED ✓", fg=COLORS["success"])
            
        except Exception as e:
            self._log("ERROR", f"Encoding failed: {str(e)}")
            messagebox.showerror("Encode Error", f"Failed to encode message:\n{str(e)}")
            self.mode_label.configure(text="MODE: ERROR", fg=COLORS["error"])
    
    def _decode(self):
        """Reveal a hidden message from the loaded image."""
        if not self.filename:
            self._log("ERROR", "No image loaded! Load an image first.")
            messagebox.showwarning("No Image", "Please load an image first.")
            return
        
        self._log("SYSTEM", "Starting decode operation...")
        self._animate_progress(1500)
        self.mode_label.configure(text="MODE: DECODING...", fg=COLORS["neon_blue"])
        self.root.update()
        
        try:
            self._log("SYSTEM", "Extracting LSB data from image pixels...")
            hidden_message = lsb.reveal(self.filename)
            
            if hidden_message is None:
                self._log("WARNING", "No hidden message found in this image.")
                messagebox.showinfo("No Data", "No hidden message was found in this image.")
                self.mode_label.configure(text="MODE: NO DATA FOUND", fg=COLORS["warning"])
                return
            
            password = self.password_var.get()
            
            # Check if encrypted
            if hidden_message.startswith("<<ENC>>"):
                self._log("CRYPTO", "Encrypted message detected!")
                if not password:
                    self._log("WARNING", "This message is password-protected. Enter the password and try again.")
                    messagebox.showwarning(
                        "Password Required",
                        "This message is encrypted. Enter the correct password and decode again."
                    )
                    self.mode_label.configure(text="MODE: PASSWORD REQUIRED", fg=COLORS["neon_purple"])
                    return
                
                self._log("CRYPTO", "Decrypting with provided password...")
                try:
                    hidden_message = self._decrypt_message(
                        hidden_message[7:],  # Remove <<ENC>> prefix
                        password
                    )
                except ValueError:
                    self._log("ERROR", "═══════════════════════════════════════")
                    self._log("ERROR", "  DECRYPTION FAILED!")
                    self._log("ERROR", "  Access denied — wrong password.")
                    self._log("ERROR", "═══════════════════════════════════════")
                    self.mode_label.configure(text="MODE: ACCESS DENIED ✖", fg=COLORS["error"])
                    CyberAlert(
                        self.root,
                        title="ACCESS DENIED",
                        message=(
                            "DECRYPTION FAILED\n\n"
                            "The password you entered is incorrect.\n"
                            "The encrypted payload could not be verified.\n\n"
                            ">> Check your password and try again. <<"
                        ),
                        alert_type="error"
                    )
                    return
                self._log("CRYPTO", "Password verified. Decryption complete.")
            
            # Display the message
            self.message_text.delete("1.0", "end")
            self.message_text.insert("1.0", hidden_message)
            self._update_char_count()
            
            self._log("SUCCESS", "═══════════════════════════════════════")
            self._log("SUCCESS", "  MESSAGE DECODED SUCCESSFULLY!")
            self._log("SUCCESS", f"  Length: {len(hidden_message)} characters")
            self._log("SUCCESS", "═══════════════════════════════════════")
            
            self.mode_label.configure(text="MODE: DECODED ✓", fg=COLORS["success"])
            
            # Scan animation
            self._animate_scan_line()
            
        except Exception as e:
            self._log("ERROR", f"Decoding failed: {str(e)}")
            messagebox.showerror("Decode Error", f"Failed to decode message:\n{str(e)}")
            self.mode_label.configure(text="MODE: ERROR", fg=COLORS["error"])
    
    def _save_image(self):
        """Save the steganographic image."""
        if not self.secret_image:
            self._log("ERROR", "No encoded image to save! Encode a message first.")
            messagebox.showwarning("Nothing to Save", "Encode a message first before saving.")
            return
        
        self._log("SYSTEM", "Opening save dialog...")
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=(("PNG Files", "*.png"), ("All Files", "*.*")),
            title="Save Steganographic Image",
            initialfile="stego_output.png"
        )
        
        if not filepath:
            self._log("WARNING", "Save cancelled.")
            return
        
        try:
            self.secret_image.save(filepath)
            file_size = os.path.getsize(filepath)
            
            if file_size > 1024 * 1024:
                size_str = f"{file_size / (1024*1024):.1f} MB"
            else:
                size_str = f"{file_size / 1024:.1f} KB"
            
            self._log("SUCCESS", f"Image saved: {os.path.basename(filepath)} ({size_str})")
            self._log("INFO", f"  Full path: {filepath}")
            self._animate_progress(1000)
            self.mode_label.configure(text="MODE: SAVED ✓", fg=COLORS["success"])
            
        except Exception as e:
            self._log("ERROR", f"Save failed: {str(e)}")
            messagebox.showerror("Save Error", f"Failed to save:\n{str(e)}")
    
    def _clear_all(self):
        """Reset everything."""
        self.filename = None
        self.secret_image = None
        self.original_image = None
        
        self.image_label.configure(
            image="",
            text="[ NO IMAGE LOADED ]\n\nClick 'LOAD IMAGE' to select a file\nSupported: PNG, JPG, BMP"
        )
        self.image_label.image = None
        
        self.message_text.delete("1.0", "end")
        self.password_var.set("")
        
        self.info_file.configure(text="FILE: —")
        self.info_size.configure(text="SIZE: —  |  RES: —")
        self.info_capacity.configure(text="CAPACITY: —")
        self.char_count_label.configure(text="CHARS: 0")
        self.mode_label.configure(text="MODE: STANDBY", fg=COLORS["text_dim"])
        
        self._log("SYSTEM", "All data cleared. Ready for new operation.")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = (
            "◈ CYBER STEGANOGRAPHY v2.0 ◈\n\n"
            "Advanced LSB Image Steganography Tool\n"
            "with optional password encryption.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Technique: Least Significant Bit (LSB)\n"
            "Encryption: SHA-256 XOR Cipher\n"
            "Formats: PNG, JPG, BMP\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Hide your secrets in plain sight."
        )
        messagebox.showinfo("About — Cyber Steganography", about_text)
    
    # ──────────────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────────────
    def _update_char_count(self, event=None):
        count = len(self.message_text.get("1.0", "end-1c"))
        self.char_count_label.configure(text=f"CHARS: {count}")
    
    def _toggle_password(self, event=None):
        self.pw_visible = not self.pw_visible
        self.password_entry.configure(show="" if self.pw_visible else "●")
        self.pw_toggle_btn.configure(
            fg=COLORS["neon_purple"] if self.pw_visible else COLORS["text_dim"]
        )
    
    def _copy_message(self, event=None):
        message = self.message_text.get("1.0", "end-1c")
        if message.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(message)
            self._log("INFO", "Message copied to clipboard.")
        else:
            self._log("WARNING", "Nothing to copy — message area is empty.")
    
    def on_close(self):
        """Clean shutdown."""
        self.matrix.stop()
        self.root.destroy()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LAUNCH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    root = tk.Tk()
    app = CyberSteganographyApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
