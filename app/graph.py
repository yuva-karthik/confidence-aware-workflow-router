import yaml
from typing import Optional, TypedDict

from langgraph.graph import StateGraph, END

from agents.router import classify
from agents.billing import billing_agent
from agents.refund import refund_agent
from agents.technical import technical_agent
from agents.account import account_agent


class RouterState(TypedDict):
    input: str
    intents: Optional[list]
    category: Optional[str]
    confidence: Optional[float]
    status: Optional[str]
    workflow: Optional[str]
    result: Optional[str]


with open("routing.yaml", "r") as f:
    ROUTING_TABLE = yaml.safe_load(f)["routes"]


# --------------------------------------------------
# CLASSIFIER
# --------------------------------------------------

def classifier_node(state: RouterState):

    classification = classify(state["input"])

    intents = [
        {
            "category": intent.category.value,
            "confidence": intent.confidence
        }
        for intent in classification.intents
    ]

    return {
        "intents": intents
    }


# --------------------------------------------------
# CONFIDENCE / MULTI-INTENT GATE
# --------------------------------------------------

def confidence_node(state: RouterState):

    intents = state["intents"]

    if not intents:
        return {
            "status": "human_review"
        }

    # Multiple intents automatically require review
    if len(intents) > 1:
        return {
            "status": "human_review"
        }

    # Single low-confidence intent
    if intents[0]["confidence"] < 0.70:
        return {
            "status": "human_review"
        }

    return {
        "status": "approved",
        "category": intents[0]["category"],
        "confidence": intents[0]["confidence"]
    }


# --------------------------------------------------
# ROUTING DECISION
# --------------------------------------------------

def route_decision(state: RouterState):

    if state["status"] == "human_review":
        return "human_review"

    category = state["category"]

    if category not in ROUTING_TABLE:
        return "human_review"

    return category


# --------------------------------------------------
# BILLING
# --------------------------------------------------

def billing_node(state: RouterState):

    return {
        "workflow": ROUTING_TABLE["billing"]["agent"],
        "result": billing_agent(state["input"]),
        "status": "completed"
    }


# --------------------------------------------------
# REFUND
# --------------------------------------------------

def refund_node(state: RouterState):

    return {
        "workflow": ROUTING_TABLE["refund"]["agent"],
        "result": refund_agent(state["input"]),
        "status": "completed"
    }


# --------------------------------------------------
# TECHNICAL
# --------------------------------------------------

def technical_node(state: RouterState):

    return {
        "workflow": ROUTING_TABLE["technical_support"]["agent"],
        "result": technical_agent(state["input"]),
        "status": "completed"
    }


# --------------------------------------------------
# ACCOUNT
# --------------------------------------------------

def account_node(state: RouterState):

    return {
        "workflow": ROUTING_TABLE["account_access"]["agent"],
        "result": account_agent(state["input"]),
        "status": "completed"
    }


# --------------------------------------------------
# HUMAN REVIEW
# --------------------------------------------------

def human_review_node(state: RouterState):

    print("\n")
    print("=" * 60)
    print("              HUMAN REVIEW")
    print("=" * 60)

    print(f"Input: {state['input']}")

    print("\nDetected intents:")

    intents = state["intents"]

    for i, intent in enumerate(intents, start=1):

        print(
            f"  {i}. "
            f"{intent['category']} "
            f"({intent['confidence']:.2%})"
        )

    print("\nAvailable categories:")

    categories = list(ROUTING_TABLE.keys())

    for i, category in enumerate(categories, start=1):

        print(
            f"  {i}. {category}"
        )

    print(
        "\nSelect the category to route to:"
    )

    while True:

        choice = input(
            "\nYour choice: "
        ).strip()

        try:

            index = int(choice) - 1

            if 0 <= index < len(categories):

                corrected_category = categories[index]

                break

        except ValueError:
            pass

        print("Invalid choice. Try again.")

    return {
        "category": corrected_category,
        "confidence": 1.0,
        "status": "human_corrected"
    }


# --------------------------------------------------
# BUILD GRAPH
# --------------------------------------------------

def build_graph():

    builder = StateGraph(RouterState)

    builder.add_node(
        "classifier",
        classifier_node
    )

    builder.add_node(
        "confidence",
        confidence_node
    )

    builder.add_node(
        "billing",
        billing_node
    )

    builder.add_node(
        "refund",
        refund_node
    )

    builder.add_node(
        "technical_support",
        technical_node
    )

    builder.add_node(
        "account_access",
        account_node
    )

    builder.add_node(
        "human_review",
        human_review_node
    )

    builder.set_entry_point(
        "classifier"
    )

    builder.add_edge(
        "classifier",
        "confidence"
    )

    builder.add_conditional_edges(
        "confidence",
        route_decision,
        {
            "billing": "billing",
            "refund": "refund",
            "technical_support": "technical_support",
            "account_access": "account_access",
            "human_review": "human_review"
        }
    )

    builder.add_edge(
        "billing",
        END
    )

    builder.add_edge(
        "refund",
        END
    )

    builder.add_edge(
        "technical_support",
        END
    )

    builder.add_edge(
        "account_access",
        END
    )

    # Human review needs to route again
    builder.add_conditional_edges(
        "human_review",
        lambda state: state["category"],
        {
            "billing": "billing",
            "refund": "refund",
            "technical_support": "technical_support",
            "account_access": "account_access"
        }
    )

    return builder.compile()


graph = build_graph()