💡 Code Breakdown & Explanation
1️⃣ Authentication System
The app requires users to log in with a username and password stored in the .env file.
If the login fails, access is denied.
python
Copy
Edit
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

st.sidebar.header("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if username == USERNAME and password == PASSWORD:
        st.session_state["logged_in"] = True
        st.sidebar.success("Login Successful!")
    else:
        st.sidebar.error("Invalid username or password")
2️⃣ Database Setup & Management (SQLite)
The system uses SQLite as a lightweight database.
The database has two main tables:
books → Stores all books.
checked_out_books → Stores books that are currently checked out.
python
Copy
Edit
def create_database():
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    
    # Books Table
    c.execute('''CREATE TABLE IF NOT EXISTS books 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author TEXT, genre TEXT, year INTEGER)''')

    # Checked Out Books Table
    c.execute('''CREATE TABLE IF NOT EXISTS checked_out_books 
                 (id INTEGER PRIMARY KEY, title TEXT, author TEXT, genre TEXT, year INTEGER, return_date TEXT)''')

    conn.commit()
    conn.close()
3️⃣ Adding a Book
Users can add books through a Streamlit sidebar form.
The book is stored in the books table.
python
Copy
Edit
def add_book(title, author, genre, year):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author, genre, year) VALUES (?, ?, ?, ?)", 
              (title, author, genre, year))
    conn.commit()
    conn.close()
4️⃣ Searching for Books
Users can search for books by title, author, or genre.
The search function uses SQL wildcard matching (LIKE query).
python
Copy
Edit
def search_books(search_query):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    search_term = f"%{search_query}%"
    c.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?", 
              (search_term, search_term, search_term))
    books = c.fetchall()
    conn.close()
    return books
5️⃣ Checking Out & Checking In Books
🔹 Check Out
The check-out function:
Moves the book to checked_out_books.
Assigns a 14-day return deadline.
python
Copy
Edit
def check_out_book(book_id):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()

    c.execute("SELECT * FROM books WHERE id=?", (book_id,))
    book = c.fetchone()

    if book:
        title, author, genre, year = book[1], book[2], book[3], book[4]
        return_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        c.execute("INSERT INTO checked_out_books (id, title, author, genre, year, return_date) VALUES (?, ?, ?, ?, ?, ?)",
                  (book_id, title, author, genre, year, return_date))
        conn.commit()

    conn.close()
    st.session_state["refresh"] = True
🔹 Check In
Removes the book from checked_out_books, making it available again.
python
Copy
Edit
def check_in_book(book_id):
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    
    c.execute("DELETE FROM checked_out_books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    st.session_state["refresh"] = True
6️⃣ Auto-Return Books After 14 Days
If a checked-out book isn't returned in 14 days, it automatically becomes available again.
python
Copy
Edit
def auto_return_books():
    conn = sqlite3.connect("library.db")
    c = conn.cursor()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM checked_out_books WHERE return_date < ?", (current_date,))
    overdue_books = c.fetchall()

    for book in overdue_books:
        book_id, title, author, genre, year, _ = book
        c.execute("DELETE FROM checked_out_books WHERE id=?", (book_id,))
    
    conn.commit()
    conn.close()
7️⃣ AI Chatbot for Book Descriptions
Uses OpenAI's GPT-4 API to retrieve book details.
python
Copy
Edit
def get_book_description(title):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a library assistant."},
                  {"role": "user", "content": f"Tell me about the book '{title}'"}]
    )
    return response.choices[0].message.content
🔍 RAG (Retrieval-Augmented Generation) Attempt
I attempted to implement a Retrieval-Augmented Generation (RAG) model to enhance the search engine.
However, due to time constraints and performance issues, the implementation wasn't completed under pressure.

The current search engine relies on SQLite queries, which work well for now.
In the future, I plan to integrate vector-based search (FAISS or Pinecone) for more advanced AI-powered search capabilities.

🔮 Future Improvements
Switch to MongoDB for better scalability.
Implement an AI-powered search engine using FAISS or Pinecone.
Improve UI/UX for a better user experience.
👨‍💻 Author
Developed by [Your Name].
Feel free to contribute, improve, and modify this project! 🚀

📜 License
This project is open-source. You can modify and distribute it freely.

🚀 Now your README is complete with detailed explanations! Let me know if you need more improvements! 🔥