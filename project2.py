import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime
from tkinter import Tk, Label
from PIL import Image, ImageTk


def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="EmployeeManagement"
    )

def clear_right_frame():
    """Clear all widgets in the right frame."""
    for widget in right_frame.winfo_children():
        widget.destroy()

  
    bg_label = Label(right_frame, image=right_frame_bg_photo)
    bg_label.place(relwidth=1, relheight=1)



def add_employee():
    clear_right_frame()

    tk.Label(right_frame, text="Add Employee", font=("Arial", 16)).pack(pady=10)

    tk.Label(right_frame, text="Name").pack(pady=5)
    entry_name = tk.Entry(right_frame)
    entry_name.pack()
  
    tk.Label(right_frame, text="Designation").pack(pady=5)
    entry_designation = tk.Entry(right_frame)
    entry_designation.pack()

    tk.Label(right_frame, text="Salary/Day").pack(pady=5)
    entry_salary = tk.Entry(right_frame)
    entry_salary.pack()

    def submit():
        name = entry_name.get()
        designation = entry_designation.get()
        salary = entry_salary.get()

        if not (name and designation and salary):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO employees (name, designation, salary_per_day) VALUES (%s, %s, %s)",
                (name, designation, salary),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Employee added successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(right_frame, text="Add Employee", command=submit, bg="lightgreen").pack(pady=10)

def calculate_remaining_salary():
    clear_right_frame()

    tk.Label(right_frame, text="Calculate Remaining Salary", font=("Arial", 16)).pack(pady=10)

    tk.Label(right_frame, text="Employee ID").pack(pady=5)
    entry_calc_emp_id = tk.Entry(right_frame)
    entry_calc_emp_id.pack()

    tk.Label(right_frame, text="Month (MM)").pack(pady=5)
    entry_calc_month = tk.Entry(right_frame)
    entry_calc_month.pack()

    tk.Label(right_frame, text="Year (YYYY)").pack(pady=5)
    entry_calc_year = tk.Entry(right_frame)
    entry_calc_year.pack()

    def submit():
        employee_id = entry_calc_emp_id.get()
        month = entry_calc_month.get()
        year = entry_calc_year.get()

        if not (employee_id and month and year):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            # Calculate total salary
            query_total_salary = """
            SELECT COUNT(a.status) AS days_present, e.salary_per_day
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            WHERE a.employee_id = %s AND MONTH(a.date) = %s AND YEAR(a.date) = %s AND a.status = 'Present'
            """
            cursor.execute(query_total_salary, (employee_id, month, year))
            result = cursor.fetchone()

            if not result or result[0] is None:
                messagebox.showinfo("Remaining Salary", "No attendance records found!")
                return

            days_present, salary_per_day = result
            total_salary = days_present * salary_per_day

            # Calculate payments made
            query_payments = """
            SELECT SUM(amount) FROM salaries
            WHERE employee_id = %s AND MONTH(payment_date) = %s AND YEAR(payment_date) = %s
            """
            cursor.execute(query_payments, (employee_id, month, year))
            total_payments = cursor.fetchone()[0] or 0

            remaining_salary = total_salary - total_payments

            messagebox.showinfo(
                "Remaining Salary",
                f"Total Salary: {total_salary}\nPayments Made: {total_payments}\nRemaining Salary: {remaining_salary}",
            )
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(right_frame, text="Calculate Remaining Salary", command=submit, bg="lightblue").pack(pady=10)

def mark_attendance():
    clear_right_frame()

    tk.Label(right_frame, text="Mark Attendance", font=("Arial", 16)).pack(pady=10)

    tk.Label(right_frame, text="Employee ID").pack(pady=5)
    entry_emp_id = tk.Entry(right_frame)
    entry_emp_id.pack()

    tk.Label(right_frame, text="Status").pack(pady=5)
    combo_status = ttk.Combobox(right_frame, values=["Present", "Absent"])
    combo_status.pack()

    def submit():
        emp_id = entry_emp_id.get()
        status = combo_status.get()
        date = datetime.now().date()

        if not (emp_id and status):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO attendance (employee_id, date, status) VALUES (%s, %s, %s)",
                (emp_id, date, status),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Attendance marked successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(right_frame, text="Mark Attendance", command=submit, bg="lightgreen").pack(pady=10)


