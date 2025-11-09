import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import numpy as np
import colorsys

# --------- Corrected Matplotlib Imports ---------
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt  # Only needed for colormaps

# ---------------- PREDECLARE GUI VARIABLES ----------------
name_entry = None
class_entry = None
student_combo = None
marks_table = None
stats_label = None
chart_frame = None
header_canvas = None
input_frame = None
marks_frame = None
view_frame = None
stats_frame = None
mode_button = None
current_colors = {}
dark_mode = False

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT NOT NULL,
            score REAL NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    """)
    conn.commit()
    conn.close()

# ---------------- FUNCTIONS ----------------
def add_student():
    name = name_entry.get().strip()
    student_class = class_entry.get().strip()
    if not name or not student_class:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO students (name, class) VALUES (?, ?)", (name, student_class))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Student '{name}' added successfully!")
    name_entry.delete(0, tk.END)
    class_entry.delete(0, tk.END)
    load_students()
    load_marks_table()

def add_marks():
    selected = student_combo.get()
    if " - " not in selected:
        messagebox.showwarning("Input Error", "Please select a student.")
        return
    student_id = selected.split(" - ")[0]
    subject = subject_entry.get().strip()
    score = score_entry.get().strip()
    if not subject or not score:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return
    try:
        score = float(score)
    except ValueError:
        messagebox.showerror("Invalid Input", "Score must be numeric.")
        return

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO marks (student_id, subject, score) VALUES (?, ?, ?)", (student_id, subject, score))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Marks added successfully!")
    subject_entry.delete(0, tk.END)
    score_entry.delete(0, tk.END)
    load_marks_table()

def load_students():
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    cur.execute("SELECT student_id, name FROM students")
    students = cur.fetchall()
    conn.close()
    student_combo['values'] = [f"{s[0]} - {s[1]}" for s in students]

def load_marks_table():
    for row in marks_table.get_children():
        marks_table.delete(row)
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT s.name, s.class, m.subject, m.score
        FROM marks m
        JOIN students s ON s.student_id = m.student_id
        ORDER BY s.name
    """)
    rows = cur.fetchall()
    conn.close()
    for row in rows:
        marks_table.insert("", "end", values=row)

def calculate_stats():
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    cur.execute("SELECT score FROM marks")
    scores = [row[0] for row in cur.fetchall()]
    conn.close()
    if not scores:
        messagebox.showinfo("No Data", "No marks found.")
        return
    avg, med, max_s, min_s = np.mean(scores), np.median(scores), np.max(scores), np.min(scores)
    stats_label.config(
        text=f"✨ Class Statistics ✨\nAverage: {avg:.2f}\nMedian: {med:.2f}\nHighest: {max_s:.2f}\nLowest: {min_s:.2f}"
    )

