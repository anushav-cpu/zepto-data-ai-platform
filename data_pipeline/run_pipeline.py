import subprocess
import sys


print("Starting Data Pipeline...")

# Step 1: Scrape data
print("\nStep 1: Scraping data...")
subprocess.run([sys.executable, "data_pipeline/scraper.py"], check=True)

# Step 2: Clean data
print("\nStep 2: Cleaning data...")
subprocess.run([sys.executable, "data_pipeline/cleaner.py"], check=True)

# Step 3: Store data in database
print("\nStep 3: Creating database...")
subprocess.run([sys.executable, "data_pipeline/database.py"], check=True)

print("\nData Pipeline completed successfully!")