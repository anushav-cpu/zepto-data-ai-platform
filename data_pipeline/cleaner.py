import pandas as pd

input_file = "data_pipeline/data/books_raw.csv"
output_file = "data_pipeline/data/books_clean.csv"

# Load raw data
df = pd.read_csv(input_file)

print("Original rows:", len(df))

# Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# Check duplicate rows
print("\nDuplicate rows:", df.duplicated().sum())

# -----------------------------
# Clean price
# -----------------------------

df["price_gbp"] = pd.to_numeric(
    df["price"]
    .astype(str)
    .str.replace("Â", "", regex=False)
    .str.replace("£", "", regex=False)
    .str.strip(),
    errors="coerce"
)

# -----------------------------
# Convert star rating
# -----------------------------

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

df["rating"] = df["star_rating"].map(rating_map)

# -----------------------------
# Convert availability to boolean
# -----------------------------

availability = (
    df["availability"]
    .astype("string")
    .str.strip()
    .str.lower()
)

df["in_stock"] = pd.NA

df.loc[
    availability.str.contains("in stock", na=False),
    "in_stock"
] = True

df.loc[
    availability.str.contains("out of stock", na=False),
    "in_stock"
] = False

df["in_stock"] = df["in_stock"].astype("boolean")


# -----------------------------
# Convert GBP to INR
# Fixed project rate:
# 1 GBP = 105.50 INR
# -----------------------------

df["price_inr"] = df["price_gbp"] * 105.50

# -----------------------------
# Handle parsing failures
# -----------------------------

# Drop rows where required values could not be parsed
df = df.dropna(
    subset=[
        "title",
        "price_gbp",
        "rating",
        "in_stock",
        "category"
    ]
)

# Remove duplicate rows
df = df.drop_duplicates()

# -----------------------------
# Select final columns
# -----------------------------

df = df[
    [
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category"
    ]
]

print("\nCleaned rows:", len(df))

print("\nData types:")
print(df.dtypes)

print("\nSample cleaned data:")
print(df.head())

# Save cleaned data
df.to_csv(
    output_file,
    index=False
)

print("\nCleaned data saved successfully!")