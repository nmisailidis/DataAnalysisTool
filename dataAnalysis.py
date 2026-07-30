import pandas as pd
import tkinter as tk
from tkinter import ttk
import sqlite3
import database as db

selected_columns = []
selected_var = []
source = ""
columns = None


def on_click_create_columns():

    selected_index = columns.current()

    if selected_index == -1:
        status_label.config(text="⚠️ Please select a sorting column!", foreground="#dc2626")
        return

    selected = list_of_columns[selected_index]

    for i in range(len(selected_var)):
        if selected_var[i].get() == 1:
            selected_columns.append(list_of_columns[i])

    if not selected_columns:
        status_label.config(text="⚠️ Please check at least one column box!", foreground="#dc2626")
        return

    try:
        data = pd.read_excel(source)

        category_summary = data.groupby(selected)[selected_columns].sum()

        try:
            f = open("Report.txt", "x")
        except FileExistsError:
            with open("Report.txt", "a") as f:
                f.write("\n--- Σύνοψη ανά Κατηγορία Προϊόντων ---\n")
                f.write(str(category_summary))

            with open("Report.txt") as f:
                print(f.read())
    except Exception as e:
        status_label.config(text=f"❌ Error generating report: {e}", foreground="#dc2626")


def on_click_analysis():

    global source, columns, selected_var, list_of_columns

    if source_entry.get().strip().startswith("https"):
        source = source_entry.get()
        source_list = source.split("/")
        source_list[-1] = "export?format=xlsx"
        delimeter = "/"
        source = delimeter.join(source_list)
        print(source)
    else:
        source = source_entry.get()

    try:
        data = pd.read_excel(source)
        list_of_columns = list(data.columns)
        conn = sqlite3.connect("data_analysis.db")
        db.init_db()
        db.save_dataset(conn, source, "local", data)
    except Exception as e:
        status_label.config(text=f"❌ Error reading file: {e}", foreground="#dc2626")
        return

    status_label.config(text="Excel loaded successfully. Setup your criteria below.", foreground="#4b5563")

    for widget in root.winfo_children():
        widget.destroy()

    pick_criteria_label = ttk.Label(
        root,
        text="Pick the main sorting column:",
        font=("Segoe UI", 11, "bold")
    )
    pick_criteria_label.pack(anchor="w", pady=(10, 5))

    columns = ttk.Combobox(root, values=list_of_columns, state="readonly")
    columns.pack(anchor="w", pady=(0, 15))

    checkbox_label = ttk.Label(
        root,
        text="Select metrics to sum up:",
        font=("Segoe UI", 11, "bold")
    )
    checkbox_label.pack(anchor="w", pady=(0, 5))

    selected_var = []

    checkbox_container = tk.Frame(root, bg="#ffffff", bd=1, relief="solid", highlightthickness=0)
    checkbox_container.config(bg="#f4f6f9")  # subtle separation boundary
    checkbox_container.pack(fill="x", pady=(0, 20), ipady=5, ipadx=5)

    for i in range(len(list_of_columns)):
        selected_var.append(tk.IntVar())

        selected_check = tk.Checkbutton(
            checkbox_container,
            text=list_of_columns[i],
            variable=selected_var[i],
            onvalue=1,
            offvalue=0,
            bg="#ffffff",
            activebackground="#ffffff",
            fg="#1f2937",
            font=("Segoe UI", 10)
        )
        selected_check.pack(anchor="w", padx=10, pady=2)

    create_list_button = ttk.Button(root, text="Generate Report!", width=10, command=on_click_create_columns)
    create_list_button.pack(fill="x", ipady=4)


def show_history_window():
    conn = sqlite3.connect("data_analysis.db")
    datasets = db.get_all_datasets(conn)
    conn.close()

    history_win = tk.Toplevel(root)
    history_win.title("Dataset History")
    history_win.geometry("600x400")

    label = ttk.Label(history_win, text="Double-click a dataset to view its records:",
                        font=("Segoe UI", 10, "bold"))
    label.pack(anchor="w", padx=10, pady=(10, 5))

    tree = ttk.Treeview(history_win, columns=("filename", "source", "date"), show="headings")
    tree.heading("filename", text="Filename")
    tree.heading("source", text="Source")
    tree.heading("date", text="Imported At")
    tree.column("filename", width=250)
    tree.column("source", width=100)
    tree.column("date", width=180)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    for row in datasets:
        dataset_id, filename, source_type, imported_at = row
        tree.insert("", "end", iid=dataset_id, values=(filename, source_type, imported_at))

    def on_double_click(event):
        selected_item = tree.selection()
        if selected_item:
            dataset_id = selected_item[0]
            show_records_window(dataset_id)

    tree.bind("<Double-1>", on_double_click)


def show_records_window(dataset_id):
    conn = sqlite3.connect("data_analysis.db")
    records = db.get_records_for_dataset(conn, dataset_id)
    conn.close()

    records_win = tk.Toplevel(root)
    records_win.title(f"Records — Dataset {dataset_id}")
    records_win.geometry("700x450")

    if not records:
        ttk.Label(records_win, text="No records found.").pack(pady=20)
        return

    columns = list(records[0].keys())

    tree = ttk.Treeview(records_win, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    for record in records:
        values = [record.get(col, "") for col in columns]
        tree.insert("", "end", values=values)

    """
    The list with the left-one columns will be printed,
    so the user will pick the columns they would like to participate 
    in the results
    """

    """
    The selected columns will be added in a list
    """


root = tk.Tk()
root.title("Excel Analysis App")
root.geometry("650x650")
root.configure(bg="#f0f2f5") # Clean, light-grey background

# Initialize Style
style = ttk.Style()
style.theme_use("clam")

# Configure custom styles
style.configure("TLabel", background="#f0f2f5", foreground="#333333", font=("Segoe UI", 11))
style.configure("TButton", background="#0078d4", foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0)
style.map("TButton", background=[("active", "#005a9e")]) # Hover effect

top_frame = tk.Frame(root, bg="#f4f6f9", padx=20, pady=20)
top_frame.pack(fill="x")

# Usage
label = ttk.Label(root, text="Type the path of the source:")
label.pack(pady=(20, 5))

source_entry = ttk.Entry(root, width=40)
source_entry.pack(pady=5)

sourceButton = ttk.Button(root, text="Analysis", command=on_click_analysis)
sourceButton.pack(pady=15)

history_button = ttk.Button(root, text="View History", command=show_history_window)
history_button.pack(pady=5)

status_label = ttk.Label(top_frame, text="Awaiting data source asset...", foreground="#4b5563", font=("Segoe UI", 9, "italic"))
status_label.pack(anchor="w", pady=(10, 0))

root.mainloop()

