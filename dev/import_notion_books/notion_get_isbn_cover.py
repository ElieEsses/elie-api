import ast

import pandas as pd
import requests
from tqdm import tqdm
import dotenv
import os

dotenv.load_dotenv()

def get_isbn(title, authors):
    return "test-isbn"  # Placeholder for the actual ISBN lookup logic

def run_get_isbn_and_covers_pipeline(df):
    isbns = []
    cover_urls = []

    for index, row in tqdm(df.iterrows(), total=len(df)):
        title = row["title"]
        authors = row["authors"]

        try:
            isbn = get_isbn(title, authors)
            cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"
        except requests.RequestException as e:
            tqdm.write(f"Lookup failed for {title}: {e}")
            isbn, cover_url = None, None

        isbns.append(isbn)
        cover_urls.append(cover_url)

    df["isbn"] = isbns
    df["cover_url"] = cover_urls

    return df


if __name__ == "__main__":
    df = pd.read_csv(
        "dev/import_notion_books/notion_books_transformed.csv"
    )
    df["authors"] = df["authors"].apply(ast.literal_eval)

    df = df.head(10)  # Limit to first 10 rows for testing

    final_df = run_get_isbn_and_covers_pipeline(df)

    final_df.to_csv(
        "dev/import_notion_books/notion_books_transformed_final.csv",
        index=False,
    )
