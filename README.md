# Zepto Data & AI Platform

This project is a capstone project for the AI/ML Certificate Program.

The project contains three modules:

- `data_pipeline` – Data scraping, cleaning, database creation, and SQL analysis
- `analytics` – Analytics and insights
- `support_assistant` – Support assistant

## Module 1: Data Pipeline

### Objective

Scrape book data from Books to Scrape, clean the data, convert prices from GBP to INR, store the data in a normalized SQLite database, and perform SQL and Pandas analysis.

## Data Collection

The project scrapes the first 5 paginated listing pages from:

`https://books.toscrape.com`

The first 5 pages contain 100 books in total.

For each book, the following raw fields are collected:

- `title`
- `price`
- `star_rating`
- `availability`
- `category`

The raw data is saved as:

`data_pipeline/data/books_raw.csv`

## Data Cleaning

The following transformations are applied:

- GBP currency symbols are removed and `price_gbp` is converted to a numeric value.
- Star ratings such as `One`, `Two`, `Three`, `Four`, and `Five` are converted to integers from 1 to 5.
- Availability text is converted to the boolean field `in_stock`.
- Rows with parsing failures in required fields are dropped so that invalid records do not cause the pipeline to crash.
- Duplicate rows are removed.

The cleaned data is saved as:

`data_pipeline/data/books_clean.csv`

## GBP to INR Conversion

A fixed project-defined exchange rate is used:

**1 GBP = 105.50 INR**

No external exchange-rate API is used.

The INR price is calculated as:

`price_inr = price_gbp * 105.50`

## SQLite Database

The cleaned data is stored in:

`data_pipeline/data/books.db`

The database uses two normalized tables:

### categories

- `category_id` – Primary Key
- `category_name` – Unique category name

### books

- `book_id` – Primary Key
- `title`
- `price_gbp`
- `price_inr`
- `rating`
- `in_stock`
- `category_id` – Foreign Key referencing `categories`

The database contains 100 books across 29 categories.

## SQL Analysis

Five SQL queries are executed to demonstrate:

1. `SELECT` and `WHERE`
2. `ORDER BY` and `LIMIT`
3. `DISTINCT`
4. `BETWEEN`
5. `JOIN` between `books` and `categories`

SQL query strings and their outputs are saved in:

`data_pipeline/data/sql_results.txt`

The SQL results are also loaded into Pandas using `pd.read_sql()`.

The JOIN result is independently reproduced using:

`pandas.merge()`

The SQL JOIN and Pandas merge results are compared and confirmed to match.

## Project Structure

```text
zepto-data-ai-platform/
│
├── README.md
├── requirements.txt
│
├── data_pipeline/
│   ├── scraper.py
│   ├── cleaner.py
│   ├── database.py
│   ├── run_pipeline.py
│   ├── sql_queries.py
│   │
│   └── data/
│       ├── books_raw.csv
│       ├── books_clean.csv
│       ├── books.db
│       └── sql_results.txt
│
├── analytics/
│
└── support_assistant/
## Installation

Create and activate a Python virtual environment:

```bash
python -m venv venv

Activate it on Windows PowerShell:

.\venv\Scripts\Activate.ps1

Install the required packages:

pip install -r requirements.txt
Running Module 1

From the project root directory, run:

python data_pipeline/run_pipeline.py

This runs:

Scraping
Data cleaning
Database creation

Then run the SQL analysis:

python data_pipeline/sql_queries.py
Module 1 Output

After successful execution, the following files are generated:

books_raw.csv
books_clean.csv
books.db
sql_results.txts