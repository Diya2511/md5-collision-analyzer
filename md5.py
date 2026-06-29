import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog
import hashlib
import difflib
import os

# ---------- THEME ----------
ctk.set_appearance_mode("dark")

PRIMARY = "#7c3aed"
HOVER = "#6d28d9"
CARD = "#1e293b"
BG = "#0f172a"

file1 = ""
file2 = ""

# ---------- HASH ----------
def get_md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

# ---------- DROP ----------
def handle_drop(event, num):
    global file1, file2
    path = event.data.strip().replace("{", "").replace("}", "")

    if num == 1:
        file1 = path
        file1_label.configure(text=os.path.basename(path))
        file1_card.configure(border_width=1, border_color=PRIMARY)
    else:
        file2 = path
        file2_label.configure(text=os.path.basename(path))
        file2_card.configure(border_width=1, border_color=PRIMARY)

# ---------- SELECT ----------
def select_file(num):
    path = filedialog.askopenfilename()
    if not path:
        return
    handle_drop(type("e", (), {"data": path}), num)

# ---------- DEMO ----------
def load_demo():
    global file1, file2
    f1 = "collision_files/md5-1.pdf"
    f2 = "collision_files/md5-2.pdf"

    if not os.path.exists(f1) or not os.path.exists(f2):
        status.configure(text="⚠ Demo files missing", text_color="#f59e0b")
        return

    file1 = f1
    file2 = f2

    file1_label.configure(text="Demo File 1")
    file2_label.configure(text="Demo File 2")

# ---------- COMPARE ----------
def compare():
    if not file1 or not file2:
        status.configure(text="⚠ Select both files", text_color="#f59e0b")
        return

    try:
        h1 = get_md5(file1)
        h2 = get_md5(file2)
    except Exception as e:
        status.configure(text=f"❌ {e}", text_color="#ef4444")
        return

    hash1.configure(text=h1)
    hash2.configure(text=h2)

    show_diff()

    if h1 == h2:
        status.configure(text="🚨 Collision Detected", text_color="#ef4444")
    else:
        status.configure(text="✅ No Collision", text_color="#22c55e")

# ---------- DIFF ----------
def show_diff():
    diff_box.delete("1.0", "end")

    try:
        with open(file1, errors="ignore") as f1, open(file2, errors="ignore") as f2:
            diff = list(difflib.ndiff(f1.read().splitlines(), f2.read().splitlines()))

            for line in diff[:200]:
                if line.startswith("+"):
                    diff_box.insert("end", line + "\n", "add")
                elif line.startswith("-"):
                    diff_box.insert("end", line + "\n", "remove")
                else:
                    diff_box.insert("end", line + "\n")

            diff_box.tag_config("add", foreground="#22c55e")
            diff_box.tag_config("remove", foreground="#ef4444")

    except:
        diff_box.insert("end", "Binary files")

# ---------- EXPORT ----------
def export_report():
    if not file1 or not file2:
        return

    with open("report.txt", "w") as f:
        f.write(f"""
File1: {file1}
File2: {file2}

MD5-1: {hash1.cget("text")}
MD5-2: {hash2.cget("text")}
""")

    status.configure(text="📂 Report Saved", text_color=PRIMARY)

# ---------- APP ----------
app = TkinterDnD.Tk()
app.title("MD5 Analyzer")
app.geometry("1200x700")
app.configure(bg=BG)

app.grid_rowconfigure(1, weight=1)
app.grid_columnconfigure(0, weight=1)

# ---------- HEADER ----------
header = ctk.CTkFrame(app, fg_color=BG)
header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20,10))

ctk.CTkLabel(
    header,
    text="🔐  MD5 Collision Analyzer",
    font=ctk.CTkFont(size=26, weight="bold")
).pack(anchor="w")

ctk.CTkLabel(
    header,
    text="Compare files and detect hash collisions",
    text_color="gray"
).pack(anchor="w")

# ---------- BODY ----------
body = ctk.CTkFrame(app, fg_color=BG)
body.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)

body.grid_columnconfigure((0,1), weight=1)
body.grid_rowconfigure(3, weight=1)

# ---------- FILE CARD ----------
def file_card(title):
    frame = ctk.CTkFrame(body, fg_color=CARD, corner_radius=10)

    ctk.CTkLabel(frame, text=title,
                 font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10,5))

    label = ctk.CTkLabel(frame, text="Drop file or browse", text_color="gray")
    label.pack(pady=10)

    btn = ctk.CTkButton(frame, text="Browse",
                        fg_color=PRIMARY,
                        hover_color=HOVER)
    btn.pack(pady=(0,10))

    return frame, label, btn

file1_card, file1_label, btn1 = file_card("File 1")
file1_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

file2_card, file2_label, btn2 = file_card("File 2")
file2_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

btn1.configure(command=lambda: select_file(1))
btn2.configure(command=lambda: select_file(2))

# Drag & Drop
file1_card.drop_target_register(DND_FILES)
file1_card.dnd_bind("<<Drop>>", lambda e: handle_drop(e, 1))

file2_card.drop_target_register(DND_FILES)
file2_card.dnd_bind("<<Drop>>", lambda e: handle_drop(e, 2))

# ---------- BUTTON BAR ----------
btn_frame = ctk.CTkFrame(body, fg_color=BG)
btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

btn_frame.grid_columnconfigure((0,1,2), weight=1)

def action_btn(text, cmd):
    return ctk.CTkButton(btn_frame, text=text,
                         command=cmd,
                         fg_color=PRIMARY,
                         hover_color=HOVER,
                         height=40)

action_btn("Demo", load_demo).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
action_btn("Compare", compare).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
action_btn("Export", export_report).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

# ---------- HASH ----------
def hash_card(title):
    frame = ctk.CTkFrame(body, fg_color=CARD, corner_radius=10)

    ctk.CTkLabel(frame, text=title,
                 font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(10,5))

    label = ctk.CTkLabel(frame, text="—", wraplength=350)
    label.pack(padx=15, pady=10)

    return frame, label

hash1_card, hash1 = hash_card("File 1 Hash")
hash1_card.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

hash2_card, hash2 = hash_card("File 2 Hash")
hash2_card.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

# ---------- DIFF ----------
diff_frame = ctk.CTkFrame(body, fg_color=CARD, corner_radius=10)
diff_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

ctk.CTkLabel(diff_frame, text="Difference",
             font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=10)

diff_box = ctk.CTkTextbox(diff_frame)
diff_box.pack(fill="both", expand=True, padx=10, pady=(0,10))

# ---------- STATUS ----------
status = ctk.CTkLabel(
    app,
    text="",
    font=ctk.CTkFont(size=18, weight="bold")
)
status.grid(row=2, column=0, pady=10)

app.mainloop()
