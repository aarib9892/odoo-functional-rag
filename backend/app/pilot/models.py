from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1800)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceReference(StrictModel):
    evidence_id: str
    quote: str


class Claim(StrictModel):
    text: str
    citations: list[EvidenceReference]


class DraftAnswer(StrictModel):
    status: Literal["answered", "needs_clarification", "insufficient_evidence"]
    claims: list[Claim]
    clarification_question: str | None


class SupportReview(StrictModel):
    supported: bool
    complete: bool
    needs_clarification: bool
    clarification_question: str | None
    issues: list[str] = Field(default_factory=list)


class QuestionInput(StrictModel):
    question: Text
    odoo_version: Annotated[str, StringConstraints(max_length=30)] = "unknown"


class LoginInput(StrictModel):
    access_key: Annotated[str, StringConstraints(min_length=1, max_length=256)]


class FeedbackInput(StrictModel):
    outcome: Literal["solved", "partially_solved", "unresolved"]
    comment: Annotated[str, StringConstraints(max_length=2000)] = ""
    task_minutes: float | None = Field(default=None, ge=0, le=1440)
