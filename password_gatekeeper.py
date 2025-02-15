import tkinter as tk
from tkinter import messagebox
import subprocess

def check_password():
    if password_entry.get() == "1234":  # Replace 'your_password' with your actual password
        root.destroy()
        subprocess.run(["python", "test.py"])  # Replace 'your_main_script.py' with the name of your main script
    else:
        messagebox.showerror("Error", "Incorrect password")

root = tk.Tk()
root.title("Password")
root.geometry("300x150")

tk.Label(root, text="Enter Password:").pack()

password_entry = tk.Entry(root, show="*")
password_entry.pack()
password_entry.focus()

submit_button = tk.Button(root, text="Submit", command=check_password)
submit_button.pack()

root.mainloop()
