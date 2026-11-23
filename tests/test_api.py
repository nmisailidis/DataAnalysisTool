import sqlite3

import pandas as pd
import pytest
from fastapi.testclient import TestClient

import database as db
from api.main import app, get_db


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"
    db.init_db(str(db_path))

    def get_test_db():
        conn = sqlite3.connect(db_path, check_same_thread=False)
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app), db_path
    app.dependency_overrides.clear()


def add_dataset(db_path):
    data = pd.DataFrame({
        "Category": ["Drinks", "Drinks", "Food"],
        "Product": ["Coffee", "Tea", "Cake"],
        "Quantity": [10, 5, 8],
    })

    conn = sqlite3.connect(db_path)
    dataset_id = db.save_dataset(conn, "test.xlsx", "upload", data)
    conn.close()
    return dataset_id


def test_health(client):
    test_client, _ = client
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_report_unknown_dataset_returns_404(client):
    test_client, _ = client
    response = test_client.post("/datasets/999/report", json={"group_by": "Category", "columns": ["Quantity"]})
    assert response.status_code == 404


def test_ask_with_fake_llm(client, monkeypatch):
    test_client, db_path = client
    dataset_id = add_dataset(db_path)
    monkeypatch.setattr("api.main.question_to_plan",
                        lambda question, columns, numeric_columns: '{"group_by": "Category", "columns": ["Quantity"]}')

    response = test_client.post(f"/datasets/{dataset_id}/ask", json={"question": "Quantity per category?"})

    assert response.status_code == 200
    assert response.json()["result"] == [
        {"Category": "Drinks", "Quantity": 15},
        {"Category": "Food", "Quantity": 8},
    ]


def test_ask_invalid_plan_returns_502(client, monkeypatch):
    test_client, db_path = client
    dataset_id = add_dataset(db_path)
    monkeypatch.setattr("api.main.question_to_plan",
                        lambda question, columns, numeric_columns: "Sorry, I don't know")

    response = test_client.post(f"/datasets/{dataset_id}/ask", json={"question": "anything"})

    assert response.status_code == 502


def test_ask_removes_text_columns_from_plan(client, monkeypatch):
    test_client, db_path = client
    dataset_id = add_dataset(db_path)
    monkeypatch.setattr("api.main.question_to_plan",
                        lambda question, columns, numeric_columns: '{"group_by": "Category", "columns": ["Product", "Quantity"]}')

    response = test_client.post(f"/datasets/{dataset_id}/ask", json={"question": "Products and quantity per category?"})

    assert response.status_code == 200
    assert response.json()["plan"]["columns"] == ["Quantity"]
