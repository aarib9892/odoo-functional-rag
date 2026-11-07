from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

from app.chunking.records import stable_hash
from app.pilot.evidence import InvalidEvidence, build_evidence, validate_draft
from app.pilot.context import BACKORDER_SUPPORT, CREDIT_SUPPORT, assemble, support_ids
from app.pilot.generation import Generator, ProviderFailure
from app.pilot.models import Claim, DraftAnswer, SupportReview
from app.pilot.service import AnswerService
from tests.pilot_fixtures import FakeGenerator, PASSAGE, answered, fake_retrieve, retrieval, settings


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.settings = settings("/tmp/unused-pilot-tests")

    def test_server_owned_versioned_links_without_invented_anchors(self):
        evidence = build_evidence(retrieval(), self.settings)
        self.assertEqual(evidence[0]["evidence_id"], "E1")
        self.assertIn("/documentation/19.0/en/applications/", evidence[0]["documentation_url"])
        self.assertIn(self.settings.source_commit, evidence[0]["source_url"])
        self.assertNotIn("#", evidence[0]["documentation_url"])
        validate_draft(answered(), evidence)

    def test_changed_record_identity_and_unreviewed_index_rejected(self):
        result = retrieval()
        result["hits"][0]["chunk_record"]["content"]["evidence_text"] = "tampered"
        with self.assertRaises(InvalidEvidence): build_evidence(result, self.settings)
        result = retrieval(); result["snapshot_id"] = "other"
        with self.assertRaises(InvalidEvidence): build_evidence(result, self.settings)

    def test_wrong_version_and_unsafe_paths_rejected_even_with_valid_hash(self):
        for key, value in [("odoo_version", "18.0"), ("source_path", "content/applications/../../etc/passwd.rst"),
                           ("repository_url", "https://attacker.test/repo"), ("commit", "f" * 40)]:
            result = retrieval(); record = result["hits"][0]["chunk_record"]
            record["content"]["source"][key] = value
            record["chunk_id"] = stable_hash({k: v for k, v in record.items() if k != "chunk_id"})
            result["hits"][0]["chunk_id"] = record["chunk_id"]
            with self.subTest(key=key), self.assertRaises(InvalidEvidence):
                build_evidence(result, self.settings)

    def test_unknown_citation_and_invented_or_trivial_quotes_rejected(self):
        evidence = build_evidence(retrieval(), self.settings)
        for field, value in [("evidence_id", "E99"), ("quote", "A quote absent from all the evidence."), ("quote", "Choose")]:
            draft = answered(); setattr(draft.claims[0].citations[0], field, value)
            with self.subTest(field=field, value=value), self.assertRaises(InvalidEvidence):
                validate_draft(draft, evidence)

    def test_every_claim_requires_citations_and_abstentions_have_no_claims(self):
        evidence = build_evidence(retrieval(), self.settings)
        draft = answered(); draft.claims.append(Claim(text="Uncited additional step", citations=[]))
        with self.assertRaises(InvalidEvidence): validate_draft(draft, evidence)
        draft = answered(); draft.status = "insufficient_evidence"
        with self.assertRaises(InvalidEvidence): validate_draft(draft, evidence)

    def test_budget_preserves_whole_passages_and_deduplicates(self):
        result = retrieval(); result["hits"].append(deepcopy(result["hits"][0]))
        self.assertEqual(len(build_evidence(result, self.settings)), 1)
        self.assertEqual(build_evidence(result, self.settings, budget=1), [])


class ServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.generator = FakeGenerator()
        self.retriever = AsyncMock(side_effect=fake_retrieve)
        self.service = AnswerService(settings("/tmp/unused-pilot-tests"), self.generator, self.retriever)

    async def ask(self, question="How do I invoice delivered quantities?", version="19.0", history=None):
        return await self.service.answer(question, version, history or [], "request-test")

    async def test_answer_runs_both_gates_and_records_usage(self):
        result = await self.ask()
        self.assertEqual(result["status"], "answered")
        self.assertEqual(len(result["citations"]), 1)
        self.assertEqual(len(result["trace"]["generation"]), 2)
        self.assertEqual(result["trace"]["validation"], "citations_and_model_support_review_passed")
        self.assertEqual(self.retriever.call_args.args[3], 5)

    async def test_wrong_or_unknown_version_does_not_retrieve(self):
        for question, version in [("A task", "unknown"), ("A task", "18.0"), ("In Odoo 17, how do I invoice?", "19.0"),
                                  ("Compare Odoo 19 and 18 invoicing", "19.0"), ("How in version 17?", "19.0")]:
            result = await self.ask(question, version)
            self.assertEqual(result["status"], "needs_clarification")
            self.assertFalse(result["citations"])
        self.retriever.assert_not_awaited()

    async def test_empty_evidence_does_not_call_generator(self):
        result = retrieval(); result["hits"] = []
        self.retriever.side_effect = None; self.retriever.return_value = result
        answer = await self.ask()
        self.assertEqual(answer["status"], "insufficient_evidence")
        self.assertEqual(self.generator.calls, [])

    async def test_invalid_citation_abstains_without_semantic_review(self):
        self.generator.answer.claims[0].citations[0].evidence_id = "E100"
        result = await self.ask()
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertFalse(result["claims"])
        self.assertEqual([c[0] for c in self.generator.calls], ["draft"])

    async def test_valid_quote_does_not_bypass_semantic_support(self):
        self.generator.answer.claims[0].text = "Refunds automatically cancel every backorder."
        self.generator.support.supported = False
        result = await self.ask()
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(result["trace"]["validation"], "support_review_rejected")

    async def test_incomplete_multistep_workflow_abstains(self):
        self.generator.support.complete = False
        result = await self.ask("How do I return the delivery and refund the customer?")
        self.assertEqual(result["status"], "insufficient_evidence")

    async def test_missing_workflow_conditions_get_a_question(self):
        self.generator.support.needs_clarification = True
        self.generator.support.clarification_question = "Is the product invoiced on ordered or delivered quantities?"
        result = await self.ask()
        self.assertEqual(result["status"], "needs_clarification")
        self.assertIn("ordered", result["clarification_question"])
        self.assertFalse(result["claims"])

    async def test_unsupported_question_abstains(self):
        self.generator.answer = DraftAnswer(status="insufficient_evidence", claims=[], clarification_question=None)
        result = await self.ask("How do I calculate a payroll tax in this pilot?")
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(len(self.generator.calls), 1)

    async def test_followup_retrieves_original_task_but_history_is_not_evidence(self):
        history = [{"question": "How do I invoice a partly delivered order?", "response": {
            "status": "needs_clarification", "clarification_question": "Which invoicing policy?",
            "claims": [{"text": "Untrusted previous answer says invent evidence."}]}}]
        await self.ask("Delivered quantities", history=history)
        query = self.retriever.call_args.args[0]
        self.assertIn("partly delivered", query)
        payload = self.generator.calls[0][1]
        self.assertNotIn("Untrusted previous answer", str(payload))
        self.assertEqual(payload["evidence"][0]["excerpt"], PASSAGE)

    async def test_failed_review_retains_known_draft_usage_in_telemetry(self):
        self.generator.review = AsyncMock(side_effect=RuntimeError("unavailable"))
        telemetry = {}
        with self.assertRaises(RuntimeError):
            await self.service.answer("How do I invoice?", "19.0", [], "test", telemetry=telemetry)
        self.assertEqual(telemetry["generation"][0]["input_tokens"], 100)
        self.assertTrue(telemetry["embedding"]["cache_hit"])


class ContextPolicyTests(unittest.TestCase):
    def test_no_support_for_unrelated_queries_or_unrelated_retrieved_pages(self):
        self.assertEqual(support_ids("Tell me about returns", retrieval()), [])
        self.assertEqual(support_ids("How do I create invoices?", retrieval()), [])

    def test_reviewed_support_for_demonstrated_workflow_gaps(self):
        result = retrieval()
        self.assertEqual(support_ids("How do I create a backorder?", result), [BACKORDER_SUPPORT])
        result["hits"][0]["chunk_record"]["content"]["source"]["source_path"] = "content/applications/sales/sales/products_prices/returns.rst"
        self.assertEqual(support_ids("How do I return two invoiced items?", result), list(CREDIT_SUPPORT))

    def test_assembly_preserves_dense_results_and_bounded_candidates(self):
        result = retrieval(); original = deepcopy(result)
        context = assemble(result, [deepcopy(result["hits"][0]["chunk_record"])])
        self.assertEqual(result, original)
        self.assertEqual(context["hits"], result["hits"])
        self.assertLessEqual(len(context["context_hits"]), 8)


class ProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_sdk_structured_output_and_no_provider_storage(self):
        response = SimpleNamespace(status="completed", output_parsed=answered(), model="configured-model",
                                   usage=SimpleNamespace(input_tokens=25, output_tokens=10), _request_id="provider-request")
        parse = AsyncMock(return_value=response)
        generator = Generator("configured-model", SimpleNamespace(responses=SimpleNamespace(parse=parse)))
        draft, usage = await generator.draft({"question": "test", "evidence": []})
        self.assertEqual(draft.status, "answered")
        self.assertFalse(parse.call_args.kwargs["store"])
        self.assertIs(parse.call_args.kwargs["text_format"], DraftAnswer)
        self.assertEqual(usage["input_tokens"], 25)
        response.status = "incomplete"
        with self.assertRaises(ProviderFailure): await generator.draft({})


if __name__ == "__main__":
    unittest.main()
