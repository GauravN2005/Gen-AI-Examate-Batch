import unittest
from unittest.mock import patch

from app.agent_loop import run_agent


class AgentLoopTests(unittest.TestCase):
    @patch("app.agent_loop.answer_with_rag")
    def test_educational_question_uses_rag(self, rag) -> None:
        rag.return_value = {
            "answer": "A SIP invests a fixed amount regularly.",
            "citations": [{"source_url": "https://example.test"}],
            "confidence": "high",
        }
        result = run_agent("What is a SIP?")
        self.assertEqual(result["intent"], "retrieval")
        rag.assert_called_once()

    def test_calculation_requires_complete_inputs(self) -> None:
        result = run_agent("Calculate my SIP")
        self.assertEqual(result["status"], "needs_clarification")

    def test_calculation_uses_deterministic_tool(self) -> None:
        result = run_agent(
            "Calculate a monthly SIP of 1000 with NAVs 10, 8, 12, 10"
        )
        self.assertEqual(result["intent"], "calculation")
        self.assertEqual(result["calculation"]["total_invested"], 4000)


if __name__ == "__main__":
    unittest.main()
