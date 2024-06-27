import tkinter as tk
from tkinter import messagebox
import sqlite3
from sqlite3 import Error
import bcrypt
import pandas as pd

# Database setup
database = "inventory.db"

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file} successfully.")
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    try:
        sql_create_users_table = """CREATE TABLE IF NOT EXISTS users (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        username TEXT NOT NULL UNIQUE,
                                        password TEXT NOT NULL
                                    );"""

        sql_create_products_table = """CREATE TABLE IF NOT EXISTS products (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        name TEXT NOT NULL,
                                        quantity INTEGER NOT NULL,
                                        price REAL NOT NULL
                                    );"""

        conn.execute(sql_create_users_table)
        conn.execute(sql_create_products_table)
        print("Tables created successfully.")
    except Error as e:
        print(e)

conn = create_connection(database)
if conn is not None:
    create_tables(conn)
    conn.close()

# User authentication functions
def register_user(username, password):
    conn = create_connection(database)
    if conn is not None:
        cursor = conn.cursor()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            print("User registered successfully.")
            messagebox.showinfo("Success", "User registered successfully.")
        except Error as e:
            print(e)
            messagebox.showerror("Error", "User registration failed.")
        finally:
            conn.close()

def login_user(username, password):
    conn = create_connection(database)
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row and bcrypt.checkpw(password.encode('utf-8'), row[0]):
            print("Login successful.")
            return True
        else:
            print("Invalid username or password.")
            return False

def add_product(name, quantity, price):
    conn = create_connection(database)
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
            conn.commit()
            messagebox.showinfo("Success", "Product added successfully.")
        except Error as e:
            print(e)
            messagebox.showerror("Error", "Failed to add product.")
        finally:
            conn.close()

def edit_product(product_id, name, quantity, price):
    conn = create_connection(database)
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE products SET name=?, quantity=?, price=? WHERE id=?", (name, quantity, price, product_id))
            conn.commit()
            messagebox.showinfo("Success", "Product updated successfully.")
        except Error as e:
            print(e)
            messagebox.showerror("Error", "Failed to update product.")
        finally:
            conn.close()

def delete_product(product_id):
    conn = create_connection(database)
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            conn.commit()
            messagebox.showinfo("Success", "Product deleted successfully.")
        except Error as e:
            print(e)
            messagebox.showerror("Error", "Failed to delete product.")
        finally:
            conn.close()

def view_inventory():
    conn = create_connection(database)
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

def generate_report():
    conn = create_connection(database)
    if conn is not None:
        df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        low_stock_df = df[df['quantity'] < 10]
        print("Low Stock Products:")
        print(low_stock_df)
        df.to_csv("inventory_report.csv", index=False)
        messagebox.showinfo("Report", "Inventory report generated: inventory_report.csv")

