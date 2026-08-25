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

Your job is to identify ALL relevant intents
in the user's request.

You may ONLY use these categories:

- billing
- refund
- technical_support
- account_access
- general_query

NEVER invent a category.

A request may contain MORE THAN ONE intent.

Example:

"The application has bugs and my invoice
was not generated."

This contains:

1. technical_support
2. billing

Return BOTH categories.

For every detected intent return:
- category
- confidence between 0 and 1

Rules:

1. If exactly one category clearly applies,
   return one intent.

2. If multiple categories independently apply,
   return all relevant intents.

3. If the request is unclear, return the
   most relevant category with an appropriate
   confidence score.

4. Never merge categories into a new category.

5. NEVER create categories such as:
   "billing_technical"
   "technical_billing"
   "invoice_bug"
   "payment_issue"

The category set is CLOSED.
"""


def classify(text: str) -> Classification:

    return classifier.invoke([
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": text
        }
    ])