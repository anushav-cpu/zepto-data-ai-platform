import sqlite3
import pandas as pd

# File paths
input_file = "data_pipeline/data/books_clean.csv"
database_file = "data_pipeline/data/books.db"

# Load cleaned data
df = pd.read_csv(input_file)

# Connect to SQLite
connection = sqlite3.connect(database_file)

# Enable foreign key support
connection.execute("PRAGMA foreign_keys = ON")

# Create Categories table
connection.execute("""
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
)
""")

# Create Books table
connection.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock INTEGER,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
)
""")

# Start fresh each time the pipeline runs
connection.execute("DELETE FROM books")
connection.execute("DELETE FROM categories")

# Insert categories
categories = df["category"].drop_duplicates().tolist()

for category in categories:
    connection.execute(
        "INSERT INTO categories (category_name) VALUES (?)",
        (category,)
    )

# Insert books
for _, row in df.iterrows():

    category_id = connection.execute(
        "SELECT category_id FROM categories WHERE category_name = ?",
        (row["category"],)
    ).fetchone()[0]

    connection.execute("""
        INSERT INTO books
        (title, price_gbp, price_inr, rating, in_stock, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["title"],
        row["price_gbp"],
        row["price_inr"],
        row["rating"],
        int(row["in_stock"]),
        category_id
    ))

connection.commit()

# Check record counts
category_count = connection.execute(
    "SELECT COUNT(*) FROM categories"
).fetchone()[0]

book_count = connection.execute(
    "SELECT COUNT(*) FROM books"
).fetchone()[0]

print("Categories in database:", category_count)
print("Books in database:", book_count)

connection.close()

print("Database created successfully!")