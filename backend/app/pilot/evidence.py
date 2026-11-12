"""Only the server constructs citation metadata; never generate URL anchors."""
import json
from pathlib import PurePosixPath
import re
from urllib.parse import quote

from app.chunking.records import stable_hash
from app.chunking.tokens import count_tokens
from app.pilot.models import DraftAnswer


class InvalidEvidence(ValueError):
    pass


def build_evidence(result: dict, settings, budget: int = 3500) -> list[dict]:
    if result["snapshot_id"] != settings.snapshot_id:
        raise InvalidEvidence("Published index differs from the reviewed pilot index")
    evidence = []
    seen = set()
    for hit in result.get("context_hits", result["hits"])[:12 if getattr(settings, 'full_applications', False) else 8]:
        record = hit["chunk_record"]
        chunk_id = record["chunk_id"]
        body = {k: v for k, v in record.items() if k != "chunk_id"}
        if stable_hash(body) != chunk_id or chunk_id != hit["chunk_id"]:
            raise InvalidEvidence("Chunk identity mismatch")
        if chunk_id in seen:
            continue
        seen.add(chunk_id)
        content = record["content"]
        source = content["source"]
        path = PurePosixPath(source["source_path"])
        if (source["repository_url"] != "https://github.com/odoo/documentation.git"
                or source["odoo_version"] != "19.0" or source["language"] != "en"
                or source["commit"] != settings.source_commit
                or path.is_absolute() or ".." in path.parts
                or not str(path).startswith("content/applications/") or path.suffix != ".rst"
                or not re.fullmatch(r"[a-f0-9]{40}", source["commit"])):
            raise InvalidEvidence("Evidence outside the accepted source/version")
        passage = content["evidence_text"]
        if not isinstance(passage, str) or not passage.strip():
            continue
        item = {
            "evidence_id": f"E{len(evidence) + 1}",
            "chunk_id": chunk_id,
            "title": " › ".join(content["heading_path"]),
            "version": "19.0",
            "excerpt": passage,
            "source_path": str(path),
            "commit": source["commit"],
            "documentation_url": "https://www.odoo.com/documentation/19.0/en/"
                + quote(str(path.relative_to("content").with_suffix(".html")), safe="/"),
            "source_url": "https://github.com/odoo/documentation/blob/"
                + source["commit"] + "/" + quote(str(path), safe="/"),
        }
        if count_tokens(json.dumps([*evidence, item], ensure_ascii=False)) <= budget:
            evidence.append(item)
    return evidence


def validate_draft(draft: DraftAnswer, evidence: list[dict]) -> None:
    by_id = {e["evidence_id"]: e for e in evidence}
    if draft.status != "answered":
        if draft.claims:
            raise InvalidEvidence("Abstentions must not contain factual claims")
        if draft.status == "needs_clarification" and (
            not draft.clarification_question or not draft.clarification_question.strip()
            or len(draft.clarification_question) > 600
        ):
            raise InvalidEvidence("Clarification question missing or too long")
        return
    if not 1 <= len(draft.claims) <= 12 or draft.clarification_question is not None:
        raise InvalidEvidence("Answer must contain bounded, cited claims")
    for claim in draft.claims:
        if not claim.text.strip() or len(claim.text) > 1800 or not 1 <= len(claim.citations) <= 3:
            raise InvalidEvidence("Missing claim or citations")
        for citation in claim.citations:
            if (citation.evidence_id not in by_id or not 20 <= len(citation.quote) <= 1000
                    or citation.quote not in by_id[citation.evidence_id]["excerpt"]):
                raise InvalidEvidence("Unknown citation or quote not present in evidence")
