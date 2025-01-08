import tkinter
from tkinter import messagebox
from datetime import datetime, timedelta
import sqlite3

# Database connection
connection = sqlite3.connect('library.db')
cursor = connection.cursor()

# Creating tables
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        category TEXT NOT NULL,
        isbn TEXT UNIQUE NOT NULL,
        added_date TEXT NOT NULL,
        available INTEGER DEFAULT 1
    )'''
)
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    issue_date TEXT NOT NULL,
    return_date TEXT NOT NULL,
    fine REAL DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)''')
connection.commit()

# Login Functionality
def login():
    def verify_login():
        username = username_entry.get()
        password = password_entry.get()
        cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            role = user[0]
            messagebox.showinfo("Login Successful", "Welcome!")
            login_window.destroy()
            if role == 'admin':
                admin_window()
            else:
                user_window()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    login_window = tkinter.Tk()
    login_window.title("Library Management System")

    tkinter.Label(login_window, text="Username").grid(row=0, column=0, padx=20, pady=10)
    username_entry = tkinter.Entry(login_window)
    username_entry.grid(row=0, column=1, padx=10, pady=5)

    tkinter.Label(login_window, text="Password").grid(row=1, column=0, padx=20, pady=10)
    password_entry = tkinter.Entry(login_window, show='*')
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    login_button = tkinter.Button(login_window, text="Login", command=verify_login)
    login_button.grid(row=2, column=0, columnspan=2, pady=10)

    login_window.mainloop()

# Add Book Functionality
def add_book():
    def save_book():
        title = title_entry.get()
        author = author_entry.get()
        category = category_var.get()
        isbn = isbn_entry.get()
        added_date = datetime.now().strftime("%Y-%m-%d")

        if not (title and author and category and isbn):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            cursor.execute("INSERT INTO books (title, author, category, isbn, added_date) VALUES (?, ?, ?, ?, ?)",
                           (title, author, category, isbn, added_date))
            connection.commit()
            messagebox.showinfo("Success", "Book added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Book with this ISBN already exists!")

    add_window = tkinter.Toplevel()
    add_window.title("Add Book")

    tkinter.Label(add_window, text="Title").grid(row=0, column=0, padx=10, pady=5)
    title_entry = tkinter.Entry(add_window)
    title_entry.grid(row=0, column=1, padx=10, pady=5)

    tkinter.Label(add_window, text="Author").grid(row=1, column=0, padx=10, pady=5)
    author_entry = tkinter.Entry(add_window)
    author_entry.grid(row=1, column=1, padx=10, pady=5)

    tkinter.Label(add_window, text="Category").grid(row=2, column=0, padx=10, pady=5)
    category_var = tkinter.StringVar(value="Book")
    tkinter.OptionMenu(add_window, category_var, "Book", "Movie", "Fiction", "Horror").grid(row=2, column=1, padx=10, pady=5)

    tkinter.Label(add_window, text="ISBN").grid(row=3, column=0, padx=10, pady=5)
    isbn_entry = tkinter.Entry(add_window)
    isbn_entry.grid(row=3, column=1, padx=10, pady=5)

    add_button = tkinter.Button(add_window, text="Add Book", command=save_book)
    add_button.grid(row=4, column=0, columnspan=2, pady=10)

