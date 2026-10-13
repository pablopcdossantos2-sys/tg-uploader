from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from .config import SESSION_PATH
from .i18n import tr
from .storage import QueueItem, QueueStore, sha256_file


class UploadCancelled(Exception):
    """Raised when the user asks to cancel the active upload."""


@dataclass(frozen=True)
class GroupInfo:
    id: int
    title: str


@dataclass(frozen=True)
class UploadProgress:
    file_index: int
    file_count: int
    file_name: str
    file_sent: int
    file_total: int
    total_sent: int
    total_bytes: int
    bytes_per_second: float

    @property
    def file_percent(self) -> float:
        if not self.file_total:
            return 0.0
        return min(100.0, self.file_sent / self.file_total * 100.0)

    @property
    def total_percent(self) -> float:
        if not self.total_bytes:
            return 0.0
        return min(100.0, self.total_sent / self.total_bytes * 100.0)


@dataclass(frozen=True)
class UploadSummary:
    uploaded: int
    skipped: int
    failed: int
    total: int


PromptCallback = Callable[[str, str, bool], str | None]
StatusCallback = Callable[[str], None]
ProgressCallback = Callable[[UploadProgress], None]


class TelegramService:
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        phone: str,
        prompt: PromptCallback,
        language: str = "pt-BR",
    ):
        self.api_id = api_id
        self.api_hash = api_hash.strip()
        self.phone = phone.strip()
        self.prompt = prompt
        self.language = language

    def _t(self, key: str, **kwargs) -> str:
        return tr(self.language, key, **kwargs)

    def _client(self) -> TelegramClient:
        return TelegramClient(str(SESSION_PATH), self.api_id, self.api_hash)

    async def _ensure_authorized(self, client: TelegramClient) -> None:
        await client.connect()
        if await client.is_user_authorized():
            return

        if not self.phone:
            raise ValueError(self._t("phone_required"))

        await client.send_code_request(self.phone)
        code = self.prompt(
            self._t("verification_title"),
            self._t("verification_text"),
            False,
        )
        if not code:
            raise UploadCancelled(self._t("auth_cancelled"))

        try:
            await client.sign_in(self.phone, code.strip())
        except SessionPasswordNeededError:
            password = self.prompt(
                self._t("password_title"),
                self._t("password_text"),
                True,
            )
            if password is None:
                raise UploadCancelled(self._t("auth_cancelled"))
            await client.sign_in(password=password)

    async def list_groups_async(self) -> list[GroupInfo]:
        client = self._client()
        try:
            await self._ensure_authorized(client)
            groups: list[GroupInfo] = []
            async for dialog in client.iter_dialogs():
                if dialog.is_group:
                    groups.append(
                        GroupInfo(
                            id=int(dialog.id),
                            title=dialog.name or str(dialog.id),
                        )
                    )
            groups.sort(key=lambda item: item.title.casefold())
            return groups
        finally:
            await client.disconnect()

    def list_groups(self) -> list[GroupInfo]:
        return asyncio.run(self.list_groups_async())

    async def upload_job_async(
        self,
        *,
        store: QueueStore,
        job_id: str,
        cancel_event: threading.Event,
        skip_duplicates: bool,
        on_progress: ProgressCallback,
        on_status: StatusCallback,
    ) -> UploadSummary:
        job = store.get_job(job_id)
        if not job:
            raise ValueError(f"Upload job not found: {job_id}")

        store.start_job(job_id)
        items = store.items_for_job(job_id)
        job = store.get_job(job_id)
        if not job:
            raise ValueError(f"Upload job not found: {job_id}")

        total_bytes = 0
        completed_bytes = 0
        uploaded_this_run = 0
        for item in items:
            if item.status in {"completed", "skipped_duplicate"}:
                size = item.size
                completed_bytes += size
            else:
                try:
                    size = item.path.stat().st_size
                except OSError:
                    size = item.size
            total_bytes += size

        started_at = time.monotonic()
        client = self._client()

        try:
            await self._ensure_authorized(client)
            entity = await client.get_entity(job.group_id)

            for item in items:
                if item.status in {"completed", "skipped_duplicate"}:
                    continue

                if cancel_event.is_set():
                    raise UploadCancelled(self._t("upload_cancelled"))

                if not item.path.is_file():
                    store.mark_item_failed(
                        item,
                        job.group_id,
                        job.group_title,
                        self._t("file_missing", path=str(item.path)),
                    )
                    continue

                file_total = item.path.stat().st_size
                store.mark_item_uploading(item.id)
                on_status(self._t("status_hashing", name=item.path.name))

                try:
                    checksum = sha256_file(item.path, cancel_event)
                except InterruptedError as exc:
                    store.mark_item_pending(item.id)
                    raise UploadCancelled(self._t("upload_cancelled")) from exc

                store.update_item_fingerprint(item.id, file_total, checksum)

                if cancel_event.is_set():
                    store.mark_item_pending(item.id)
                    raise UploadCancelled(self._t("upload_cancelled"))

                if skip_duplicates and store.is_duplicate(job.group_id, checksum):
                    store.mark_item_skipped(
                        item,
                        job.group_id,
                        job.group_title,
                        file_total,
                        checksum,
                    )
                    completed_bytes += file_total
                    uploaded_this_run += file_total
                    elapsed = max(time.monotonic() - started_at, 0.001)
                    on_status(self._t("status_duplicate", name=item.path.name))
                    on_progress(
                        UploadProgress(
                            file_index=item.position,
                            file_count=len(items),
                            file_name=item.path.name,
                            file_sent=file_total,
                            file_total=file_total,
                            total_sent=completed_bytes,
                            total_bytes=total_bytes,
                            bytes_per_second=uploaded_this_run / elapsed,
                        )
                    )
                    continue

                last_emit = 0.0
                on_status(self._t("status_sending", name=item.path.name))

                def progress_callback(sent: int, total: int) -> None:
                    nonlocal last_emit
                    if cancel_event.is_set():
                        raise UploadCancelled(self._t("upload_cancelled"))

                    now = time.monotonic()
                    if sent != total and now - last_emit < 0.10:
                        return
                    last_emit = now
                    elapsed = max(now - started_at, 0.001)
                    current_total_sent = completed_bytes + int(sent)
                    on_progress(
                        UploadProgress(
                            file_index=item.position,
                            file_count=len(items),
                            file_name=item.path.name,
                            file_sent=int(sent),
                            file_total=int(total),
                            total_sent=current_total_sent,
                            total_bytes=total_bytes,
                            bytes_per_second=(uploaded_this_run + int(sent)) / elapsed,
                        )
                    )

                try:
                    message = await client.send_file(
                        entity,
                        str(item.path),
                        force_document=True,
                        progress_callback=progress_callback,
                    )
                    message_id = getattr(message, "id", None)
                    store.mark_item_completed(
                        item,
                        job.group_id,
                        job.group_title,
                        file_total,
                        checksum,
                        int(message_id) if message_id is not None else None,
                    )
                    completed_bytes += file_total
                    elapsed = max(time.monotonic() - started_at, 0.001)
                    on_progress(
                        UploadProgress(
                            file_index=item.position,
                            file_count=len(items),
                            file_name=item.path.name,
                            file_sent=file_total,
                            file_total=file_total,
                            total_sent=completed_bytes,
                            total_bytes=total_bytes,
                            bytes_per_second=uploaded_this_run / elapsed,
                        )
                    )
                except UploadCancelled:
                    store.mark_item_pending(item.id)
                    raise
                except Exception as exc:
                    store.mark_item_failed(
                        item,
                        job.group_id,
                        job.group_title,
                        str(exc),
                    )

            final = store.finish_job(job_id)
            if not final:
                return UploadSummary(0, 0, 0, len(items))
            return UploadSummary(
                uploaded=max(0, final.done_files - final.skipped_files),
                skipped=final.skipped_files,
                failed=final.failed_files,
                total=final.total_files,
            )
        except UploadCancelled:
            store.interrupt_job(job_id)
            raise
        except Exception:
            store.interrupt_job(job_id)
            raise
        finally:
            await client.disconnect()

    def upload_job(
        self,
        *,
        store: QueueStore,
        job_id: str,
        cancel_event: threading.Event,
        skip_duplicates: bool,
        on_progress: ProgressCallback,
        on_status: StatusCallback,
    ) -> UploadSummary:
        return asyncio.run(
            self.upload_job_async(
                store=store,
                job_id=job_id,
                cancel_event=cancel_event,
                skip_duplicates=skip_duplicates,
                on_progress=on_progress,
                on_status=on_status,
            )
        )
