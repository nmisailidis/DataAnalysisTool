import os
from openai import OpenAI

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("LLM_API_KEY", "ollama")
)
MODEL = os.getenv("LLM_MODEL", "llama3.2")


def question_to_plan(question: str, columns: list[str], numeric_columns: list[str]) -> str:
    system_prompt = (
        "You turn questions about a spreadsheet into a report plan. \n"
        f"The spreadsheet has these columns: {columns} \n"
        f"These columns hold numeric data{numeric_columns} \n"
        "Reply with JSON only, in exactly this format:\n"
        '{"group_by": "<one column name>", "columns": ["<column name>", ...]}\n'
        "Use only column names from the list above, spelled exactly the same."
    )

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    return response.choices[0].message.content


def write_summary(facts: str) -> str:
    system_prompt = (
        "You are a data analyst writing for a busy manager.\n"
        "Write a short summary of a spreadsheet in 3 to 5 sentences, based only on the facts given.\n"
        "Copy numbers exactly as they appear in the facts. Never calculate, convert or invent numbers.\n"
        "Do not add currency symbols or units that are not in the facts.\n"
        "For prices and percentages, mention averages, not totals."
    )

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": facts},
        ],

    )

    return response.choices[0].message.content
