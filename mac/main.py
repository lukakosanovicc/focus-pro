import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import json
import os, sys

def resource_path(relative_path):
    """
    Get the absolute path to a resource, whether in development or bundled by PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # This is where your added data files (tasks.txt, done.txt) will be
        base_path = sys._MEIPASS
    except AttributeError:
        # If running in a normal Python environment (not bundled),
        # use the current script's directory as the base path.
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class TodoListApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("FocusPro")
        self.geometry("400x400")
        style = Style(theme="flatly")
        style.configure("Custon.TEntry", foreground="gray")

        self.task_input = ttk.Entry(self, font=("TkDefaultFont", 16), width=30, style="Custon.TEntry")
        self.task_input.pack(pady=10)

        self.task_input.insert(0, "Enter your todo here...")

        self.task_input.bind("<FocusIn>", self.clear_placeholder)
        self.task_input.bind("<FocusOut>", self.restore_placeholder)
        
        ttk.Button(self, text="Add", command=self.add_task).pack(pady=5)

        self.task_list = tk.Listbox(self, font=("TkDefaultFont", 16), height=10, selectmode=tk.NONE)
        self.task_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(self, text="Delete All", style="danger.TButton",command=self.delete_all).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(self, text="Delete", style="danger.TButton",command=self.delete_task).pack(side=tk.RIGHT, padx=10, pady=10)
        
        ttk.Button(self, text="Start session", style="info.TButton",command=self.start_session).pack(side=tk.BOTTOM, pady=10)
        
        self.load_tasks()
    
    def start_session(self):
        self.current_task_index = self.get_next_task_index()

        if self.current_task_index is None:
            messagebox.showinfo("Alert", "No tasks to focus on")
            return

        self.focus_win = tk.Toplevel(self)
        self.focus_win.title("Now Focusing")
        self.focus_win.geometry("400x75")
        self.focus_win.attributes("-topmost", True)

        container = ttk.Frame(self.focus_win)
        container.pack(fill="both", expand=True, padx=10, pady=20)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=0)

        self.task_label = ttk.Label(
            container,
            text=self.task_list.get(self.current_task_index),
            font=("TkDefaultFont", 14),
            wraplength=250,
            anchor="w",
            justify="left"
        )
        self.task_label.grid(row=0, column=0, sticky="w")

        done_button = ttk.Button(container, text="Done", command=self.mark_and_next_task)
        done_button.grid(row=0, column=1, sticky="e")

    def get_next_task_index(self):
        if self.task_list.size() > 0:
            return 0
        return None

    def mark_and_next_task(self):
        if self.current_task_index is not None:
            task = self.task_list.get(self.current_task_index)
            index_to_delete = self.current_task_index

            duration_win = tk.Toplevel(self)
            duration_win.title("How long?")
            duration_win.geometry("300x140")
            duration_win.transient(self)
            duration_win.grab_set()
            duration_win.focus_force()

            ttk.Label(duration_win, text=f"Duration for:\n\"{task}\"", justify="center").pack(pady=10)

            duration_entry = ttk.Entry(duration_win, width=30)
            duration_entry.pack(pady=5)
            duration_entry.focus()

            def on_submit_focus_task():
                duration = duration_entry.get().strip()
                result = task

                if duration:
                    result = f"{task} - {duration}"

                try:
                    with open(resource_path("done.txt"), "a") as f:
                        f.write(result + "\n")
                except Exception as e:
                    print("Error writing to file:", e)

                self.task_list.delete(index_to_delete)
                self.save_tasks()

                self.current_task_index = self.get_next_task_index()

                if self.current_task_index is not None:
                    next_task = self.task_list.get(self.current_task_index)
                    self.task_label.config(text=next_task)
                else:
                    self.focus_win.destroy()

                duration_win.destroy()

            ttk.Button(duration_win, text="Submit", command=on_submit_focus_task).pack(pady=10)
            duration_entry.bind("<Return>", lambda e: on_submit_focus_task())

    def add_task(self):
        task = self.task_input.get()
        if task != "Enter your todo here...":
            self.task_list.insert(tk.END, task)
            self.task_input.delete(0, tk.END)
            self.save_tasks()
    
    def delete_task(self):
        task_index = self.task_list.curselection()
        if task_index:
            self.task_list.delete(task_index)
            self.save_tasks()

    def delete_all(self):
        confirm = messagebox.askyesno("Delete All", "Are you sure you want to delete all tasks?")
        if confirm:
            self.task_list.delete(0, tk.END)
            self.save_tasks()
    
    def clear_placeholder(self, event):
        if self.task_input.get() == "Enter your todo here...":
            self.task_input.delete(0, tk.END)
            self.task_input.configure(style="TEntry")

    def restore_placeholder(self, event):
        if self.task_input.get() == "":
            self.task_input.insert(0, "Enter your todo here...")
            self.task_input.configure(style="Custom.TEntry")

    def load_tasks(self):
        try:
            with open(resource_path("tasks.txt"), "r") as f:
                for line in f:
                    task = line.strip()
                    if task:
                        self.task_list.insert(tk.END, task)
        except FileNotFoundError:
            pass
    
    def save_tasks(self):
        with open(resource_path("tasks.txt"), "w") as f:
            for i in range(self.task_list.size()):
                task = self.task_list.get(i)
                f.write(task + "\n")

if __name__ == '__main__':
    app = TodoListApp()
    app.mainloop()
