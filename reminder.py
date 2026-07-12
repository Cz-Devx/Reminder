import tkinter as tk
from tkinter import ttk, messagebox
from plyer import notification
import threading
import time
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# --- Theme Configurations ---
THEMES = {
    "light": {
        "bg": "#F3F3F3",          # Main canvas background
        "card_bg": "#FFFFFF",     # Interactive card background
        "fg_main": "#242424",     # Primary text
        "fg_muted": "#555555",    # Labels / muted text
        "input_bg": "#FAFAFA",    # Input fields background
        "border": "#E5E5E5",      # Subtle borders
        "list_select": "#EFF6FC", # Highlight color for list selection
        "toggle_btn": "#E5E5E5",  # Theme button color
        "toggle_fg": "#242424"
    },
    "dark": {
        "bg": "#1F1F1F",          # Dark canvas background
        "card_bg": "#2D2D2D",     # Dark card container
        "fg_main": "#FFFFFF",     # Bright primary text
        "fg_muted": "#AAAAAA",    # Lighter gray for labels
        "input_bg": "#3B3B3B",    # Dark input fields
        "border": "#3F3F3F",      # Dark border accents
        "list_select": "#353535", # Dark selection highlight
        "toggle_btn": "#3B3B3B",  # Dark button background
        "toggle_fg": "#FFFFFF"
    }
}

current_theme = "light"

def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()

def apply_theme():
    colors = THEMES[current_theme]
    
    # Update main windows & frames
    root.configure(bg=colors["bg"])
    header_frame.configure(bg=colors["bg"])
    card.configure(bg=colors["card_bg"], highlightbackground=colors["border"])
    list_frame.configure(bg=colors["card_bg"], highlightbackground=colors["border"])
    
    # Update Labels (using config dynamically for basic labels)
    title_label.configure(background=colors["bg"], foreground=colors["fg_main"])
    active_title_label.configure(background=colors["bg"], foreground=colors["fg_main"])
    
    label_task.configure(bg=colors["card_bg"], fg=colors["fg_muted"])
    label_time.configure(bg=colors["card_bg"], fg=colors["fg_muted"])
    
    # Update Inputs
    task_entry.configure(bg=colors["input_bg"], fg=colors["fg_main"], highlightbackground=colors["border"])
    time_entry.configure(bg=colors["input_bg"], fg=colors["fg_main"], highlightbackground=colors["border"])
    
    # Update Listbox
    active_listbox.configure(bg=colors["card_bg"], fg=colors["fg_main"], selectbackground=colors["list_select"])
    
    # Update Toggle Button text/style
    theme_text = "🌙 Dark Mode" if current_theme == "light" else "☀️ Light Mode"
    theme_button.configure(text=theme_text, bg=colors["toggle_btn"], fg=colors["toggle_fg"])

# --- Tray Icon Setup ---
tray_icon = None

def create_dummy_icon():
    img = Image.new('RGB', (64, 64), color='#0078D4')
    d = ImageDraw.Draw(img)
    d.rectangle([20, 20, 44, 44], fill="white")
    return img

def show_window(icon, item):
    global tray_icon
    if tray_icon:
        tray_icon.stop()
    root.after(0, root.deiconify)

def quit_app(icon, item):
    global tray_icon
    if tray_icon:
        tray_icon.stop()
    root.quit()

def minimize_to_tray():
    global tray_icon
    root.withdraw()
    menu = (item('Open To Do', show_window, default=True), item('Exit App', quit_app))
    tray_icon = pystray.Icon("ToDoReminder", create_dummy_icon(), "My To-Do Reminders", menu)
    threading.Thread(target=tray_icon.run, daemon=True).start()

# --- Core Reminder Logic ---
def schedule_reminder():
    task = task_entry.get().strip()
    time_str = time_entry.get().strip()

    if not task or not time_str:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    try:
        minutes = float(time_str)
        if minutes <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number of minutes.")
        return

    task_entry.delete(0, tk.END)
    time_entry.delete(0, tk.END)

    reminder_id = f"{task} ({minutes}m)"
    active_listbox.insert(tk.END, f"⏳ {reminder_id}")

    seconds = minutes * 60
    threading.Thread(target=background_timer, args=(task, seconds, reminder_id), daemon=True).start()

def background_timer(task, seconds, reminder_id):
    time.sleep(seconds)
    notification.notify(
        title="Microsoft To-Do",
        message=task,
        app_name="To-Do Reminder",
        timeout=10
    )
    root.after(0, remove_from_list, reminder_id)

def remove_from_list(reminder_id):
    items = active_listbox.get(0, tk.END)
    for index, item_str in enumerate(items):
        if reminder_id in item_str:
            active_listbox.delete(index)
            break

# --- Modern UI Setup ---
root = tk.Tk()
root.title("To Do")
root.geometry("400x520")

# Intercept the 'X' button
root.protocol('WM_DELETE_WINDOW', minimize_to_tray)

# Header Frame (Houses Title + Theme Toggle)
header_frame = tk.Frame(root)
header_frame.pack(fill="x", padx=25, pady=(25, 15))

title_label = tk.Label(header_frame, text="🔔 My Reminders", font=("Segoe UI Semibold", 16))
title_label.pack(side="left")

theme_button = tk.Button(header_frame, text="🌙 Dark Mode", command=toggle_theme, font=("Segoe UI", 9), bd=0, padx=10, pady=4, cursor="hand2")
theme_button.pack(side="right")

# Main Input Card
card = tk.Frame(root, bd=0, highlightthickness=1)
card.pack(fill="x", padx=25, pady=10)

label_task = tk.Label(card, text="What needs to be done?", font=("Segoe UI", 9, "bold"))
label_task.pack(anchor="w", padx=15, pady=(15, 2))

task_entry = tk.Entry(card, font=("Segoe UI", 11), bd=0, highlightthickness=1, insertbackground="#0078D4")
task_entry.pack(fill="x", padx=15, pady=(0, 10), ipady=6)

label_time = tk.Label(card, text="Remind me in (minutes)", font=("Segoe UI", 9, "bold"))
label_time.pack(anchor="w", padx=15, pady=(5, 2))

time_entry = tk.Entry(card, font=("Segoe UI", 11), bd=0, highlightthickness=1, insertbackground="#0078D4")
time_entry.pack(fill="x", padx=15, pady=(0, 15), ipady=6)

# Windows Blue Button
add_button = tk.Button(card, text="+ Add Reminder", command=schedule_reminder, bg="#0078D4", fg="white", font=("Segoe UI Semibold", 10), bd=0, activebackground="#005A9E", activeforeground="white", cursor="hand2")
add_button.pack(fill="x", padx=15, pady=(0, 15), ipady=6)

# Active Tasks Section
active_title_label = tk.Label(root, text="Active Reminders", font=("Segoe UI Semibold", 11))
active_title_label.pack(anchor="w", padx=25, pady=(20, 5))

list_frame = tk.Frame(root, bd=0, highlightthickness=1)
list_frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))

active_listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), bd=0, highlightthickness=0, selectforeground="#0078D4")
active_listbox.pack(fill="both", expand=True, padx=10, pady=10)

# Apply default Light theme values on launch
apply_theme()

root.mainloop()