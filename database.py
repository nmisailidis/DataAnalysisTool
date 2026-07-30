import sqlite3
import json


def save_dataset(conn, filename, source_type, dataframe):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO datasets (source_filename, source_type) VALUES (?, ?)",
        (filename, source_type)
    )
    dataset_id = cursor.lastrowid

    for _, row in dataframe.iterrows():
        cursor.execute(
            "INSERT INTO records (dataset_id, data_json) VALUES (?, ?)",
            (dataset_id, json.dumps(row.to_dict(), default=str))
        )

    conn.commit()
    return dataset_id


def init_db(db_path="data_analysis.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_filename TEXT NOT NULL,
            source_type TEXT NOT NULL,   -- 'local' ή 'url'
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id INTEGER NOT NULL,
            data_json TEXT NOT NULL,     -- η γραμμή δεδομένων ως JSON
            FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        )
    """)

    conn.commit()
    conn.close()


def get_all_datasets(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, source_filename, source_type, imported_at FROM datasets ORDER BY imported_at DESC")
    return cursor.fetchall()


def get_records_for_dataset(conn, dataset_id):
    cursor = conn.cursor()
    cursor.execute("SELECT data_json FROM records WHERE dataset_id = ?", (dataset_id,))
    rows = cursor.fetchall()
    return [json.loads(row[0]) for row in rows]