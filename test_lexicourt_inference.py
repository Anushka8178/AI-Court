import unittest
import os
import json
from lexicourt_inference import load_model, predict_outcome, strip_leakage, DECISION_LEAK_PATTERNS

class TestLexiCourtInference(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Pre-load model before running tests."""
        print("setUpClass: Loading model once for test suite...")
        cls.model, cls.tokenizer, cls.id2label = load_model()

    def test_model_loading(self):
        """Test that model, tokenizer, and label mapping are loaded properly."""
        self.assertIsNotNone(self.model)
        self.assertIsNotNone(self.tokenizer)
        self.assertIsInstance(self.id2label, dict)
        self.assertIn(0, self.id2label)
        self.assertIn(1, self.id2label)
        self.assertIn(2, self.id2label)

    def test_decision_leak_patterns_regex(self):
        """Test that DECISION_LEAK_PATTERNS exists and is a valid list of regexes."""
        self.assertIsInstance(DECISION_LEAK_PATTERNS, list)
        self.assertGreater(len(DECISION_LEAK_PATTERNS), 0)

        # Test disposition leakage phrase stripping
        text_with_leakage = "The High Court analyzed the records. The appeal is hereby allowed with no order as to costs."
        stripped = strip_leakage(text_with_leakage)
        self.assertNotIn("hereby allowed", stripped)

        # Test that non-disposition factual uses of 'accepted' or 'rejected' are preserved
        text_factual = "The accused accepted the settlement offer in writing."
        stripped_factual = strip_leakage(text_factual)
        self.assertIn("accepted", stripped_factual)

    def test_predict_outcome_structure(self):
        """
        Task 9 requirement:
        Assert response has predicted_label, confidence (0-1 float), and a probabilities dict with 3 keys.
        """
        sample_text = (
            "The petitioner filed a writ petition under Article 226 of the Constitution of India "
            "seeking quashing of the impugned administrative order. The respondent state submitted counter affidavit."
        )
        response = predict_outcome(sample_text, apply_leakage_strip=True)

        # 1. Check predicted_label presence and value
        self.assertIn("predicted_label", response)
        self.assertIn(response["predicted_label"], ["Accepted", "Other", "Rejected"])

        # 2. Check confidence score float range [0.0, 1.0]
        self.assertIn("confidence", response)
        self.assertIsInstance(response["confidence"], float)
        self.assertGreaterEqual(response["confidence"], 0.0)
        self.assertLessEqual(response["confidence"], 1.0)

        # 3. Check probabilities dict with 3 keys
        self.assertIn("probabilities", response)
        probs = response["probabilities"]
        self.assertIsInstance(probs, dict)
        self.assertEqual(len(probs), 3)
        self.assertIn("Accepted", probs)
        self.assertIn("Other", probs)
        self.assertIn("Rejected", probs)

        # Sum of probabilities should be approximately 1.0
        prob_sum = sum(probs.values())
        self.assertAlmostEqual(prob_sum, 1.0, places=2)

        # Disclaimer presence check
        self.assertIn("disclaimer", response)

    def test_empty_input_handling(self):
        """Check error handling for empty or whitespace text."""
        res_empty = predict_outcome("")
        self.assertIn("error", res_empty)
        self.assertEqual(res_empty["predicted_label"], "Unknown")
        self.assertEqual(res_empty["confidence"], 0.0)

        res_none = predict_outcome(None)
        self.assertIn("error", res_none)

if __name__ == "__main__":
    unittest.main()
