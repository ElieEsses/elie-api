import pandas as pd

df = pd.read_csv("dev/import_notion_books/notion_books_transformed.csv")

for index, row in df.iterrows():
    if pd.isna(row["isbn"]):
        print(f"Missing ISBN for book: {row['title']} by {', '.join(row['authors'])}")