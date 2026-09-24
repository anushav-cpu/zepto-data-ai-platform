import sqlite3
import pandas as pd

database_file = "data_pipeline/data/books.db"

connection = sqlite3.connect(database_file)

# -----------------------------
# Query 1: SELECT + WHERE
# -----------------------------

query1 = """
SELECT title, price_gbp, rating
FROM books
WHERE rating >= 4
"""

print("\n--- Query 1: Books with rating 4 or higher ---")
print(query1)

result1 = pd.read_sql(query1, connection)
print(result1)


# -----------------------------
# Query 2: ORDER BY + LIMIT
# -----------------------------

query2 = """
SELECT title, price_inr
FROM books
ORDER BY price_inr DESC
LIMIT 10
"""

print("\n--- Query 2: 10 most expensive books ---")
print(query2)

result2 = pd.read_sql(query2, connection)
print(result2)


# -----------------------------
# Query 3: DISTINCT
# -----------------------------

query3 = """
SELECT DISTINCT category_name
FROM categories
ORDER BY category_name
"""

print("\n--- Query 3: Unique categories ---")
print(query3)

result3 = pd.read_sql(query3, connection)
print(result3)


# -----------------------------
# Query 4: BETWEEN
# -----------------------------

query4 = """
SELECT title, price_gbp
FROM books
WHERE price_gbp BETWEEN 20 AND 40
ORDER BY price_gbp
"""

print("\n--- Query 4: Books priced between £20 and £40 ---")
print(query4)

result4 = pd.read_sql(query4, connection)
print(result4)


# -----------------------------
# Query 5: JOIN
# -----------------------------

query5 = """
SELECT
    books.title,
    books.rating,
    categories.category_name
FROM books
JOIN categories
    ON books.category_id = categories.category_id
ORDER BY books.rating DESC
LIMIT 10
"""

print("\n--- Query 5: Books with their categories ---")
print(query5)

result5 = pd.read_sql(query5, connection)
print(result5)

# -----------------------------
# Reproduce JOIN using pandas.merge()
# -----------------------------

books_df = pd.read_sql(
    "SELECT * FROM books",
    connection
)

categories_df = pd.read_sql(
    "SELECT * FROM categories",
    connection
)

merge_result = pd.merge(
    books_df,
    categories_df,
    on="category_id",
    how="inner"
)

merge_result = merge_result[
    ["title", "rating", "category_name"]
].sort_values(
    by="rating",
    ascending=False
).head(10)

print("\n--- Pandas merge() JOIN result ---")
print(merge_result)

# Compare SQL JOIN and pandas.merge()
sql_join_result = result5[
    ["title", "rating", "category_name"]
].copy()

merge_result = merge_result[
    ["title", "rating", "category_name"]
].copy()

# Convert rating to the same integer type
sql_join_result["rating"] = sql_join_result["rating"].astype(int)
merge_result["rating"] = merge_result["rating"].astype(int)

# Sort both results in the same way
sql_join_result = sql_join_result.sort_values(
    by=["rating", "title"],
    ascending=[False, True]
).reset_index(drop=True)

merge_result = merge_result.sort_values(
    by=["rating", "title"],
    ascending=[False, True]
).reset_index(drop=True)

print("\n--- SQL JOIN and pandas.merge() comparison ---")

if sql_join_result.equals(merge_result):
    print("MATCH: SQL JOIN and pandas.merge() produce equivalent results.")
else:
    print("Results do not match.")
    print("\nSQL JOIN:")
    print(sql_join_result)

    print("\nPandas merge():")
    print(merge_result)

# -----------------------------
# Save SQL queries and outputs
# -----------------------------

with open(
    "data_pipeline/data/sql_results.txt",
    "w",
    encoding="utf-8"
) as file:

    file.write("QUERY 1\n")
    file.write(query1)
    file.write("\nOUTPUT:\n")
    file.write(result1.to_string(index=False))
    file.write("\n\n")

    file.write("QUERY 2\n")
    file.write(query2)
    file.write("\nOUTPUT:\n")
    file.write(result2.to_string(index=False))
    file.write("\n\n")

    file.write("QUERY 3\n")
    file.write(query3)
    file.write("\nOUTPUT:\n")
    file.write(result3.to_string(index=False))
    file.write("\n\n")

    file.write("QUERY 4\n")
    file.write(query4)
    file.write("\nOUTPUT:\n")
    file.write(result4.to_string(index=False))
    file.write("\n\n")

    file.write("QUERY 5 - JOIN\n")
    file.write(query5)
    file.write("\nOUTPUT:\n")
    file.write(result5.to_string(index=False))
    file.write("\n\n")

    file.write("PANDAS MERGE JOIN OUTPUT\n")
    file.write(merge_result.to_string(index=False))
    file.write("\n\n")

    if sql_join_result.equals(merge_result):
        file.write(
            "MATCH: SQL JOIN and pandas.merge() "
            "produce equivalent results.\n"
        )
    else:
        file.write("Results do not match.\n")

print("\nSQL queries and outputs saved successfully!")

connection.close()

print("\nAll SQL queries executed successfully!")