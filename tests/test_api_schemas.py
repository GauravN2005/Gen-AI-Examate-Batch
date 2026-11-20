import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class ApiSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_schema(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "healthy")
        self.assertIn("provider", payload)
        self.assertIn("chroma", payload)

    @patch("app.main.answer_with_rag")
    def test_ask_rag_schema_is_validated(self, answer_with_rag) -> None:
        answer_with_rag.return_value = {
            "answer": "NAV is the per-unit value of a mutual fund.",
            "citations": [
                {
                    "chunk_id": "test-chunk",
                    "title": "Net Asset Value",
                    "source_url": "https://investor.sebi.gov.in/",
                    "page": None,
                }
            ],
            "confidence": "high",
        }
        response = self.client.post(
            "/ask", json={"question": "What is NAV?", "top_k": 3}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["question"], "What is NAV?")
        self.assertEqual(payload["confidence"], "high")
        self.assertEqual(len(payload["citations"]), 1)

    @patch("app.main.answer_with_rag")
    def test_ask_recommendation_is_refused_before_rag(self, answer_with_rag) -> None:
        response = self.client.post(
            "/ask", json={"question": "Which mutual fund should I buy?"}
        )
        self.assertEqual(response.status_code, 400)
        answer_with_rag.assert_not_called()


if __name__ == "__main__":
    unittest.main()
