"""
This script ingests CSV data into PostgreSQL instead of SQLite due to memory limitations.
It skips uploading files if the table already exists in the database.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, inspect
import logging
import time
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# Load environment variables from .env
load_dotenv()

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Setup logging
logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",
    force=True
)

# PostgreSQL engine
engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

try:
    with engine.connect() as conn:
        print("Connection successful ✅")
except Exception as e:
    print("Connection failed ❌", e)
    exit(1)

# Table:CSV map
tables = {
    'purchases': 'data/purchases.csv',
    'purchase_prices': 'data/purchase_prices.csv',
    'sales': 'data/sales.csv',
    'vendor_invoice': 'data/vendor_invoice.csv',
    'begin_inventory': 'data/begin_inventory.csv',
    'end_inventory': 'data/end_inventory.csv'
}

CHUNK_SIZE = 100_000


def validate_all_files_exist(tables):
    missing_files = [f for f in tables.values() if not os.path.exists(f)]
    if missing_files:
        logging.error("❌ Missing CSVs: " + ", ".join(missing_files))
        return False
    return True


def table_exists(table_name, engine):
    """Check if a table already exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def upload_csv_with_chunks(table_name, file_path, engine):
    logging.info(f"Uploading {file_path} to {table_name} using pandas chunks...")
    try:
        for i, chunk in enumerate(pd.read_csv(file_path, chunksize=CHUNK_SIZE)):
            chunk.to_sql(table_name, engine, if_exists='append' if i else 'replace', index=False)
            logging.info(f"  Chunk {i+1} uploaded.")
        return True
    except Exception as e:
        logging.error(f"❌ Chunk upload failed for {table_name}: {e}")
        return False


def upload_csv_with_copy(table_name, file_path, conn):
    logging.info(f"Uploading {file_path} to {table_name} using COPY...")
    try:
        with conn.cursor() as cursor, open(file_path, 'r', encoding='utf-8') as f:
            cursor.copy_expert(sql.SQL("COPY {} FROM STDIN WITH CSV HEADER").format(
                sql.Identifier(table_name)), f)
        conn.commit()
        logging.info(f"✅ COPY upload complete for {table_name}")
        return True
    except Exception as e:
        logging.error(f"❌ COPY failed for {table_name}: {e}")
        return False


def upload_raw_csvs(tables):
    conn = engine.raw_connection()
    for table, path in tables.items():
        logging.info(f"⬆️ Uploading {table} from {path}...")

        if table_exists(table, engine):
            # Use COPY for existing tables
            success = upload_csv_with_copy(table, path, conn)
            if not success:
                logging.warning(f"⚠️ Falling back to chunk upload for {table}")
                upload_csv_with_chunks(table, path, engine)
        else:
            # If table doesn't exist, just use chunk upload which creates the table
            logging.info(f"🆕 Table {table} doesn't exist, using pandas chunks to create and upload.")
            upload_csv_with_chunks(table, path, engine)
    conn.close()



def ingest_db(df, tables, engine):
    """Ingest a cleaned DataFrame into the given PostgreSQL table."""
    try:
        df.to_sql(tables, engine, if_exists='replace', index=False)
        logging.info(f"✅ DataFrame successfully written to {tables}")
    except Exception as e:
        logging.error(f"❌ Failed to ingest DataFrame to {tables}: {e}")


def load_raw_data():
    start = time.time()
    logging.info("🚀 Starting data ingestion...")

    if not validate_all_files_exist(tables):
        logging.error("❌ Ingestion aborted.")
        return

    upload_raw_csvs(tables)

    elapsed = (time.time() - start) / 60
    logging.info(f"✅ Ingestion complete in {elapsed:.2f} minutes.")

if __name__ == "__main__":
    load_raw_data()
