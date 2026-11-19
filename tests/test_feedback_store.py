import json
import tempfile
import unittest
from pathlib import Path

from app.feedback_store import save_feedback


class FeedbackStoreTests(unittest.TestCase):
    def test_feedback_is_updated_not_duplicated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "feedback.jsonl"
            save_feedback(
                message_id="message-1",
                feedback="up",
                question="What is NAV?",
                response="NAV is net asset value.",
                file_path=file_path,
            )
            save_feedback(
                message_id="message-1",
                feedback="down",
                question="What is NAV?",
                response="NAV is net asset value.",
                comment="Need more detail",
                file_path=file_path,
            )
            entries = [
                json.loads(line)
                for line in file_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["feedback"], "down")
            self.assertEqual(entries[0]["comment"], "Need more detail")
            self.assertIn("timestamp", entries[0])

    def test_invalid_feedback_is_rejected(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaises(ValueError),
        ):
            save_feedback(
                message_id="message-2",
                feedback="invalid",
                question="What is SIP?",
                response="A SIP invests regularly.",
                file_path=Path(directory) / "feedback.jsonl",
            )


if __name__ == "__main__":
    unittest.main()
