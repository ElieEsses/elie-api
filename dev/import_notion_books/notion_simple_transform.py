import pandas as pd


def run_transform_pipeline(df):
    df = df.drop(
        columns=[
            "Finished",
            "Genre",
            "Type",
            "Language",
            "Re-Read Finished",
        ]
    )

    df = df.rename(
        columns={
            "Name": "title",
            "Author": "authors",
            "Status": "status",
            "Rating": "rating",
        }
    )

    def map_status(value):
        if pd.isna(value) or value == "Not Yet":
            return "unread"
        return value.lower()

    def map_author(value):
        if pd.isna(value):
            return []
        return [
            author.strip()
            for author in value.split(",")
            if author.strip()
        ]

    def map_rating(value):
        if pd.isna(value):
            return 0
        return value.count("⭐")

    df["status"] = df["status"].apply(map_status)
    df["authors"] = df["authors"].apply(map_author)
    df["rating"] = df["rating"].apply(map_rating)

    return df


if __name__ == "__main__":
    df = pd.read_csv("dev/import_notion_books/notion_books_export.csv")
    df = run_transform_pipeline(df)
    df.to_csv(
        "dev/import_notion_books/notion_books_transformed.csv",
        index=False,
    )