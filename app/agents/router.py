import os

from langchain_ollama import ChatOllama

from schemas import Classification


llm = ChatOllama(
    model="llama3.2",
    base_url=os.getenv(
        "OLLAMA_BASE_URL",
        "http://host.docker.internal:11434"
    ),
    temperature=0
)


classifier = llm.with_structured_output(
    Classification
)


SYSTEM_PROMPT = """
You are the Router Agent.

Your ONLY responsibility is to classify the
user's request into exactly ONE category.

Allowed categories:

1. billing
2. refund
3. technical_support
4. account_access
5. general_query

You MUST NOT invent a category.

You MUST NOT create a workflow.

You MUST NOT select an agent.

You MUST NOT solve the user's problem.

Return:
- category
- confidence between 0 and 1

Classification rules:

billing:
Payment, charges, invoices, duplicate charges,
incorrect charges or billing questions.

refund:
Refunds, cancellations, returns involving money,
money-back requests or refund status.

technical_support:
Software errors, crashes, bugs,
configuration and technical problems.

account_access:
Login, password, authentication,
account lockout and account recovery.

general_query:
Questions that don't belong to the
other categories.
"""


def classify(text: str) -> Classification:

    result = classifier.invoke([
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": text
        }
    ])

    return result