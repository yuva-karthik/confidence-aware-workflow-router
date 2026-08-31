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
- coding
- general_query

NEVER invent a category.

A request may contain MORE THAN ONE intent.

CATEGORY RULES:

coding:
Use this for ANY request involving programming,
source code, code errors, syntax errors, debugging,
algorithms, data structures, programming languages,
functions, classes, scripts, APIs, or writing code.

Examples:

"rint('hello world') is throwing an error"
→ coding

"why does my Python code crash?"
→ coding

"fix this Java function"
→ coding

"write a binary search in Python"
→ coding


technical_support:
Use this for problems with a software application,
website, device, service, or system from the user's
perspective.

Examples:

"the mobile app keeps crashing"
→ technical_support

"the website won't load"
→ technical_support


billing:
Use for charges, invoices, payments and billing.


refund:
Use for refunds, cancellations and money-back requests.


account_access:
Use for login, passwords, authentication and
account recovery.


general_query:
Use ONLY when the request does not meaningfully
belong to any of the categories above.

IMPORTANT:

If the user provides source code or describes an
error occurring in source code, prefer CODING over
technical_support or general_query.

Never create a new category.

Never merge categories into a new label.

Return all relevant intents with confidence scores.
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