import sqlite3
from fastapi import HTTPException
from fastapi import UploadFile
from core import sources, summary
from fastapi import FastAPI, Depends
import database as db
from pydantic import BaseModel, ValidationError
import pandas as pd
from core import report
from api.llm import question_to_plan, write_summary

app = FastAPI(title="Data Analysis API")
db.init_db()


class SourceRequest(BaseModel):
    source: str


class DatasetCreated(BaseModel):
    id: int
    columns: list[str]
    rows: int


class ReportRequest(BaseModel):
    group_by: str
    columns: list[str]


class AskRequest(BaseModel):
    question: str


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


@app.post("/datasets/{dataset_id}/ask")
def question_to_llm(dataset_id: int, request: AskRequest, conn=Depends(get_db)):
    records = db.get_records_for_dataset(conn, dataset_id)

    if not records:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    data = pd.DataFrame(records)
    columns = data.columns

    numeric_columns = []

    for i in columns:
        if pd.api.types.is_numeric_dtype(data[i]):
            numeric_columns.append(i)

    answer = question_to_plan(request.question, columns, numeric_columns)

    try:
        plan = ReportRequest.model_validate_json(answer)
    except ValidationError as e:
        raise HTTPException(status_code=502, detail=f"The AI returned an invalid plan: {e}")

    plan.columns = [column for column in plan.columns if column in numeric_columns]
    if not plan.columns:
        raise HTTPException(status_code=400, detail="The question didn't match any number columns. Try rephrasing it.")

    result = generate_report(plan, dataset_id, conn)

    return {"plan": plan, "result": result}


@app.get("/datasets/{dataset_id}/summary")
def summarize(dataset_id: int, conn=Depends(get_db)):
    records = db.get_records_for_dataset(conn, dataset_id)
    if not records:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    data = pd.DataFrame(records)

    stats = summary.compute_stats(data)
    text = write_summary(summary.stats_to_lines(stats))

    if summary.numbers_are_valid(text, stats):
        return {"stats": stats, "summary": text, "ai-generated": True}
    return {"stats": stats, "summary": summary.template_summary(stats), "ai-generated": False}