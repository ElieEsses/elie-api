import json
from pathlib import Path

import pandas as pd
import streamlit as st

progress_path = Path("dev/import_notion_books/progress.json")

def save_progress():
    progress_path.write_text(json.dumps({
        "index": st.session_state.index,
        "kept": st.session_state.kept
    }, default=str))

st.set_page_config(page_title="Book Import Review")

df = pd.read_csv("dev/import_notion_books/notion_books_transformed_final.csv")

st.title("Book Import Review")
st.write(f"{len(df)} books to review")

if "index" not in st.session_state:
    if progress_path.exists():
        progress = json.loads(progress_path.read_text())
        st.session_state.index = progress["index"]
        st.session_state.kept = progress["kept"]
    else:
        st.session_state.index = 0
        st.session_state.kept = []

index = st.session_state.index
book = df.iloc[index]

if index >= len(df):
    st.success("All books reviewed!")
    st.stop()

st.progress(index / len(df))
st.caption(f"Reviewed {index} of {len(df)} books")

st.header(book["title"])
st.write(book["authors"])
st.write(book["isbn"])
cover_url = st.text_input(
    "Cover URL",
    value=book["cover_url"] if pd.notna(book["cover_url"]) else "",
    key=f"cover_{index}"
)

if cover_url:
    st.image(cover_url, width=150)

if "kept" not in st.session_state:
    st.session_state.kept = []


col1, col2 = st.columns(2)

if col1.button("🗑️ Delete", use_container_width=True):
    st.session_state.index += 1
    st.rerun()

if col2.button("✓ Keep", use_container_width=True):
    updated_book = book.to_dict()
    updated_book["cover_url"] = cover_url

    st.session_state.kept.append(updated_book)
    st.session_state.index += 1
    st.rerun()