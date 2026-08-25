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
    category: Optional[str]
    confidence: Optional[float]
    status: Optional[str]
    workflow: Optional[str]
    result: Optional[str]


with open("routing.yaml", "r") as f:
    ROUTING_TABLE = yaml.safe_load(f)["routes"]


def classifier_node(state: RouterState):

    classification = classify(state["input"])

    return {
        "category": classification.category.value,
        "confidence": classification.confidence
    }


def confidence_node(state: RouterState):

    confidence = state["confidence"]

    if confidence is None or confidence < 0.70:
        return {
            "status": "human_review"
        }

    return {
        "status": "approved"
    }


def route_decision(state: RouterState):

    if state["status"] == "human_review":
        return "human_review"

    category = state["category"]

    if category not in ROUTING_TABLE:
        return "human_review"

    return category


def billing_node(state: RouterState):

    return {
        "workflow": ROUTING_TABLE["billing"]["agent"],
        "result": billing_agent(state["input"]),
        "status": "completed"
    }


def refund_node(state: RouterState):

    return {
        "workflow": ROUTING_TABLE["refund"]["agent"],
        "result": refund_agent(state["input"]),
        "status": "completed"
    }


def technical_node(state: RouterState):

    return {
        "workflow": ROUTING_TABLE["technical_support"]["agent"],
        "result": technical_agent(state["input"]),
        "status": "completed"
    }


def account_node(state: RouterState):

    return {
        "workflow": ROUTING_TABLE["account_access"]["agent"],
        "result": account_agent(state["input"]),
        "status": "completed"
    }


def human_review_node(state: RouterState):

    print("\n")
    print("=" * 60)
    print("              HUMAN REVIEW")
    print("=" * 60)

    print(f"Input      : {state['input']}")
    print(f"Prediction : {state['category']}")
    print(f"Confidence : {state['confidence']:.2%}")

    print("\nSelect the correct category:")

    categories = list(ROUTING_TABLE.keys())

    for i, category in enumerate(categories, start=1):
        print(f"  {i}. {category}")

    while True:

        choice = input("\nYour choice: ").strip()

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
        "status": "human_corrected"
    }


def corrected_route(state: RouterState):

    category = state["category"]

    return category


def build_graph():

    builder = StateGraph(RouterState)

    # Nodes
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

    # Entry
    builder.set_entry_point("classifier")

    # Classifier → confidence
    builder.add_edge(
        "classifier",
        "confidence"
    )

    # Confidence → route
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

    # Normal workflows
    builder.add_edge("billing", END)
    builder.add_edge("refund", END)
    builder.add_edge("technical_support", END)
    builder.add_edge("account_access", END)

    # Human review → corrected route
    builder.add_conditional_edges(
        "human_review",
        corrected_route,
        {
            "billing": "billing",
            "refund": "refund",
            "technical_support": "technical_support",
            "account_access": "account_access"
        }
    )

    return builder.compile()


graph = build_graph()