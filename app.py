import streamlit as st
import sqlite3
import openai
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Get API Key and Login Credentials from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# Ensure OpenAI API Key is Set
if not OPENAI_API_KEY:
    st.error("Missing OpenAI API Key! Please check your .env file.")
    st.stop()

# Initialize OpenAI Client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Database Helper
def get_db_connection():
    return sqlite3.connect("library.db")

# Database Setup
def create_database():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS books 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author TEXT, genre TEXT, year INTEGER)''')

    c.execute('''CREATE TABLE IF NOT EXISTS checked_out_books 
                 (id INTEGER PRIMARY KEY, title TEXT, author TEXT, genre TEXT, year INTEGER, return_date TEXT)''')

    conn.commit()
    conn.close()

create_database()

# Add Book
def add_book(title, author, genre, year):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author, genre, year) VALUES (?, ?, ?, ?)", 
              (title, author, genre, year))
    conn.commit()
    conn.close()
    st.session_state["refresh"] = True

# Delete Book
def delete_book(book_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (book_id,))
    c.execute("DELETE FROM checked_out_books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    st.session_state["refresh"] = True

# Fetch Books
def get_books():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()
    return books

# Search Books
def search_books(search_query):
    conn = get_db_connection()
    c = conn.cursor()
    search_term = f"%{search_query}%"
    c.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?", 
              (search_term, search_term, search_term))
    books = c.fetchall()
    conn.close()
    return books

# Check Out Book
def check_out_book(book_id):
    conn = get_db_connection()
    c = conn.cursor()

    # Get book details
    c.execute("SELECT * FROM books WHERE id=?", (book_id,))
    book = c.fetchone()

    if book:
        title, author, genre, year = book[1], book[2], book[3], book[4]
        return_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        # Insert into checked out books
        c.execute("INSERT INTO checked_out_books (id, title, author, genre, year, return_date) VALUES (?, ?, ?, ?, ?, ?)",
                  (book_id, title, author, genre, year, return_date))
        conn.commit()

    conn.close()
    st.session_state["refresh"] = True

# Check In Book
def check_in_book(book_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Remove from checked out books
    c.execute("DELETE FROM checked_out_books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    st.session_state["refresh"] = True

# Auto-Return Books after 14 Days
def auto_return_books():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get books that are past return date
    current_date = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM checked_out_books WHERE return_date < ?", (current_date,))
    overdue_books = c.fetchall()

    for book in overdue_books:
        book_id, title, author, genre, year, _ = book
        c.execute("DELETE FROM checked_out_books WHERE id=?", (book_id,))
    
    conn.commit()
    conn.close()
    st.session_state["refresh"] = True

# Chatbot
def get_book_description(title):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a library assistant. you are asked to provide a description of a book. reccomendation and summary"}],
                  {"role": "user", "content": f"Tell me about the following :"}]
    )
    return response.choices[0].message.content

# Streamlit Login Page
st.sidebar.header("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

# ✅ Added "Login" Button
if st.sidebar.button("Login"):
    if username == USERNAME and password == PASSWORD:
        st.session_state["logged_in"] = True
        st.sidebar.success("Login Successful!")
    else:
        st.sidebar.error("Invalid username or password")

# ✅ Show content only if logged in
if "logged_in" in st.session_state and st.session_state["logged_in"]:
    st.title("📚 Library Management System")

    # ✅ Auto Return Overdue Books
    auto_return_books()

    # Manage Books
    st.sidebar.header("Manage Books")
    book_title = st.sidebar.text_input("Title")
    author = st.sidebar.text_input("Author")
    genre = st.sidebar.text_input("Genre")
    year = st.sidebar.number_input("Year", min_value=0, max_value=2100, step=1)

    if st.sidebar.button("Add Book"):
        add_book(book_title, author, genre, year)
        st.sidebar.success("Book added successfully!")

    # ✅ Search Books
    st.header("🔍 Search Books")
    search_query = st.text_input("Enter book title, author, or genre")
    if st.button("Search"):
        search_results = search_books(search_query)
        if search_results:
            for book in search_results:
                st.subheader(f"{book[1]} by {book[2]}")
                st.text(f"Genre: {book[3]}, Year: {book[4]}")
        else:
            st.warning("No books found.")

    # View Books Button
    if st.button("View Books"):
        st.header("📖 Book Catalog")
        books = get_books()

        for book in books:
            book_id = book[0]
            title = book[1]
            author = book[2]
            genre = book[3]
            year = book[4]

            st.subheader(f"{title} by {author}")
            st.text(f"Genre: {genre}, Year: {year}")

            # Check Out Button
            if st.button(f"Check Out {title}", key=f"checkout_{book_id}"):
                check_out_book(book_id)

            # Check In Button
            if st.button(f"Check In {title}", key=f"checkin_{book_id}"):
                check_in_book(book_id)

            # Delete Button
            if st.button(f"Delete {title}", key=f"delete_{book_id}"):
                delete_book(book_id)

    # Chatbot
    st.header("🤖 Ask the Library Assistant")
    user_input = st.text_input("Ask me about a book")
    if st.button("Get Answer"):
        response = get_book_description(user_input)
        st.write(response)

    # ✅ Force Streamlit to Refresh if Needed
    if "refresh" in st.session_state and st.session_state["refresh"]:
        st.session_state["refresh"] = False
        st.experimental_rerun()
else:
    st.warning("Please log in to access the system.")
