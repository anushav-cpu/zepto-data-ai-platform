import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

base_url = "https://books.toscrape.com/catalogue/page-{}.html"

all_books = []

# Scrape first 5 pages = 100 books
for page in range(1, 6):

    url = base_url.format(page)

    response = requests.get(url)

    print("Scraping page:", page)

    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    for book in books:

        title = book.h3.a["title"]

        price = book.find("p", class_="price_color").text.strip()

        star_rating = book.p["class"][1]

        product_url = book.h3.a["href"]

        # Convert relative URL to full URL
        product_url = "https://books.toscrape.com/catalogue/" + product_url.replace("../", "")

        # Open individual book page
        product_response = requests.get(product_url)

        product_soup = BeautifulSoup(
            product_response.text,
            "html.parser"
        )

        # Availability
        availability = product_soup.find(
            "p",
            class_="instock availability"
        ).text.strip()

        # Category from breadcrumb
        breadcrumb = product_soup.find(
            "ul",
            class_="breadcrumb"
        )

        category = breadcrumb.find_all("li")[2].text.strip()

        all_books.append({
            "title": title,
            "price": price,
            "star_rating": star_rating,
            "availability": availability,
            "category": category
        })

df = pd.DataFrame(all_books)

print("\nTotal books:", len(df))

print("\nCategories:")
print(df["category"].unique())

# Create data folder if it does not exist
os.makedirs("data_pipeline/data", exist_ok=True)

# Save raw data
df.to_csv(
    "data_pipeline/data/books_raw.csv",
    index=False
)

print("\nData saved successfully!")