# Issue Book Functionality
def issue_book():
    def process_issue():
        book_id = book_id_entry.get()
        user_id = user_id_entry.get()
        issue_date = datetime.now().strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        cursor.execute("SELECT available FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()

        if book and book[0] == 1:
            cursor.execute("INSERT INTO transactions (book_id, user_id, issue_date, return_date) VALUES (?, ?, ?, ?)",
                           (book_id, user_id, issue_date, return_date))
            cursor.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
            connection.commit()
            messagebox.showinfo("Success", "Book issued successfully!")
        else:
            messagebox.showerror("Error", "Book not available or invalid Book ID")

    issue_window = tkinter.Toplevel()
    issue_window.title("Issue Book")

    tkinter.Label(issue_window, text="Book ID").grid(row=0, column=0, padx=10, pady=5)
    book_id_entry = tkinter.Entry(issue_window)
    book_id_entry.grid(row=0, column=1, padx=10, pady=5)

    tkinter.Label(issue_window, text="User ID").grid(row=1, column=0, padx=10, pady=5)
    user_id_entry = tkinter.Entry(issue_window)
    user_id_entry.grid(row=1, column=1, padx=10, pady=5)

    issue_button = tkinter.Button(issue_window, text="Issue Book", command=process_issue)
    issue_button.grid(row=2, column=0, columnspan=2, pady=10)

# Return Book Functionality
def return_book():
    def process_return():
        transaction_id = transaction_id_entry.get()

        cursor.execute("SELECT book_id, return_date FROM transactions WHERE id = ?", (transaction_id,))
        transaction = cursor.fetchone()

        if transaction:
            book_id, return_date = transaction
            actual_return_date = datetime.now()
            due_date = datetime.strptime(return_date, "%Y-%m-%d")
            fine = max((actual_return_date - due_date).days * 1, 0)  # $1 fine per day

            cursor.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
            cursor.execute("UPDATE transactions SET fine = ? WHERE id = ?", (fine, transaction_id))
            connection.commit()
            messagebox.showinfo("Success", f"Book returned successfully! Fine: ${fine}")
        else:
            messagebox.showerror("Error", "Invalid Transaction ID")

    return_window = tkinter.Toplevel()
    return_window.title("Return Book")

    tkinter.Label(return_window, text="Transaction ID").grid(row=0, column=0, padx=10, pady=5)
    transaction_id_entry = tkinter.Entry(return_window)
    transaction_id_entry.grid(row=0, column=1, padx=10, pady=5)

    return_button = tkinter.Button(return_window, text="Return Book", command=process_return)
    return_button.grid(row=1, column=0, columnspan=2, pady=10)

def removal_book():
    def process_removal():
        book_id = book_id_entry.get()
        if book_id:
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            connection.commit()
            messagebox.showinfo("Success", "Book removed successfully")
        else:
            messagebox.showerror("Error", "Please enter a valid Book ID")

    remove_window = tkinter.Toplevel()
    remove_window.title("Remove Book")

    tkinter.Label(remove_window, text="Book ID").grid(row=0, column=0, padx=10, pady=5)
    book_id_entry = tkinter.Entry(remove_window)
    book_id_entry.grid(row=0, column=1, padx=10, pady=5)

    remove_button = tkinter.Button(remove_window, text="Remove Book", command=process_removal)
    remove_button.grid(row=1, column=0, columnspan=2, pady=10)

def view_books():
    view_window = tkinter.Toplevel()
    view_window.title("View Books")
    view_window.geometry("600x400")

    # Create a Listbox to display books
    listbox = tkinter.Listbox(view_window, width=80, height=20)
    listbox.pack(pady=10, padx=10)

    # Fetch all books from the database
    cursor.execute("SELECT id, title, author, category, isbn, available FROM books")
    books = cursor.fetchall()

    # Insert books into the Listbox
    for book in books:
        book_id, title, author, category, isbn, available = book
        availability = "Available" if available else "Not Available"
        listbox.insert(tkinter.END, f"ID: {book_id}, Title: {title}, Author: {author}, Category: {category}, ISBN: {isbn}, Status: {availability}")

def view_transactions():
    view_transactions_window = tkinter.Toplevel()
    view_transactions_window.title("View Transactions")
    view_transactions_window.geometry("800x400")

    # Create a Listbox to display transactions
    listbox = tkinter.Listbox(view_transactions_window, width=120, height=20)
    listbox.pack(pady=10, padx=10)

    # Fetch all transactions from the database
    cursor.execute("SELECT transactions.id, books.title, users.username, transactions.issue_date, transactions.return_date, transactions.fine FROM transactions JOIN books ON transactions.book_id = books.id JOIN users ON transactions.user_id = users.id")
    transactions = cursor.fetchall()

    # Insert transactions into the Listbox
    for transaction in transactions:
        transaction_id, book_title, username, issue_date, return_date, fine = transaction
        listbox.insert(tkinter.END, f"Transaction ID: {transaction_id}, Book: {book_title}, User: {username}, Issue Date: {issue_date}, Return Date: {return_date}, Fine: ${fine}")

def pay_fine():
    def view_fines():
        user_id = user_id_entry.get()
        if user_id:
            cursor.execute("SELECT transactions.id, books.title, transactions.fine FROM transactions JOIN books ON transactions.book_id = books.id WHERE user_id = ? AND fine > 0", (user_id,))
            fines = cursor.fetchall()
            if fines:
                for fine in fines:
                    listbox.insert(tkinter.END, f"Transaction ID: {fine[0]}, Book: {fine[1]}, Fine: ${fine[2]}")
            else:
                messagebox.showinfo("Info", "No outstanding fines for this user.")
        else:
            messagebox.showerror("Error", "Please enter a valid User ID")

    def process_payment():
        transaction_id = transaction_id_entry.get()
        if transaction_id:
            cursor.execute("UPDATE transactions SET fine = 0 WHERE id = ?", (transaction_id,))
            connection.commit()
            messagebox.showinfo("Success", "Payment processed successfully!")
            view_fines()  # Refresh the list after payment
        else:
            messagebox.showerror("Error", "Please enter a valid Transaction ID")

    pay_window = tkinter.Toplevel()
    pay_window.title("Pay Fine")
    pay_window.geometry("500x400")

    tkinter.Label(pay_window, text="User  ID").grid(row=0, column=0, padx=10, pady=5)
    user_id_entry = tkinter.Entry(pay_window)
    user_id_entry.grid(row=0, column=1, padx=10, pady=5)

    view_fines_button = tkinter.Button(pay_window, text="View Fines", command=view_fines)
    view_fines_button.grid(row=1, column=0, columnspan=2, pady=10)

    listbox = tkinter.Listbox(pay_window, width=60, height=10)
    listbox.grid(row=2, column=0, columnspan=2, pady=10)

    tkinter.Label(pay_window, text="Transaction ID").grid(row=3, column=0, padx=10, pady=5)
    transaction_id_entry = tkinter.Entry(pay_window)
    transaction_id_entry.grid(row=3, column=1, padx=10, pady=5)

    pay_button = tkinter.Button(pay_window, text="Pay Fine", command=process_payment)
    pay_button.grid(row=4, column=0, columnspan=2, pady=10)

# User Window
def user_window():
    user_win = tkinter.Toplevel()
    user_win.title("User Window")
    user_win.geometry("400x300")

    tkinter.Label(user_win, text="User Window", font=("Arial", 16)).pack(pady=10)

    tkinter.Button(user_win, text="View Book", command=view_books).pack(pady=5)
    tkinter.Button(user_win, text="Issue Book", command=issue_book).pack(pady=5)
    tkinter.Button(user_win, text="Return Book", command=return_book).pack(pady=5)
    tkinter.Button(user_win, text="Pay Transaction", command=pay_fine).pack(pady=5)

# Admin Window
def admin_window():
    admin_win = tkinter.Toplevel()
    admin_win.title("Admin Window")
    admin_win.geometry("400x300")

    tkinter.Label(admin_win, text="Admin Window", font=("Arial", 16)).pack(pady=10)

    tkinter.Button(admin_win, text="View Book", command=view_books).pack(pady=5)
    tkinter.Button(admin_win, text="Add Book", command=add_book).pack(pady=5)
    tkinter.Button(admin_win, text="remove books", command=removal_book).pack(pady=5)
    tkinter.Button(admin_win, text="view transactions", command=view_transactions).pack(pady=5)

# Main Window
root = tkinter.Tk()
root.title("Library Management System")
root.geometry("400x200")

tkinter.Label(root, text="Library Management System", font=("Arial", 16)).pack(pady=10)

tkinter.Label(root, text="Select Role:", font=("Arial", 12)).pack(pady=5)

tkinter.Button(root, text="Login", width=15, command=login).pack(pady=5)
# tkinter.Button(root, text="User", width=15, command=user_window).pack(pady=5)
# tkinter.Button(root, text="Admin", width=15, command=admin_window).pack(pady=5)

tkinter.Button(root, text="Exit", width=15, command=root.destroy).pack(pady=10)

root.mainloop()
