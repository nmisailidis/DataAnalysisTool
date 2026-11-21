import sqlite3

from fastapi import FastAPI, Depends
import database as db

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


def get_db():
    conn = sqlite3.connect("data_analysis.db")
    try:
        yield conn
    finally:
        conn.close()


@app.get("/datasets")
def get_datasets(conn=Depends(get_db)):
    return db.get_all_datasets(conn)


@app.get("/datasets/{dataset_id}/records")
def get_records(dataset_id: int, conn=Depends(get_db)):
    return db.get_records_for_dataset(conn, dataset_id)