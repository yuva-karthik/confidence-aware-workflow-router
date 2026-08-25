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


def refund_agent(text: str) -> str:

    response = llm.invoke([
        {
            "role": "system",
            "content": """
You are the Refund Agent.

Handle:
- Refund requests
- Order cancellation
- Money-back requests
- Refund status
- Return-related payment questions

Give clear, concise and helpful responses.

Do not handle general billing questions
unless they are specifically about obtaining
or checking a refund.
"""
        },
        {
            "role": "user",
            "content": text
        }
    ])

    return response.content