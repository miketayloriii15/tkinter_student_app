from tkinter import *
from tkinter import ttk, messagebox
import psycopg2

# Replace these with environment variables or a config file in production
DB_NAME = "your_database_name"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"

def run_query(query, parameters=()):
    """Executes a SQL query with optional parameters."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    result = None
    try:
        cur.execute(query, parameters)
        if query.strip().lower().startswith("select"):
            result = cur.fetchall()
        conn.commit()
    except psycopg2.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        cur.close()
        conn.close()
    return result

def refresh_treeview():
    """Clears and repopulates the treeview with student records."""
    for item in tree.get_children():
        tree.delete(item)
    records = run_query("SELECT * FROM students;")
    if records:
        for record in records:
            tree.insert('', END, values=record)

def insert_data():
    """Adds a new student to the database."""
    query = """
        INSERT INTO students(name, address, age, number)
        VALUES (%s, %s, %s, %s)
    """
    parameters = (
        name_entry.get(),
        address_entry.get(),
        age_entry.get(),
        phone_entry.get()
    )
    run_query(query, parameters)
    messagebox.showinfo("Information", "Data inserted successfully")
    refresh_treeview()

def delete_data():
    """Removes the selected student record from the database."""
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("Warning", "Please select a record to delete.")
        return
    student_id = tree.item(selected_items[0])['values'][0]
    run_query("DELETE FROM students WHERE student_id = %s", (student_id,))
    messagebox.showinfo("Information", "Data deleted successfully")
    refresh_treeview()

def update_data():
    """Updates the selected student's information in the database."""
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("Warning", "Please select a record to update.")
        return
    student_id = tree.item(selected_items[0])['values'][0]
    query = """
        UPDATE students
        SET name = %s, address = %s, age = %s, number = %s
        WHERE student_id = %s
    """
    parameters = (
        name_entry.get(),
        address_entry.get(),
        age_entry.get(),
        phone_entry.get(),
        student_id
    )
    run_query(query, parameters)
    messagebox.showinfo("Information", "Data updated successfully")
    refresh_treeview()

def create_table():
    """Creates the students table in the database if it doesn't already exist."""
    query = """
        CREATE TABLE IF NOT EXISTS students (
            student_id serial PRIMARY KEY,
            name text,
            address text,
            age int,
            number text
        );
    """
    run_query(query)
    messagebox.showinfo("Information", "Table created successfully")
    refresh_treeview()

# ---------------- UI SETUP ---------------- #

root = Tk()
root.title("Student Management System")

# Entry fields container
frame = LabelFrame(root, text="Student Data")
frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

Label(frame, text="Name:").grid(row=0, column=0, padx=2, sticky="w")
name_entry = Entry(frame)
name_entry.grid(row=0, column=1, pady=2, sticky="ew")

Label(frame, text="Address:").grid(row=1, column=0, padx=2, sticky="w")
address_entry = Entry(frame)
address_entry.grid(row=1, column=1, pady=2, sticky="ew")

Label(frame, text="Age:").grid(row=2, column=0, padx=2, sticky="w")
age_entry = Entry(frame)
age_entry.grid(row=2, column=1, pady=2, sticky="ew")

Label(frame, text="Phone Number:").grid(row=3, column=0, padx=2, sticky="w")
phone_entry = Entry(frame)
phone_entry.grid(row=3, column=1, pady=2, sticky="ew")

# Button section
button_frame = Frame(root)
button_frame.grid(row=1, column=0, pady=5, sticky="ew")

Button(button_frame, text="Create Table", command=create_table).grid(row=0, column=0, padx=5)
Button(button_frame, text="Add Data", command=insert_data).grid(row=0, column=1, padx=5)
Button(button_frame, text="Update Data", command=update_data).grid(row=0, column=2, padx=5)
Button(button_frame, text="Delete Data", command=delete_data).grid(row=0, column=3, padx=5)

# Treeview container
tree_frame = Frame(root)
tree_frame.grid(row=2, column=0, padx=10, sticky="nsew")

tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)

# Treeview setup
tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="browse")
tree.pack()
tree_scroll.config(command=tree.yview)

tree['columns'] = ("student_id", "name", "address", "age", "number")
tree.column("#0", width=0, stretch=NO)
tree.column("student_id", anchor=CENTER, width=80)
tree.column("name", anchor=CENTER, width=120)
tree.column("address", anchor=CENTER, width=120)
tree.column("age", anchor=CENTER, width=50)
tree.column("number", anchor=CENTER, width=120)

tree.heading("student_id", text="ID", anchor=CENTER)
tree.heading("name", text="Name", anchor=CENTER)
tree.heading("address", text="Address", anchor=CENTER)
tree.heading("age", text="Age", anchor=CENTER)
tree.heading("number", text="Phone Number", anchor=CENTER)

# Initial data load
refresh_treeview()

# Launch the app
root.mainloop()
