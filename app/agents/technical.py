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


def technical_agent(text: str) -> str:

    response = llm.invoke([
        {
            "role": "system",
            "content": """
You are the Technical Support Agent.

Handle:
- Application errors
- Software bugs
- Crashes
- Feature failures
- Configuration problems
- Technical troubleshooting

Give step-by-step troubleshooting
when appropriate.

Do not handle billing, refunds,
or account recovery.
"""
        },
        {
            "role": "user",
            "content": text
        }
    ])

    return response.content