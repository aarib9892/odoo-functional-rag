import json
from pathlib import Path
import unittest

from app.chunking.drafts import iter_chunk_drafts
from app.chunking.grouping import (
    attach_images,
    iter_section_groups,
    merge_drafts,
)
from app.chunking.packing import pack_section
from app.chunking.tokens import count_tokens
from app.chunking.walk import iter_blocks


class PackingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        project = Path(__file__).resolve().parents[2]
        snapshot = (
            project
            / "data/normalized/corpus"
            / ("15fce1c26f99a9d986c792aeae260e329519a830ee329c1aa263ad962196c7cc")
        )
        relative = Path(
            "content/applications/sales/sales/invoicing/invoicing_policy.json"
        )
        document = json.loads(
            (snapshot / "documents" / relative).read_text(encoding="utf-8")
        )

        kinds = {
            block["block_id"]: block["kind"] for block in iter_blocks(document["items"])
        }
        workflow = next(
            group
            for group in iter_section_groups(iter_chunk_drafts(document))
            if group[0].section_id == "s0030"
        )

        cls.title = document["title"]
        cls.units = attach_images(workflow, kinds, cls.title)[:2]
        cls.merged = merge_drafts(cls.units, cls.title)
        cls.exact_budget = count_tokens(cls.merged.retrieval_text)

    def test_exact_fit_produces_one_chunk(self):
        chunks = pack_section(self.units, self.title, self.exact_budget)

        self.assertEqual(chunks, [self.merged])
        self.assertEqual(count_tokens(chunks[0].retrieval_text), self.exact_budget)

    def test_one_token_less_produces_two_intact_chunks(self):
        budget = self.exact_budget - 1
        self.assertTrue(
            all(count_tokens(unit.retrieval_text) <= budget for unit in self.units)
        )

        chunks = pack_section(self.units, self.title, budget)

        self.assertEqual(chunks, self.units)

    def test_oversized_unit_is_rejected(self):
        budget = count_tokens(self.merged.retrieval_text) - 1

        with self.assertRaisesRegex(ValueError, "needs .*budget"):
            pack_section([self.merged], self.title, budget)


if __name__ == "__main__":
    unittest.main()
