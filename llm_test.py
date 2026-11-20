from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

response = client.chat.completions.create(
    model="llama3.2",
    messages=[
        {"role": "system", "content": "You are a helpful data analyst."},
        {"role": "user", "content": "In onesentence, what is a pivot table?"},
    ],
)

print(response.choices[0].message.content)