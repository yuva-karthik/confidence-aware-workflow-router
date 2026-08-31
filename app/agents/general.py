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


def general_agent(text: str) -> str:

    response = llm.invoke([
        {
            "role": "system",
            "content": """
You are the General Query Agent.

Handle general questions that do not clearly
belong to billing, refunds, technical support,
account access, or coding.

Give a concise and helpful response.
"""
        },
        {
            "role": "user",
            "content": text
        }
    ])

    return response.content