def show_data():
    clear_right_frame()

    tk.Label(right_frame, text="Show Data", font=("Arial", 16)).pack(pady=10)

    tk.Label(right_frame, text="Select Table").pack(pady=5)
    combo_table = ttk.Combobox(right_frame, values=["employees", "attendance", "salaries"])
    combo_table.pack()

    def load_data():
        table_name = combo_table.get()
        if not table_name:
            messagebox.showerror("Error", "Please select a table!")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            tree = ttk.Treeview(right_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=100)

            for row in rows:
                tree.insert("", "end", values=row)

            tree.pack(fill="both", expand=True)
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(right_frame, text="Load Data", command=load_data, bg="lightblue").pack(pady=10)


def calculate_salary():
    clear_right_frame()

    tk.Label(right_frame, text="Calculate Salary", font=("Arial", 16)).pack(pady=10)

    tk.Label(right_frame, text="Employee ID").pack(pady=5)
    entry_emp_id = tk.Entry(right_frame)
    entry_emp_id.pack()

    tk.Label(right_frame, text="Month (MM)").pack(pady=5)
    entry_month = tk.Entry(right_frame)
    entry_month.pack()

    tk.Label(right_frame, text="Year (YYYY)").pack(pady=5)
    entry_year = tk.Entry(right_frame)
    entry_year.pack()

    def submit():
        emp_id = entry_emp_id.get()
        month = entry_month.get()
        year = entry_year.get()

        if not (emp_id and month and year):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            query = """
            SELECT e.name, COUNT(a.status) AS days_present, e.salary_per_day
            FROM employees e
            JOIN attendance a ON e.id = a.employee_id
            WHERE e.id = %s AND MONTH(a.date) = %s AND YEAR(a.date) = %s AND a.status = 'Present'
            GROUP BY e.name, e.salary_per_day
            """
            cursor.execute(query, (emp_id, month, year))
            result = cursor.fetchone()

            if result:
                name, days_present, salary_per_day = result
                total_salary = days_present * salary_per_day
                messagebox.showinfo(
                    "Salary Calculation",
                    f"Employee: {name}\nDays Present: {days_present}\n"
                    f"Salary/Day: {salary_per_day}\nTotal Salary: {total_salary}",
                )
            else:
                messagebox.showinfo("Salary Calculation", "No records found!")
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(right_frame, text="Calculate Salary", command=submit, bg="lightgreen").pack(pady=10)

# Add Salary function
def add_salary():
    clear_right_frame()

    tk.Label(right_frame, text="Add Salary", font=("Arial", 16)).pack(pady=10)

    tk.Label(right_frame, text="Employee ID").pack(pady=5)
    entry_salary_emp_id = tk.Entry(right_frame)
    entry_salary_emp_id.pack()

    tk.Label(right_frame, text="Month (MM)").pack(pady=5)
    entry_salary_month = tk.Entry(right_frame)
    entry_salary_month.pack()

    tk.Label(right_frame, text="Year (YYYY)").pack(pady=5)
    entry_salary_year = tk.Entry(right_frame)
    entry_salary_year.pack()

    tk.Label(right_frame, text="Total Salary").pack(pady=5)
    entry_salary_total = tk.Entry(right_frame)
    entry_salary_total.pack()

    tk.Label(right_frame, text="Amount").pack(pady=5)
    entry_salary_amount = tk.Entry(right_frame)
    entry_salary_amount.pack()

    tk.Label(right_frame, text="Payment Date").pack(pady=5)
    entry_salary_payment_date = tk.Entry(right_frame)
    entry_salary_payment_date.pack()

# Set the default date

    def set_today_date():
        today = datetime.today().date()
        entry_salary_payment_date.delete(0, tk.END)
        entry_salary_payment_date.insert(0, today)

    set_today_date()  
    def submit():
        emp_id = entry_salary_emp_id.get()
        month = entry_salary_month.get()
        year = entry_salary_year.get()
        total_salary = entry_salary_total.get()
        amount = entry_salary_amount.get()
        payment_date = entry_salary_payment_date.get()

        if not (emp_id and month and year and total_salary and amount and payment_date):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO salaries (employee_id, month, year, total_salary, amount, payment_date) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (emp_id, month, year, total_salary, amount, payment_date),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Salary added successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(right_frame, text="Add Salary", command=submit, bg="lightgreen").pack(pady=10)
    
