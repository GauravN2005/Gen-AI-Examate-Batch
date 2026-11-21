import unittest

from app.llm import _usage_value


class LLMUsageTests(unittest.TestCase):
    def test_dictionary_usage_is_extracted(self) -> None:
        usage = {
            "prompt_tokens": 12,
            "completion_tokens": 7,
            "total_tokens": 19,
        }
        self.assertEqual(
            _usage_value(usage, "prompt_tokens", "prompt_tokens"),
            12,
        )

    def test_object_usage_is_extracted(self) -> None:
        class Usage:
            prompt_token_count = 10
            candidates_token_count = 4
            total_token_count = 14

        usage = Usage()
        self.assertEqual(
            _usage_value(usage, "prompt_token_count", "prompt_token_count"),
            10,
        )

    def test_missing_usage_is_none(self) -> None:
        self.assertIsNone(
            _usage_value(None, "prompt_tokens", "prompt_tokens")
        )


if __name__ == "__main__":
    unittest.main()
