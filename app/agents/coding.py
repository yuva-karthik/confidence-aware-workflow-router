import os

from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen2.5-coder:7b",
    base_url=os.getenv(
        "OLLAMA_BASE_URL",
        "http://host.docker.internal:11434"
    ),
    temperature=0.1
)


def coding_agent(text: str) -> str:
    response = llm.invoke([
        {
            "role": "system",
            "content": """
You are the Coding Agent.

Handle requests involving:
- writing code
- debugging code
- explaining code
- algorithms
- data structures
- programming errors
- code refactoring
- implementation questions

Give practical, technically correct answers.

When useful:
- provide code snippets
- explain the cause of bugs
- suggest improvements
- mention assumptions

Do not handle billing, refunds,
account access, or general support issues.
"""
        },
        {
            "role": "user",
            "content": text
        }
    ])

    return response.content