#  Edit and Delete 
def edit_or_delete_data():
    clear_right_frame()

    tk.Label(right_frame, text="Edit or Delete Data", font=("Arial", 16)).pack(pady=10)

    tk.Label(right_frame, text="Select Table").pack(pady=5)
    combo_table = ttk.Combobox(right_frame, values=["employees", "attendance", "salaries"], state="readonly")
    combo_table.pack()

    def load_data():
        table_name = combo_table.get()
        if not table_name:
            messagebox.showerror("Error", "Please select a table!")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            tree = ttk.Treeview(right_frame, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=100)

            for row in rows:
                tree.insert("", "end", values=row)

            tree.pack(fill="both", expand=True)
            conn.close()

            # Add Edit and Delete Buttons
            def edit_selected():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showerror("Error", "Please select a row to edit!")
                    return

                values = tree.item(selected_item, 'values')
                edit_record(table_name, columns, values)

            def delete_selected():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showerror("Error", "Please select a row to delete!")
                    return

                values = tree.item(selected_item, 'values')
                confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
                if confirm:
                    delete_record(table_name, columns[0], values[0])

            tk.Button(right_frame, text="Edit Selected", command=edit_selected, bg="lightgreen").pack(pady=5)
            tk.Button(right_frame, text="Delete Selected", command=delete_selected, bg="red").pack(pady=5)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(right_frame, text="Load Data", command=load_data, bg="lightblue").pack(pady=10)

def edit_record(table_name, columns, values):
    clear_right_frame()

    tk.Label(right_frame, text=f"Edit Record in {table_name}", font=("Arial", 16)).pack(pady=10)

    entries = []
    for col, val in zip(columns, values):
        tk.Label(right_frame, text=col).pack(pady=5)
        entry = tk.Entry(right_frame)
        entry.insert(0, val)
        entry.pack()
        entries.append(entry)

    def submit():
        updated_values = [entry.get() for entry in entries]
        set_clause = ", ".join([f"{col} = %s" for col in columns[1:]])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]} = %s"

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(query, updated_values[1:] + [updated_values[0]])
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Record updated successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(right_frame, text="Save Changes", command=submit, bg="lightgreen").pack(pady=10)

def delete_record(table_name, primary_key_column, primary_key_value):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        query = f"DELETE FROM {table_name} WHERE {primary_key_column} = %s"
        cursor.execute(query, (primary_key_value,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Record deleted successfully!")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# Add "Edit/Delete Data" button to the menu



# GUI Setup
root = tk.Tk()
root.title("Employee Attendance & Salary Management")
root.geometry("800x800")

    # Add the logo icon
try:
        root.iconbitmap("D:\\spLogo.ico")  
except Exception as e:
        print(f"Error setting icon: {e}")


# Left Frame (Menu)
left_frame = tk.Frame(root, bg="lightblue", width=200)
left_frame.pack(side="left", fill="y")
left_frame.pack_propagate(False)

menu_buttons = [
    ("Add Employee", add_employee),
    ("Mark Attendance", mark_attendance),
    ("Show Data", show_data),
    ("Calculate Salary", calculate_salary),
    ("Add Salary", add_salary),
    ("Calculate Remaining Salary", calculate_remaining_salary),
    ("Edit/Delete Data", edit_or_delete_data)  
]

tk.Label(left_frame, text="Menu", font=("Arial", 18), bg="lightblue").pack(pady=10)

for text, command in menu_buttons:
    tk.Button(left_frame, text=text, command=command, width=20).pack(pady=5)

# Right Frame (Content Display)
right_frame = tk.Frame(root, bg="white")
right_frame.pack(side="left", fill="both", expand=True)
#  background image
right_frame_bg_image = Image.open("Colourful Simple.png")  
right_frame_bg_image_resized = right_frame_bg_image.resize((700, 700))  # Adjust size 
right_frame_bg_photo = ImageTk.PhotoImage(right_frame_bg_image_resized)

# Initialize the right frame background image
bg_label = Label(right_frame, image=right_frame_bg_photo)
bg_label.place(relwidth=1, relheight=1)

root.mainloop()
