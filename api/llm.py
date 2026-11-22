from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "llama3.2"


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
