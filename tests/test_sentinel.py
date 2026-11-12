"""
Tests for SovereignSentinel: Knowledge graph operations, evidence weighting, and receipts.
"""

import os
import tempfile
import unittest
from sentinel.graph import ProvenanceGraph
from sentinel.receipt import generate_provenance_receipt


class TestSovereignSentinel(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_sentinel.db")
        self.graph = ProvenanceGraph(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_claim_verification_lifecycle(self):
        # 1. Add Sources
        self.graph.add_source("reuters-01", "a" * 64, url="https://reuters.com/1", credibility=0.9)
        self.graph.add_source("blog-random", "b" * 64, url="https://unknown-blog.xyz", credibility=0.2)

        # 2. Add Claim
        self.graph.add_claim("c1", "Company X", "acquired", "Startup Y")

        # 3. Link Evidence
        self.graph.link_evidence("c1", "reuters-01", supports=True, quote_snippet="Company X confirmed acquisition")
        self.graph.link_evidence("c1", "blog-random", supports=False, quote_snippet="No deal happened")

        # 4. Evaluate
        eval_res = self.graph.evaluate_claim("c1")
        self.assertEqual(eval_res["verdict"], "VERIFIED")
        self.assertGreater(eval_res["supporting_weight"], eval_res["refuting_weight"])

        # 5. Attestation Receipt
        rc = generate_provenance_receipt(eval_res)
        self.assertIn("receipt_hash", rc)
        self.assertEqual(rc["verdict"], "VERIFIED")


if __name__ == "__main__":
    unittest.main()
