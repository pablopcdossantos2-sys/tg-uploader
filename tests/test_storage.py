from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.storage import QueueStore, sha256_file


class QueueStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / "test.db"
        self.store = QueueStore(self.db)

        self.file_a = self.root / "a.txt"
        self.file_b = self.root / "b.txt"
        self.file_a.write_text("same content", encoding="utf-8")
        self.file_b.write_text("other content", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_duplicate_is_scoped_to_group_and_content(self):
        job_id = self.store.create_job(
            [self.file_a],
            self.root,
            100,
            "Group A",
            True,
        )
        item = self.store.items_for_job(job_id)[0]
        checksum = sha256_file(self.file_a)

        self.store.mark_item_completed(
            item,
            100,
            "Group A",
            None,
            None,
            self.file_a.stat().st_size,
            checksum,
            123,
        )

        self.assertTrue(self.store.is_duplicate(100, checksum))
        self.assertFalse(self.store.is_duplicate(200, checksum))
        self.assertFalse(self.store.is_duplicate(100, sha256_file(self.file_b)))

    def test_duplicate_is_scoped_to_topic_inside_same_group(self):
        job_id = self.store.create_job(
            [self.file_a],
            self.root,
            100,
            "Forum Group",
            True,
            topic_id=10,
            topic_title="Topic A",
        )
        item = self.store.items_for_job(job_id)[0]
        checksum = sha256_file(self.file_a)

        self.store.mark_item_completed(
            item,
            100,
            "Forum Group",
            10,
            "Topic A",
            self.file_a.stat().st_size,
            checksum,
            555,
        )

        self.assertTrue(self.store.is_duplicate(100, checksum, topic_id=10))
        self.assertFalse(self.store.is_duplicate(100, checksum, topic_id=20))
        self.assertFalse(self.store.is_duplicate(100, checksum, topic_id=None))

        summary = self.store.get_job(job_id)
        self.assertEqual(summary.topic_id, 10)
        self.assertEqual(summary.topic_title, "Topic A")

        history = self.store.history()
        self.assertEqual(history[0].topic_title, "Topic A")

    def test_running_item_is_recovered_as_pending(self):
        job_id = self.store.create_job(
            [self.file_a, self.file_b],
            self.root,
            100,
            "Group A",
            True,
        )
        self.store.start_job(job_id)
        first = self.store.items_for_job(job_id)[0]
        self.store.mark_item_uploading(first.id)

        recovered = QueueStore(self.db)
        summary = recovered.get_job(job_id)
        items = recovered.items_for_job(job_id)

        self.assertIsNotNone(summary)
        self.assertEqual(summary.status, "interrupted")
        self.assertEqual(items[0].status, "pending")
        self.assertEqual(items[1].status, "pending")
        self.assertEqual(recovered.latest_resumable_job().id, job_id)

    def test_completed_items_remain_completed_after_recovery(self):
        job_id = self.store.create_job(
            [self.file_a, self.file_b],
            self.root,
            100,
            "Group A",
            True,
        )
        self.store.start_job(job_id)
        first, second = self.store.items_for_job(job_id)
        checksum = sha256_file(self.file_a)
        self.store.mark_item_completed(
            first,
            100,
            "Group A",
            None,
            None,
            self.file_a.stat().st_size,
            checksum,
            321,
        )
        self.store.mark_item_uploading(second.id)

        recovered = QueueStore(self.db)
        items = recovered.items_for_job(job_id)

        self.assertEqual(items[0].status, "completed")
        self.assertEqual(items[1].status, "pending")
        self.assertEqual(recovered.get_job(job_id).done_files, 1)

    def test_history_records_uploaded_items(self):
        job_id = self.store.create_job(
            [self.file_a],
            self.root,
            100,
            "Group A",
            False,
        )
        item = self.store.items_for_job(job_id)[0]
        checksum = sha256_file(self.file_a)

        self.store.mark_item_completed(
            item,
            100,
            "Group A",
            None,
            None,
            self.file_a.stat().st_size,
            checksum,
            999,
        )
        history = self.store.history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].status, "uploaded")
        self.assertEqual(history[0].group_title, "Group A")
        self.assertEqual(history[0].message_id, 999)
        self.assertEqual(history[0].sha256, checksum)


if __name__ == "__main__":
    unittest.main()