# GUI application
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("800x600")

        self.create_initial_frame()

    def create_initial_frame(self):
        self.initial_frame = tk.Frame(self.root)
        self.initial_frame.pack(pady=50)

        tk.Button(self.initial_frame, text="Sign Up", width=20, height=3, command=self.create_signup_frame).pack(pady=10)
        tk.Button(self.initial_frame, text="Sign In", width=20, height=3, command=self.create_login_frame).pack(pady=10)

    def create_signup_frame(self):
        self.clear_frame()
        self.signup_frame = tk.Frame(self.root)
        self.signup_frame.pack(pady=50)

        tk.Label(self.signup_frame, text="Sign Up Form", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.signup_frame, text="Username:").pack()
        self.signup_username_entry = tk.Entry(self.signup_frame)
        self.signup_username_entry.pack(pady=5)

        tk.Label(self.signup_frame, text="Password:").pack()
        self.signup_password_entry = tk.Entry(self.signup_frame, show="*")
        self.signup_password_entry.pack(pady=5)

        tk.Button(self.signup_frame, text="Sign Up", width=15, command=self.signup).pack(pady=10)

    def create_login_frame(self):
        self.clear_frame()
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=50)

        tk.Label(self.login_frame, text="Sign In Form", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.login_frame, text="Username:").pack()
        self.login_username_entry = tk.Entry(self.login_frame)
        self.login_username_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Password:").pack()
        self.login_password_entry = tk.Entry(self.login_frame, show="*")
        self.login_password_entry.pack(pady=5)

        tk.Button(self.login_frame, text="Sign In", width=15, command=self.login).pack(pady=10)

    def signup(self):
        username = self.signup_username_entry.get()
        password = self.signup_password_entry.get()
        if username and password:
            register_user(username, password)
            self.signup_frame.pack_forget()
            self.create_initial_frame()
        else:
            messagebox.showerror("Error", "Username and Password cannot be empty")

    def login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()
        if login_user(username, password):
            self.login_frame.pack_forget()
            self.create_main_frame()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=50)

        tk.Button(self.main_frame, text="Add Product", width=20, height=3, command=self.add_product_window).pack(pady=10)
        tk.Button(self.main_frame, text="Edit Product", width=20, height=3, command=self.edit_product_window).pack(pady=10)
        tk.Button(self.main_frame, text="Delete Product", width=20, height=3, command=self.delete_product_window).pack(pady=10)
        tk.Button(self.main_frame, text="View Inventory", width=20, height=3, command=self.view_inventory_window).pack(pady=10)
        tk.Button(self.main_frame, text="Generate Report", width=20, height=3, command=self.generate_report).pack(pady=10)

    def add_product_window(self):
        self.clear_frame()
        self.add_product_frame = tk.Frame(self.root)
        self.add_product_frame.pack(pady=50)

        tk.Label(self.add_product_frame, text="Add Product Form", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.add_product_frame, text="Name:").pack()
        self.add_product_name_entry = tk.Entry(self.add_product_frame)
        self.add_product_name_entry.pack(pady=5)

        tk.Label(self.add_product_frame, text="Quantity:").pack()
        self.add_product_quantity_entry = tk.Entry(self.add_product_frame)
        self.add_product_quantity_entry.pack(pady=5)

        tk.Label(self.add_product_frame, text="Price:").pack()
        self.add_product_price_entry = tk.Entry(self.add_product_frame)
        self.add_product_price_entry.pack(pady=5)

        tk.Button(self.add_product_frame, text="Add", width=15, command=self.add_product_action).pack(pady=10)

    def add_product_action(self):
        name = self.add_product_name_entry.get()
        quantity = int(self.add_product_quantity_entry.get())
        price = float(self.add_product_price_entry.get())
        add_product(name, quantity, price)
        self.add_product_frame.pack_forget()
        self.create_main_frame()

    def edit_product_window(self):
        self.clear_frame()
        self.edit_product_frame = tk.Frame(self.root)
        self.edit_product_frame.pack(pady=50)
        tk.Label(self.edit_product_frame, text="Edit Product Form", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.edit_product_frame, text="Product ID:").pack()
        self.edit_product_id_entry = tk.Entry(self.edit_product_frame)
        self.edit_product_id_entry.pack(pady=5)

        tk.Label(self.edit_product_frame, text="Name:").pack()
        self.edit_product_name_entry = tk.Entry(self.edit_product_frame)
        self.edit_product_name_entry.pack(pady=5)

        tk.Label(self.edit_product_frame, text="Quantity:").pack()
        self.edit_product_quantity_entry = tk.Entry(self.edit_product_frame)
        self.edit_product_quantity_entry.pack(pady=5)

        tk.Label(self.edit_product_frame, text="Price:").pack()
        self.edit_product_price_entry = tk.Entry(self.edit_product_frame)
        self.edit_product_price_entry.pack(pady=5)

        tk.Button(self.edit_product_frame, text="Edit", width=15, command=self.edit_product_action).pack(pady=10)

    def edit_product_action(self):
        product_id = int(self.edit_product_id_entry.get())
        name = self.edit_product_name_entry.get()
        quantity = int(self.edit_product_quantity_entry.get())
        price = float(self.edit_product_price_entry.get())
        edit_product(product_id, name, quantity, price)
        self.edit_product_frame.pack_forget()
        self.create_main_frame()

    def delete_product_window(self):
        self.clear_frame()
        self.delete_product_frame = tk.Frame(self.root)
        self.delete_product_frame.pack(pady=50)

        tk.Label(self.delete_product_frame, text="Delete Product Form", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.delete_product_frame, text="Product ID:").pack()
        self.delete_product_id_entry = tk.Entry(self.delete_product_frame)
        self.delete_product_id_entry.pack(pady=5)

        tk.Button(self.delete_product_frame, text="Delete", width=15, command=self.delete_product_action).pack(pady=10)

    def delete_product_action(self):
        product_id = int(self.delete_product_id_entry.get())
        delete_product(product_id)
        self.delete_product_frame.pack_forget()
        self.create_main_frame()

    def view_inventory_window(self):
        self.clear_frame()
        self.view_inventory_frame = tk.Frame(self.root)
        self.view_inventory_frame.pack(pady=50)

        tk.Label(self.view_inventory_frame, text="Inventory", font=("Arial", 20)).pack(pady=20)

        inventory = view_inventory()
        if inventory:
            for i, product in enumerate(inventory):
                tk.Label(self.view_inventory_frame, text=f"ID: {product[0]}, Name: {product[1]}, Quantity: {product[2]}, Price: {product[3]}").pack(pady=5)
        else:
            tk.Label(self.view_inventory_frame, text="No products in inventory.").pack(pady=5)

        tk.Button(self.view_inventory_frame, text="Back", width=15, command=self.create_main_frame).pack(pady=10)

    def generate_report(self):
        generate_report()
        messagebox.showinfo("Report", "Inventory report generated: inventory_report.csv")

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
