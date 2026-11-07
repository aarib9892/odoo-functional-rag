import re
from time import perf_counter

from app.embeddings.cache import EmbeddingCache
from app.pilot.context import extend_context
from app.pilot.evidence import InvalidEvidence, build_evidence, validate_draft
from app.pilot.models import DraftAnswer
from app.retrieval.query import retrieve_question

MESSAGES = {
    "answered": "Guidance supported by the retrieved Odoo 19 documentation. Review it against your setup.",
    "needs_clarification": "A workflow detail is needed before giving guidance.",
    "insufficient_evidence": "The retrieved Odoo 19 evidence is not sufficient for a complete answer. Ask your Odoo consultant or narrow the task.",
}


def version_gate(question, version):
    explicit = re.findall(r"\b(?:odoo|version|v)\s*(?:v(?:ersion)?\s*)?(\d{1,2})(?:\.\d+)?\b", question, re.I)
    explicit += re.findall(r"\bodoo\s*\d{1,2}(?:\.\d+)?\s*(?:and|vs\.?|versus|/|to)\s*(\d{1,2})\b", question, re.I)
    if version not in {"19", "19.0", "unknown"} or any(v != "19" for v in explicit):
        return "This pilot supports Odoo 19 only. Can you ask about an Odoo 19 workflow?"
    if version == "unknown":
        return "Which Odoo version are you using? This pilot can provide guidance for version 19 only."
    return None


class AnswerService:
    def __init__(self, settings, generator, retriever=retrieve_question, assembler=extend_context):
        self.settings, self.generator, self.retriever = settings, generator, retriever
        self.assembler = assembler

    async def answer(self, question, version, history, request_id, client=None, telemetry=None):
        started = perf_counter()
        telemetry = telemetry if telemetry is not None else {}
        calls = telemetry.setdefault("generation", [])
        retrieval = None
        evidence = []
        gate = version_gate(question, version)
        draft = DraftAnswer(status="needs_clarification", claims=[], clarification_question=gate)
        validation = "version_gate"
        if gate is None:
            # Previous questions clarify intent, but never act as trusted evidence.
            context = [{"question": h["question"], "clarification":
                        (h.get("response") or {}).get("clarification_question")}
                       for h in history[-3:]]
            # A short follow-up needs its original task to retrieve relevant passages.
            previous = history[-1] if history else None
            followup = previous and (previous.get("response") or {}).get("status") == "needs_clarification"
            query = "\n".join([*(h["question"] for h in history[-3:]), "Clarification: " + question]) if followup else question
            retrieval = await self.retriever(
                query, EmbeddingCache(self.settings.query_cache), "odoo19", 5, client=client)
            telemetry["embedding"] = retrieval.get("query_embedding")
            retrieval = await self.assembler(query, retrieval, self.settings)
            telemetry["context_policy"] = retrieval.get("context_policy")
            telemetry["support_chunk_ids"] = retrieval.get("support_chunk_ids", [])
            evidence = build_evidence(retrieval, self.settings)
            telemetry["evidence_chunk_ids"] = [e["chunk_id"] for e in evidence]
            draft = DraftAnswer(status="insufficient_evidence", claims=[], clarification_question=None)
            validation = "empty_evidence"
            if evidence:
                payload = {"question": question, "odoo_version": "19.0",
                           "conversation": context, "evidence": evidence}
                draft, usage = await self.generator.draft(payload)
                calls.append({"stage": "draft", **usage})
                audit = telemetry.setdefault("_audit", {})
                audit["draft"] = draft.model_dump()
                try:
                    validate_draft(draft, evidence)
                    validation = "citations_validated"
                    if draft.status == "answered":
                        review, usage = await self.generator.review({**payload, "draft": draft.model_dump()})
                        calls.append({"stage": "support_review", **usage})
                        audit["review"] = review.model_dump()
                        if review.needs_clarification and review.clarification_question:
                            draft = DraftAnswer(status="needs_clarification", claims=[],
                                                clarification_question=review.clarification_question)
                            validate_draft(draft, evidence)
                            validation = "review_needs_clarification"
                        elif not review.supported or not review.complete or review.needs_clarification:
                            draft = DraftAnswer(status="insufficient_evidence", claims=[], clarification_question=None)
                            validation = "support_review_rejected"
                        else:
                            validation = "citations_and_model_support_review_passed"
                except InvalidEvidence as error:
                    audit["rejection"] = str(error)
                    draft = DraftAnswer(status="insufficient_evidence", claims=[], clarification_question=None)
                    validation = "citation_validation_rejected"
        used = {c.evidence_id for claim in draft.claims for c in claim.citations}
        return {
            "request_id": request_id, **draft.model_dump(), "message": MESSAGES[draft.status],
            "supported_version": "19.0", "citations": [e for e in evidence if e["evidence_id"] in used],
            "trace": {**{k: v for k, v in telemetry.items() if not k.startswith("_")},
                "latency_ms": round((perf_counter() - started) * 1000),
                "snapshot_id": retrieval["snapshot_id"] if retrieval else None,
                "retrieval_k": 5, "evidence_count": len(evidence),
                "embedding": retrieval.get("query_embedding") if retrieval else None,
                "generation": calls, "validation": validation,
            },
        }
