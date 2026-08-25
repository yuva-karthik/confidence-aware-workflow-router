from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    BILLING = "billing"
    REFUND = "refund"
    TECHNICAL = "technical_support"
    ACCOUNT = "account_access"
    GENERAL = "general_query"


class Intent(BaseModel):
    category: Category
    confidence: float = Field(
        ge=0.0,
        le=1.0
    )


class Classification(BaseModel):
    intents: list[Intent]