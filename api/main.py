import sqlite3
from fastapi import HTTPException
from fastapi import UploadFile
from core import sources
from fastapi import FastAPI, Depends
import database as db
from pydantic import BaseModel
import pandas as pd
from core import report


app = FastAPI()


class DatasetCreated(BaseModel):
    id: int
    columns: list[str]
    rows: int


class ReportRequest(BaseModel):
    group_by: str
    columns: list[str]


@app.get("/health")
async def health():
    return {"status": "ok"}


class SourceRequest(BaseModel):
    source: str


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


@app.post("/datasets/from-url", response_model=DatasetCreated)
def create_dataset_from_url(request: SourceRequest, conn=Depends(get_db)):
    try:
        data, source_type = sources.load_excel(request.source)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read the file: {e}")

    dataset_id = db.save_dataset(conn, request.source, source_type, data)
    return {"id": dataset_id, "columns": list(data.columns), "rows": len(data)}


@app.post("/datasets/upload", response_model=DatasetCreated)
def create_dataset_from_file(file: UploadFile, conn=Depends(get_db)):

    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=415, detail="Could not read other type of files except .xlsx")

    try:
        data = pd.read_excel(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read the file: {e}")

    dataset_id = db.save_dataset(conn, file.filename, "upload", data)
    return {"id": dataset_id, "columns": [str(column) for column in data.columns], "rows": len(data)}


@app.post("/datasets/{dataset_id}/report")
def generate_report(request: ReportRequest, dataset_id: int, conn=Depends(get_db)):
    records = db.get_records_for_dataset(conn, dataset_id)

    if not records:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    data = pd.DataFrame(records)

    try:
        category_summary = report.build_report(data, request.group_by, request.columns)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=f"Could not build the report: {e}")

    return category_summary.reset_index().to_dict(orient="records")




