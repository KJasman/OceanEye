## Create .EXE: Need windows environment
import tkinter as tk
from tkinter import messagebox
import subprocess

def run_setup():
    try:
        subprocess.run(["setup.bat"], check=True)
        messagebox.showinfo("Success", "Setup completed successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Setup failed: {e}")

def run_app():
    try:
        subprocess.run(["run.bat"], check=True)
        messagebox.showinfo("Success", "Application is running.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Application failed to start: {e}")

root = tk.Tk()
root.title("Application Launcher")

setup_button = tk.Button(root, text="Setup Environment", command=run_setup)
setup_button.pack(pady=10)

run_button = tk.Button(root, text="Run Application", command=run_app)
run_button.pack(pady=10)

root.mainloop()
