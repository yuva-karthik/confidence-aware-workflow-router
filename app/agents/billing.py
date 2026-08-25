import os

from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2",
    base_url=os.getenv(
        "OLLAMA_BASE_URL",
        "http://host.docker.internal:11434"
    ),
    temperature=0.2
)


def billing_agent(text: str) -> str:

    response = llm.invoke([
        {
            "role": "system",
            "content": """
You are the Billing Agent.

Handle:
- Incorrect charges
- Duplicate charges
- Payment problems
- Invoices
- Billing questions
- Transaction issues

Give clear, concise and helpful responses.

Do not process refunds directly.
Refund requests belong to the Refund Agent.
"""
        },
        {
            "role": "user",
            "content": text
        }
    ])

    return response.content