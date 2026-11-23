# Data Analysis Tool

A Python tool for analysing Excel data, with a desktop app and a REST API.
Load an Excel file or a Google Sheets link, group the data by any column and sum
the number columns, or ask a question in plain language and let an LLM turn it
into a report.

![CI](https://github.com/nmisailidis/DataAnalysisTool/actions/workflows/ci.yml/badge.svg)

## Features

- Upload `.xlsx` files, or load from a local path or a Google Sheets link
- Store datasets in SQLite and browse them and their rows
- Group-by reports that sum the chosen number columns
- **`/ask`:** ask a question in plain language → the LLM returns a report plan →
  the plan is validated → the report runs
- **`/summary`:** a short written summary of a dataset, with every number checked
  against values computed by pandas
- A desktop app (Tkinter) and a REST API (FastAPI) sharing the same logic

## Architecture

```text
Tkinter GUI (dataAnalysis.py) ──┐
                                ├──> core/ (load, report, summary) ──> database.py (SQLite)
FastAPI API (api/main.py) ──────┘
        │
        └──> api/llm.py ──> LLM (Ollama by default, any OpenAI-compatible API)
```

- **core/**: the business logic, with no UI code, shared by the GUI and the API
- **database.py**: storage; each row is saved as JSON, so any spreadsheet works without a fixed schema
- **api/llm.py**: the only place that talks to the LLM

## How the LLM is kept under control

**`/ask`**

1. The LLM receives the question and the column names. **Data rows are never sent.**
2. It replies with a JSON plan: `{"group_by": "...", "columns": [...]}`.
3. The plan is validated with the same Pydantic model a user sends to `/report`.
   An invalid plan returns **502**.
4. Columns that aren't numeric are removed in code, because small models don't always follow the prompt.
5. The plan runs through the same report function as the manual endpoint.
6. The response includes the plan, so the user can see how the question was understood.

The LLM never writes or runs code; it only fills in a plan that the application checks.

**`/summary`**

pandas computes the statistics, and the LLM only writes the text. Every number in
the text is checked against the computed values; if any number doesn't match, a
summary built by code is returned instead, and the response says so (`"ai_generated": false`).

## Run with Docker (one command)

Requires only [Docker](https://www.docker.com/products/docker-desktop/).

```powershell
docker compose up --build
```

This starts the API and an Ollama container, and downloads the `llama3.2` model
automatically. **The first start downloads about 5 GB**; later starts take seconds.

Open http://127.0.0.1:8000/docs. Wait until the Ollama logs show the model download
has finished before using `/ask` or `/summary`.

Stop with `Ctrl+C`, then `docker compose down`.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Install [Ollama](https://ollama.com/download) and run `ollama pull llama3.2`. Then:

```powershell
fastapi dev api/main.py      # the API, docs at http://127.0.0.1:8000/docs
python dataAnalysis.py       # the desktop app
```

## Using another LLM provider

The LLM is configured with environment variables, so no code changes are needed:

| Variable | Default |
| --- | --- |
| `LLM_BASE_URL` | `http://localhost:11434/v1` (local Ollama) |
| `LLM_API_KEY` | `ollama` |
| `LLM_MODEL` | `llama3.2` |

For OpenAI or Azure OpenAI, set these to the provider's URL, your key and a model name.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| GET | `/datasets` | List stored datasets |
| GET | `/datasets/{dataset_id}/records` | Rows of one dataset |
| POST | `/datasets/upload` | Upload an `.xlsx` file |
| POST | `/datasets/from-url` | Load from a path or Google Sheets link |
| POST | `/datasets/{dataset_id}/report` | Group-by report from chosen columns |
| POST | `/datasets/{dataset_id}/ask` | Report from a plain-language question |
| GET | `/datasets/{dataset_id}/summary` | Written summary with checked numbers |

## Example

`POST /datasets/1/ask`

```json
{"question": "What is the total quantity sold per region?"}
```

Response:

```json
REPLACE THIS WITH A REAL RESPONSE FROM YOUR Orders.xlsx
```

## Tests

```powershell
python -m pytest -v
```

The tests use a temporary database and a fake LLM, so they don't need Ollama.
GitHub Actions runs them on every push.

## Tech stack

Python 3.12 · FastAPI · Pydantic · pandas · SQLite · Tkinter · OpenAI Python SDK ·
Ollama · pytest · Docker · GitHub Actions

## Next steps

- Continuous deployment: build the Docker image in CI and deploy to Azure
- Keep the API's database in a Docker volume, so data survives restarts
- Choose the aggregation in reports (sum, average, count), not only sum
- Handle messy number formats in Excel files (e.g. decimal commas)
- An Angular frontend

## Author

Nikos Misailidis 
