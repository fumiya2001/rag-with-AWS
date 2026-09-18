import os
import re
import PyPDF2
import psycopg2

from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

PDF_FILE_PATH = './data/attention_is_all_you_need_paper.pdf'

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

MODEL_NAME = 'all-MiniLM-L6-v2'

def extract_text_from_pdf(pdf_path:str) -> str:
    text = ""

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
    return text


def clean_text(text:str) -> str:
    text = re.sub(r'\n+', '\n ', text)   
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = text.strip()
    return text


def split_text(text:str) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, length_function=len, is_separator_regex=False)
    return text_splitter.split_text(text)


def create_embeddings(chunks:list[str]):
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(chunks)
    return embeddings


def create_table_if_not_exists() -> None:
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id SERIAL PRIMARY KEY,
                    chunk TEXT NOT NULL,
                    embedding vector(384) NOT NULL
                );
            """)
        conn.commit()


def save_to_db(chunks: list[str], embeddings) -> None:
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            for chunk, embedding in zip(chunks, embeddings):
                cur.execute(
                    "INSERT INTO embeddings (chunk, embedding) VALUES (%s, %s)",
                    (chunk, embedding.tolist())
                )
        conn.commit()

def reset_table():
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("DROP TABLE IF EXISTS embeddings;")
            cur.execute("""
                CREATE TABLE embeddings (
                    id SERIAL PRIMARY KEY,
                    chunk TEXT NOT NULL,
                    embedding vector(384) NOT NULL
                );
            """)
        conn.commit()


def main() -> None:
    text = extract_text_from_pdf(PDF_FILE_PATH)
    cleaned_text = clean_text(text)
    chunks = split_text(cleaned_text)
    embeddings = create_embeddings(chunks)

    reset_table()
    create_table_if_not_exists()
    save_to_db(chunks, embeddings)

    print("Done")


if __name__ == "__main__":
    main()