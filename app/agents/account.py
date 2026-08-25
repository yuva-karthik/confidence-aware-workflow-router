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


def account_agent(text: str) -> str:

    response = llm.invoke([
        {
            "role": "system",
            "content": """
You are the Account Access Agent.

Handle:
- Login problems
- Forgotten passwords
- Locked accounts
- Account recovery
- Authentication issues

Give clear, concise and helpful responses.

Do not handle billing, refunds,
or technical product problems.
"""
        },
        {
            "role": "user",
            "content": text
        }
    ])

    return response.content