# ---------------- FIXED VISUALIZATION FUNCTIONS ----------------
def visualize_bar_chart():
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT s.name, AVG(m.score)
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.student_id
    """)
    data = cur.fetchall()
    conn.close()
    
    if not data:
        messagebox.showinfo("No Data", "No marks available for visualization.")
        return

    names, avgs = zip(*data)
    colors = plt.cm.Pastel2(np.linspace(0, 1, len(names)))

    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(names, avgs, color=colors)
    ax.set_title("Average Marks per Student", fontsize=14)
    ax.set_ylabel("Average Score")
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()
    update_chart(fig)

def visualize_pie_chart():
    selected = student_combo.get()
    if " - " not in selected:
        messagebox.showwarning("Input Error", "Please select a student.")
        return
    student_id = selected.split(" - ")[0]
    
    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    cur.execute("SELECT subject, score FROM marks WHERE student_id = ?", (student_id,))
    data = cur.fetchall()
    conn.close()
    
    if not data:
        messagebox.showinfo("No Data", "No marks found for this student.")
        return

    subjects, scores = zip(*data)
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(subjects)))

    fig = Figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.pie(scores, labels=subjects, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.set_title(f"{selected.split(' - ')[1]}'s Performance", fontsize=14)
    fig.tight_layout()
    update_chart(fig)

def update_chart(fig):
    # Clear previous chart
    for widget in chart_frame.winfo_children():
        widget.destroy()
    
    # Embed figure in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def clear_chart():
    for widget in chart_frame.winfo_children():
        widget.destroy()
    stats_label.config(text="✨ Stats will appear here ✨")

# ---------------- THEME SYSTEM ----------------
light_colors = {"bg": "#F8FAFC", "fg": "#000000", "frame": "#E3F2FD"}
dark_colors = {"bg": "#1E1E1E", "fg": "#FFFFFF", "frame": "#2E2E2E"}
current_colors = light_colors.copy()

def toggle_theme():
    global dark_mode, current_colors
    dark_mode = not dark_mode
    current_colors = dark_colors if dark_mode else light_colors
    apply_theme()

def apply_theme():
    root.config(bg=current_colors["bg"])
    header_canvas.config(bg=current_colors["bg"])
    for frame in [input_frame, marks_frame, view_frame, stats_frame]:
        frame.config(bg=current_colors["frame"], fg=current_colors["fg"])
        for child in frame.winfo_children():
            try:
                child.config(bg=current_colors["frame"], fg=current_colors["fg"])
            except:
                pass
    stats_label.config(bg=current_colors["frame"], fg=current_colors["fg"])
    chart_frame.config(bg=current_colors["frame"])
    mode_button.config(
        text="☀️ Light Mode" if dark_mode else "🌙 Dark Mode",
        bg="#333333" if dark_mode else "#E0E0E0",
        fg=current_colors["fg"]
    )

# ---------------- GUI SETUP ----------------
root = tk.Tk()
root.title("🌸 Student Marks Analyzer")
root.geometry("980x820")
root.configure(bg=current_colors["bg"])

header_canvas = tk.Canvas(root, height=80, bd=0, highlightthickness=0)
header_canvas.pack(fill="x")

def draw_gradient():
    width = root.winfo_width()
    gradient = header_canvas
    gradient.delete("all")
    for i in range(width):
        r, g, b = colorsys.hsv_to_rgb(i / width, 0.3, 1)
        color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        gradient.create_line(i, 0, i, 80, fill=color)
    gradient.create_text(width / 2, 40, text=" Student Marks Analyzer ", fill="white", font=("Helvetica", 20, "bold"))
    root.after(50, draw_gradient)
root.after(100, draw_gradient)

# ---------- Frames and GUI elements ----------
input_frame = tk.LabelFrame(root, text="Add Student", padx=10, pady=10, bg=current_colors["frame"], font=("Arial", 12, "bold"))
input_frame.pack(fill="x", padx=15, pady=8)
marks_frame = tk.LabelFrame(root, text="Add Marks", padx=10, pady=10, bg=current_colors["frame"], font=("Arial", 12, "bold"))
marks_frame.pack(fill="x", padx=15, pady=8)
view_frame = tk.LabelFrame(root, text="View Marks", padx=10, pady=10, bg=current_colors["frame"], font=("Arial", 12, "bold"))
view_frame.pack(fill="both", expand=True, padx=15, pady=8)
stats_frame = tk.LabelFrame(root, text="Statistics & Charts", padx=10, pady=10, bg=current_colors["frame"], font=("Arial", 12, "bold"))
stats_frame.pack(fill="both", expand=True, padx=15, pady=8)

# ---------- Input Section ----------
tk.Label(input_frame, text="Name:", bg=current_colors["frame"]).grid(row=0, column=0, padx=5)
name_entry = tk.Entry(input_frame)
name_entry.grid(row=0, column=1, padx=5)
tk.Label(input_frame, text="Class:", bg=current_colors["frame"]).grid(row=0, column=2, padx=5)
class_entry = tk.Entry(input_frame)
class_entry.grid(row=0, column=3, padx=5)
tk.Button(input_frame, text="Add Student", command=add_student, bg="#90CAF9", fg="black", relief="flat").grid(row=0, column=4, padx=10)

# ---------- Marks Section ----------
tk.Label(marks_frame, text="Student:", bg=current_colors["frame"]).grid(row=0, column=0, padx=5)
student_combo = ttk.Combobox(marks_frame, width=25)
student_combo.grid(row=0, column=1, padx=5)
tk.Label(marks_frame, text="Subject:", bg=current_colors["frame"]).grid(row=0, column=2, padx=5)
subject_entry = tk.Entry(marks_frame)
subject_entry.grid(row=0, column=3, padx=5)
tk.Label(marks_frame, text="Score:", bg=current_colors["frame"]).grid(row=0, column=4, padx=5)
score_entry = tk.Entry(marks_frame)
score_entry.grid(row=0, column=5, padx=5)
tk.Button(marks_frame, text="Add Marks", command=add_marks, bg="#FFCC80", fg="black", relief="flat").grid(row=0, column=6, padx=10)

# ---------- Table Section ----------
columns = ("Name", "Class", "Subject", "Score")
marks_table = ttk.Treeview(view_frame, columns=columns, show="headings")
for col in columns:
    marks_table.heading(col, text=col)
    marks_table.column(col, width=180)
marks_table.pack(fill="both", expand=True)

# ---------- Stats and Charts ----------
tk.Button(stats_frame, text="Calculate Stats", command=calculate_stats, bg="#CE93D8", relief="flat").pack(pady=5)
stats_label = tk.Label(stats_frame, text="✨ Stats will appear here ✨", bg=current_colors["frame"], font=("Arial", 11))
stats_label.pack()
btn_frame = tk.Frame(stats_frame, bg=current_colors["frame"])
btn_frame.pack(pady=5)
tk.Button(btn_frame, text="📊 Bar Chart", command=visualize_bar_chart, bg="#B39DDB", relief="flat").grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="🥧 Pie Chart", command=visualize_pie_chart, bg="#B39DDB", relief="flat").grid(row=0, column=1, padx=10)
tk.Button(btn_frame, text=" Clear Chart", command=clear_chart, bg="#FFAB91", relief="flat").grid(row=0, column=2, padx=10)
tk.Button(btn_frame, text="🗂 View Database", command=lambda: view_database_window(), bg="#AED581", relief="flat").grid(row=0, column=3, padx=10)
chart_frame = tk.Frame(stats_frame, bg=current_colors["frame"])
chart_frame.pack(fill="both", expand=True)

# ---------- Theme Toggle ----------
mode_button = tk.Button(root, text="🌙 Dark Mode", command=toggle_theme, bg="#E0E0E0", relief="flat")
mode_button.pack(pady=5)

# ---------------- Database Viewer Function ----------------
def view_database_window():
    win = tk.Toplevel(root)
    win.title("📋 Database Viewer")
    win.geometry("500x400")
    win.configure(bg=current_colors["bg"])

    conn = sqlite3.connect("students.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT s.name, s.class, m.subject, m.score
        FROM marks m
        JOIN students s ON s.student_id = m.student_id
    """)
    data = cur.fetchall()
    conn.close()

    tree = ttk.Treeview(win, columns=("Name", "Class", "Subject", "Score"), show="headings")
    for col in ("Name", "Class", "Subject", "Score"):
        tree.heading(col, text=col)
        tree.column(col, width=100)
    for row in data:
        tree.insert("", "end", values=row)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

# ---------------- Initialize ----------------
init_db()
load_students()
load_marks_table()
apply_theme()
root.mainloop()
