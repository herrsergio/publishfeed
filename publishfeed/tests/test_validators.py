"""Unit tests for the validators module."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators import no_first_person_pronouns, get_all_first_person_matches


class TestNoFirstPersonPronouns(unittest.TestCase):
    """Tests for the no_first_person_pronouns validator."""

    def test_clean_text_passes(self):
        """Text without first-person pronouns should pass."""
        clean_texts = [
            "New AI model achieves 95% accuracy on benchmark tests. #AI #MachineLearning",
            "The team released a groundbreaking feature today. #Tech",
            "Researchers discovered a novel approach to quantum computing. #Quantum",
            "This framework simplifies cloud deployments significantly. #DevOps",
            "Version 2.0 brings major performance improvements. #Release",
        ]
        for text in clean_texts:
            passed, reason = no_first_person_pronouns(text)
            self.assertTrue(passed, f"Should pass: '{text}' but got: {reason}")

    def test_simple_pronouns_fail(self):
        """Simple first-person pronouns should fail."""
        failing_texts = [
            ("I built this new feature.", "I"),
            ("We are excited to announce.", "We"),
            ("Check out my latest project.", "my"),
            ("Our team worked hard on this.", "Our"),
            ("This belongs to us now.", "us"),
            ("The credit goes to me.", "me"),
        ]
        for text, expected_match in failing_texts:
            passed, reason = no_first_person_pronouns(text)
            self.assertFalse(passed, f"Should fail: '{text}'")
            self.assertIn(expected_match.lower(), reason.lower())

    def test_phrase_patterns_fail(self):
        """Common first-person phrases should fail."""
        failing_phrases = [
            "Join us in the next chapter of innovation.",
            "We created a new way to process data.",
            "We're launching something amazing.",
            "We've been working on this for months.",
            "Let's explore this together.",
            "Our team is proud to present.",
            "We believe in open source.",
            "We built this from scratch.",
        ]
        for text in failing_phrases:
            passed, reason = no_first_person_pronouns(text)
            self.assertFalse(passed, f"Should fail: '{text}'")

    def test_case_insensitivity(self):
        """Validation should be case-insensitive."""
        texts = [
            "WE CREATED SOMETHING NEW",
            "Join US for the event",
            "MY project is ready",
        ]
        for text in texts:
            passed, reason = no_first_person_pronouns(text)
            self.assertFalse(passed, f"Should fail (case-insensitive): '{text}'")

    def test_word_boundaries(self):
        """Should not false-positive on words containing pronoun substrings."""
        safe_texts = [
            "Discuss the results.",
            "The museum opens today.",
            "Previous versions worked well.",
            "Minus one equals zero.",
            "The campus is beautiful.",
            "Use this tool effectively.",
        ]
        for text in safe_texts:
            passed, reason = no_first_person_pronouns(text)
            self.assertTrue(passed, f"Should pass (word boundary): '{text}' but got: {reason}")


class TestGetAllFirstPersonMatches(unittest.TestCase):
    """Tests for the get_all_first_person_matches helper."""

    def test_finds_all_matches(self):
        """Should find all matching patterns in text."""
        text = "We created this, and I think our team did well."
        matches = get_all_first_person_matches(text)
        self.assertGreaterEqual(len(matches), 3)

    def test_empty_on_clean_text(self):
        """Should return empty list for clean text."""
        text = "The team released a new version today."
        matches = get_all_first_person_matches(text)
        self.assertEqual(matches, [])


if __name__ == '__main__':
    unittest.main()
