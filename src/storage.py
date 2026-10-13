from __future__ import annotations

import hashlib
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .config import DATA_DIR

DB_PATH = DATA_DIR / "tg_uploader.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class QueueItem:
    id: int
    job_id: str
    position: int
    path: Path
    relative_path: str
    size: int
    status: str
    sha256: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class JobSummary:
    id: str
    group_id: int
    group_title: str
    source_folder: str
    status: str
    total_files: int
    done_files: int
    skipped_files: int
    failed_files: int
    total_bytes: int
    done_bytes: int
    created_at: str


@dataclass(frozen=True)
class HistoryEntry:
    occurred_at: str
    status: str
    group_title: str
    file_name: str
    path: str
    size: int
    sha256: str | None
    message_id: int | None


class QueueStore:
    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self._write_lock = threading.Lock()
        self._init_schema()
        self.recover_interrupted_jobs()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def _connection(self):
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS upload_jobs (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    group_id INTEGER NOT NULL,
                    group_title TEXT NOT NULL,
                    source_folder TEXT NOT NULL,
                    recursive INTEGER NOT NULL DEFAULT 1,
                    status TEXT NOT NULL,
                    total_files INTEGER NOT NULL,
                    total_bytes INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS upload_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL REFERENCES upload_jobs(id) ON DELETE CASCADE,
                    position INTEGER NOT NULL,
                    path TEXT NOT NULL,
                    relative_path TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    sha256 TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    error TEXT,
                    message_id INTEGER,
                    started_at TEXT,
                    completed_at TEXT,
                    UNIQUE(job_id, position)
                );

                CREATE TABLE IF NOT EXISTS upload_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    group_id INTEGER NOT NULL,
                    group_title TEXT NOT NULL,
                    job_id TEXT,
                    item_id INTEGER,
                    path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    sha256 TEXT,
                    message_id INTEGER,
                    note TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_items_job_status
                    ON upload_items(job_id, status);
                CREATE INDEX IF NOT EXISTS idx_history_duplicate
                    ON upload_history(group_id, sha256, status);
                CREATE INDEX IF NOT EXISTS idx_history_time
                    ON upload_history(occurred_at DESC);
                """
            )

    def recover_interrupted_jobs(self) -> None:
        now = utc_now()
        with self._write_lock, self._connect() as conn:
            conn.execute(
                "UPDATE upload_items SET status='pending', error=NULL "
                "WHERE status='uploading'"
            )
            conn.execute(
                "UPDATE upload_jobs SET status='interrupted', updated_at=? "
                "WHERE status='running'",
                (now,),
            )

    def create_job(
        self,
        files: Iterable[Path],
        source_folder: Path,
        group_id: int,
        group_title: str,
        recursive: bool,
    ) -> str:
        paths = [Path(p).resolve() for p in files]
        job_id = uuid.uuid4().hex
        now = utc_now()
        total_bytes = sum(p.stat().st_size for p in paths)
        with self._write_lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO upload_jobs
                    (id, created_at, updated_at, group_id, group_title, source_folder,
                     recursive, status, total_files, total_bytes)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
                """,
                (
                    job_id, now, now, int(group_id), group_title, str(source_folder.resolve()),
                    int(recursive), len(paths), total_bytes,
                ),
            )
            for position, path in enumerate(paths, start=1):
                try:
                    relative = str(path.relative_to(source_folder.resolve()))
                except ValueError:
                    relative = path.name
                conn.execute(
                    """
                    INSERT INTO upload_items
                        (job_id, position, path, relative_path, size, status)
                    VALUES (?, ?, ?, ?, ?, 'pending')
                    """,
                    (job_id, position, str(path), relative, path.stat().st_size),
                )
        return job_id

    def get_job(self, job_id: str) -> JobSummary | None:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT j.*,
                    SUM(CASE WHEN i.status='completed' THEN 1 ELSE 0 END) AS completed_files,
                    SUM(CASE WHEN i.status='skipped_duplicate' THEN 1 ELSE 0 END) AS skipped_files,
                    SUM(CASE WHEN i.status='failed' THEN 1 ELSE 0 END) AS failed_files,
                    SUM(CASE WHEN i.status IN ('completed','skipped_duplicate') THEN i.size ELSE 0 END) AS done_bytes
                FROM upload_jobs j
                LEFT JOIN upload_items i ON i.job_id=j.id
                WHERE j.id=?
                GROUP BY j.id
                """,
                (job_id,),
            ).fetchone()
        if not row:
            return None
        completed = int(row["completed_files"] or 0)
        skipped = int(row["skipped_files"] or 0)
        return JobSummary(
            id=row["id"],
            group_id=int(row["group_id"]),
            group_title=row["group_title"],
            source_folder=row["source_folder"],
            status=row["status"],
            total_files=int(row["total_files"]),
            done_files=completed + skipped,
            skipped_files=skipped,
            failed_files=int(row["failed_files"] or 0),
            total_bytes=int(row["total_bytes"]),
            done_bytes=int(row["done_bytes"] or 0),
            created_at=row["created_at"],
        )

    def latest_resumable_job(self) -> JobSummary | None:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT j.id
                FROM upload_jobs j
                WHERE j.status IN ('pending','interrupted','needs_attention')
                  AND EXISTS (
                    SELECT 1 FROM upload_items i
                    WHERE i.job_id=j.id AND i.status IN ('pending','failed')
                  )
                ORDER BY j.updated_at DESC
                LIMIT 1
                """
            ).fetchone()
        return self.get_job(row["id"]) if row else None

    def items_for_job(self, job_id: str) -> list[QueueItem]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT id, job_id, position, path, relative_path, size, status, sha256, error
                FROM upload_items
                WHERE job_id=?
                ORDER BY position
                """,
                (job_id,),
            ).fetchall()
        return [
            QueueItem(
                id=int(r["id"]),
                job_id=r["job_id"],
                position=int(r["position"]),
                path=Path(r["path"]),
                relative_path=r["relative_path"],
                size=int(r["size"]),
                status=r["status"],
                sha256=r["sha256"],
                error=r["error"],
            )
            for r in rows
        ]

    def start_job(self, job_id: str) -> None:
        now = utc_now()
        with self._write_lock, self._connect() as conn:
            conn.execute(
                "UPDATE upload_items SET status='pending', error=NULL "
                "WHERE job_id=? AND status='failed'",
                (job_id,),
            )
            conn.execute(
                "UPDATE upload_jobs SET status='running', updated_at=? WHERE id=?",
                (now, job_id),
            )

    def mark_item_uploading(self, item_id: int) -> None:
        with self._write_lock, self._connect() as conn:
            conn.execute(
                "UPDATE upload_items SET status='uploading', started_at=?, error=NULL WHERE id=?",
                (utc_now(), item_id),
            )

    def update_item_fingerprint(self, item_id: int, size: int, sha256: str) -> None:
        with self._write_lock, self._connect() as conn:
            conn.execute(
                "UPDATE upload_items SET size=?, sha256=? WHERE id=?",
                (int(size), sha256, item_id),
            )

    def is_duplicate(self, group_id: int, sha256: str) -> bool:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM upload_history
                WHERE group_id=? AND sha256=? AND status='uploaded'
                LIMIT 1
                """,
                (int(group_id), sha256),
            ).fetchone()
        return row is not None

    def _history_insert(
        self,
        conn: sqlite3.Connection,
        *,
        status: str,
        group_id: int,
        group_title: str,
        item: QueueItem,
        size: int,
        sha256: str | None,
        message_id: int | None = None,
        note: str | None = None,
    ) -> None:
        conn.execute(
            """
            INSERT INTO upload_history
                (occurred_at, status, group_id, group_title, job_id, item_id, path,
                 file_name, size, sha256, message_id, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(), status, int(group_id), group_title, item.job_id, item.id,
                str(item.path), item.path.name, int(size), sha256, message_id, note,
            ),
        )

    def mark_item_completed(
        self,
        item: QueueItem,
        group_id: int,
        group_title: str,
        size: int,
        sha256: str,
        message_id: int | None,
    ) -> None:
        now = utc_now()
        with self._write_lock, self._connect() as conn:
            conn.execute(
                """
                UPDATE upload_items
                SET status='completed', size=?, sha256=?, message_id=?, completed_at=?, error=NULL
                WHERE id=?
                """,
                (int(size), sha256, message_id, now, item.id),
            )
            self._history_insert(
                conn, status="uploaded", group_id=group_id, group_title=group_title,
                item=item, size=size, sha256=sha256, message_id=message_id,
            )

    def mark_item_skipped(
        self,
        item: QueueItem,
        group_id: int,
        group_title: str,
        size: int,
        sha256: str,
    ) -> None:
        now = utc_now()
        with self._write_lock, self._connect() as conn:
            conn.execute(
                """
                UPDATE upload_items
                SET status='skipped_duplicate', size=?, sha256=?, completed_at=?, error=NULL
                WHERE id=?
                """,
                (int(size), sha256, now, item.id),
            )
            self._history_insert(
                conn, status="skipped_duplicate", group_id=group_id, group_title=group_title,
                item=item, size=size, sha256=sha256, note="duplicate",
            )

    def mark_item_failed(
        self,
        item: QueueItem,
        group_id: int,
        group_title: str,
        error: str,
    ) -> None:
        with self._write_lock, self._connect() as conn:
            conn.execute(
                "UPDATE upload_items SET status='failed', error=? WHERE id=?",
                (error[:2000], item.id),
            )
            self._history_insert(
                conn, status="failed", group_id=group_id, group_title=group_title,
                item=item, size=item.size, sha256=item.sha256, note=error[:2000],
            )

    def mark_item_pending(self, item_id: int) -> None:
        with self._write_lock, self._connect() as conn:
            conn.execute(
                "UPDATE upload_items SET status='pending' WHERE id=?",
                (item_id,),
            )

    def finish_job(self, job_id: str) -> JobSummary | None:
        summary = self.get_job(job_id)
        if not summary:
            return None
        status = "needs_attention" if summary.failed_files else "completed"
        with self._write_lock, self._connect() as conn:
            conn.execute(
                "UPDATE upload_jobs SET status=?, updated_at=? WHERE id=?",
                (status, utc_now(), job_id),
            )
        return self.get_job(job_id)

    def interrupt_job(self, job_id: str) -> None:
        with self._write_lock, self._connect() as conn:
            conn.execute(
                "UPDATE upload_items SET status='pending' WHERE job_id=? AND status='uploading'",
                (job_id,),
            )
            conn.execute(
                "UPDATE upload_jobs SET status='interrupted', updated_at=? WHERE id=?",
                (utc_now(), job_id),
            )

    def history(self, limit: int = 300) -> list[HistoryEntry]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT occurred_at, status, group_title, file_name, path, size, sha256, message_id
                FROM upload_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (int(limit),),
            ).fetchall()
        return [
            HistoryEntry(
                occurred_at=r["occurred_at"],
                status=r["status"],
                group_title=r["group_title"],
                file_name=r["file_name"],
                path=r["path"],
                size=int(r["size"]),
                sha256=r["sha256"],
                message_id=r["message_id"],
            )
            for r in rows
        ]


def sha256_file(path: Path, cancel_event: threading.Event | None = None) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            if cancel_event is not None and cancel_event.is_set():
                raise InterruptedError("cancelled")
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()
