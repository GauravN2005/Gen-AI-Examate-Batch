import unittest

from app.education_guard import is_recommendation_request, refusal_response


class EducationGuardTests(unittest.TestCase):
    def test_blocks_recommendations(self) -> None:
        for question in (
            "Which mutual fund should I buy?",
            "Recommend a stock",
            "Which scheme guarantees profit?",
            "What fund should I buy for guaranteed profit?",
        ):
            self.assertTrue(is_recommendation_request(question), question)

    def test_allows_education(self) -> None:
        for question in (
            "What is SIP?",
            "What is NAV?",
            "How does Riskometer work?",
            "How do I compare expense ratios?",
        ):
            self.assertFalse(is_recommendation_request(question), question)

    def test_refusal_is_fixed_and_has_verified_resources(self) -> None:
        response = refusal_response()
        self.assertEqual(response["heading"], "Education, not advice")
        self.assertEqual(len(response["resources"]), 2)
        self.assertTrue(
            all(item["url"].startswith("https://investor.sebi.gov.in/") for item in response["resources"])
        )


if __name__ == "__main__":
    unittest.main()
