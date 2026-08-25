# CAWR

## Confidence-Aware Workflow Router

CAWR is an agentic routing system that classifies incoming requests into a **closed set of categories**, evaluates classification confidence, and deterministically routes high-confidence requests to the appropriate specialist agent.

Low-confidence requests are sent to a **human review path** instead of being automatically routed.

The system uses **Llama 3.2**, Ollama, LangGraph, and Docker.

---

## Architecture

```text
                         User Input
                             │
                             ▼
                    ┌─────────────────┐
                    │   Router Agent  │
                    │    Llama 3.2   │
                    └────────┬────────┘
                             │
                    Category + Confidence
                             │
                             ▼
                    ┌─────────────────┐
                    │ Confidence Gate │
                    └───────┬─────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
              HIGH                   LOW
                 │                     │
                 ▼                     ▼
        ┌────────────────┐      ┌──────────────┐
        │ Routing Table  │      │ Human Review │
        └───────┬────────┘      └──────┬───────┘
                │                      │
        ┌───────┼────────┬────────┐    │
        ▼       ▼        ▼        ▼    │
     Billing  Refund  Technical Account│
       Agent   Agent    Agent    Agent  │
        │       │        │        │     │
        └───────┴────────┴────────┴─────┘
                         │
                         ▼
                       Result
```

---

## Core Concept

CAWR deliberately separates **classification** from **routing**.

The Llama 3.2 Router Agent answers:

> "What category does this request belong to?"

It does **not** decide which agent to invoke.

The routing table answers:

> "Which workflow handles this category?"

This makes routing deterministic, inspectable, and easy to modify.

---

## Closed-Set Classification

The router can only return categories defined by the system.

Current categories:

| Category            | Purpose                                         |
| ------------------- | ----------------------------------------------- |
| `billing`           | Charges, invoices, payments and billing issues  |
| `refund`            | Refunds, cancellations and money-back requests  |
| `technical_support` | Software errors, crashes and technical problems |
| `account_access`    | Login, password and account recovery            |
| `general_query`     | General requests outside the other categories   |

Categories are represented using a Pydantic enum, preventing the model from inventing arbitrary routing labels.

---


## Confidence-Aware Routing

Every classification produces:

```json
{
  "category": "billing",
  "confidence": 0.91
}
```

The confidence gate determines what happens next.

```text
confidence >= threshold
        │
        ▼
   Automatic Routing

confidence < threshold
        │
        ▼
    Human Review
```

The current default threshold is:

```text
0.70
```

This can be adjusted depending on evaluation results.

---

## Human-in-the-Loop

When classification confidence is too low, CAWR does not blindly execute an agent.

Instead:

```text
User Request
     ↓
Router
     ↓
Low Confidence
     ↓
Human Review
     ↓
Correct Category
     ↓
Specialist Agent
```

The reviewer selects from the same closed category set used by the router.

This keeps the system's routing space consistent.

---

## Agents

CAWR currently contains specialist agents for:

### Router Agent

Classifies requests and returns:

* category
* confidence

It does not execute workflows.

### Billing Agent

Handles:

* payment issues
* incorrect charges
* duplicate charges
* invoices
* billing questions

### Refund Agent

Handles:

* refund requests
* cancellations
* money-back requests
* refund status

### Technical Support Agent

Handles:

* application errors
* crashes
* bugs
* configuration problems
* troubleshooting

### Account Access Agent

Handles:

* login issues
* forgotten passwords
* locked accounts
* authentication
* account recovery

---

## Technology Stack

* **Python**
* **Llama 3.2**
* **Ollama**
* **LangChain**
* **LangGraph**
* **Pydantic**
* **PyYAML**
* **Docker**
* **scikit-learn**
* **Pandas**

Ollama runs natively on the host machine while the CAWR application runs inside Docker.

---


## Prerequisites

Install the following on the host:

* Docker Desktop
* Ollama

Pull Llama 3.2:

```bash
ollama pull llama3.2
```

Verify:

```bash
ollama list
```

You should see:

```text
llama3.2
```

---

## Running the Project

Clone the repository:

```bash
git clone <repository-url>
cd confidence-aware-workflow-router
```

Build the Docker image:

```bash
docker compose build
```

Run the interactive router:

```bash
docker compose run --rm router
```

The application should display:

```text
============================================================
              P18 - A ROUTER
============================================================

Available commands:
  Type a request to route it
  'exit' or 'quit' to stop
------------------------------------------------------------

User:
```

---

## Example

Input:

```text
I was charged twice for my order
```

Possible result:

```text
============================================================
ROUTER RESULT
============================================================

Category   : billing
Confidence : 91.00%
Status     : completed
Workflow   : billing

Agent Response:
...
```

---

## Low-Confidence Example

Input:

```text
Something is wrong with my payment
```

If the classifier is uncertain:

```text
Category   : billing
Confidence : 52.00%
Status     : human_review
```

The request is then presented to the human reviewer rather than being automatically executed.

---
