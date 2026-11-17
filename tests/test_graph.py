import unittest
from uuid import uuid4

from langgraph.types import Command

from app.graph import agent_graph


class GraphTests(unittest.TestCase):
    def _config(self) -> dict[str, dict[str, str]]:
        return {"configurable": {"thread_id": f"test-{uuid4()}"}}

    def test_calculation_waits_for_approval(self) -> None:
        config = self._config()
        pending = agent_graph.invoke(
            {"message": "Calculate SIP 1000 with NAVs 10, 8, 12, 10"},
            config,
        )
        self.assertTrue(pending["__interrupt__"])
        self.assertNotIn("response", pending)

        completed = agent_graph.invoke(Command(resume=True), config)
        self.assertEqual(completed["response"]["status"], "completed")

    def test_rejection_does_not_execute(self) -> None:
        config = self._config()
        agent_graph.invoke(
            {"message": "Calculate SIP 1000 with NAVs 10, 8, 12, 10"},
            config,
        )
        rejected = agent_graph.invoke(Command(resume=False), config)
        self.assertEqual(rejected["response"]["status"], "cancelled")

    def test_threads_are_isolated(self) -> None:
        first = self._config()
        second = self._config()
        agent_graph.invoke({"message": "Calculate SIP 1000 with NAVs 10, 8"}, first)
        state = agent_graph.get_state(second)
        self.assertFalse(state.values)
        self.assertFalse(state.next)


if __name__ == "__main__":
    unittest.main()
