from __future__ import annotations

import inspect
import unittest

from telethon import TelegramClient

from src.telegram_service import GetForumTopicsRequest


class TelethonTopicCompatibilityTests(unittest.TestCase):
    def test_forum_topics_request_has_expected_arguments(self):
        params = inspect.signature(GetForumTopicsRequest.__init__).parameters
        for name in ("channel", "offset_date", "offset_id", "offset_topic", "limit"):
            self.assertIn(name, params)

    def test_send_file_supports_reply_to_for_topic_routing(self):
        params = inspect.signature(TelegramClient.send_file).parameters
        self.assertIn("reply_to", params)


if __name__ == "__main__":
    unittest.main()
