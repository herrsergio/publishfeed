"""Unit tests for text formatting helpers."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from text_utils import strip_wrapping_quotes


class TestStripWrappingQuotes(unittest.TestCase):
    def test_strip_wrapping_double_quotes(self):
        self.assertEqual(
            strip_wrapping_quotes('"SageMaker simplifies deployment."'),
            "SageMaker simplifies deployment.",
        )

    def test_strip_wrapping_curly_quotes_and_whitespace(self):
        self.assertEqual(
            strip_wrapping_quotes('  “A useful post.”  '), "A useful post."
        )

    def test_preserve_unpaired_or_internal_quotes(self):
        self.assertEqual(strip_wrapping_quotes('A "quoted" phrase'), 'A "quoted" phrase')
        self.assertEqual(strip_wrapping_quotes('"An unfinished quote'), '"An unfinished quote')

    def test_strip_quotes_with_trailing_emojis(self):
        self.assertEqual(
            strip_wrapping_quotes(
                '"MCP protocol undergoes major revision. #MCP #AWS" 🔁 🌍'
            ),
            "MCP protocol undergoes major revision. #MCP #AWS 🔁 🌍",
        )

    def test_strip_quotes_with_trailing_whitespace_after_close(self):
        self.assertEqual(
            strip_wrapping_quotes('"A useful post."   '), "A useful post."
        )
