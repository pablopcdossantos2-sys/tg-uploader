from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from .config import SESSION_PATH


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


PromptCallback = Callable[[str, str, bool], str | None]
StatusCallback = Callable[[str], None]
ProgressCallback = Callable[[UploadProgress], None]


class TelegramService:
    def __init__(self, api_id: int, api_hash: str, phone: str, prompt: PromptCallback):
        self.api_id = api_id
        self.api_hash = api_hash.strip()
        self.phone = phone.strip()
        self.prompt = prompt

    def _client(self) -> TelegramClient:
        return TelegramClient(str(SESSION_PATH), self.api_id, self.api_hash)

    async def _ensure_authorized(self, client: TelegramClient) -> None:
        await client.connect()
        if await client.is_user_authorized():
            return

        if not self.phone:
            raise ValueError("Informe o telefone da conta Telegram no formato internacional.")

        await client.send_code_request(self.phone)
        code = self.prompt(
            "Código de verificação",
            "Digite o código enviado pelo Telegram para esta conta:",
            False,
        )
        if not code:
            raise UploadCancelled("Autenticação cancelada.")

        try:
            await client.sign_in(self.phone, code.strip())
        except SessionPasswordNeededError:
            password = self.prompt(
                "Senha em duas etapas",
                "Esta conta usa verificação em duas etapas. Digite a senha:",
                True,
            )
            if password is None:
                raise UploadCancelled("Autenticação cancelada.")
            await client.sign_in(password=password)

    async def list_groups_async(self) -> list[GroupInfo]:
        client = self._client()
        try:
            await self._ensure_authorized(client)
            groups: list[GroupInfo] = []
            async for dialog in client.iter_dialogs():
                if dialog.is_group:
                    groups.append(GroupInfo(id=int(dialog.id), title=dialog.name or str(dialog.id)))
            groups.sort(key=lambda item: item.title.casefold())
            return groups
        finally:
            await client.disconnect()

    def list_groups(self) -> list[GroupInfo]:
        return asyncio.run(self.list_groups_async())

    async def upload_async(
        self,
        files: Iterable[Path],
        group_id: int,
        cancel_event: threading.Event,
        on_progress: ProgressCallback,
        on_status: StatusCallback,
    ) -> None:
        paths = [Path(p) for p in files]
        if not paths:
            raise ValueError("Nenhum arquivo encontrado para enviar.")

        total_bytes = sum(p.stat().st_size for p in paths)
        completed_bytes = 0
        started_at = time.monotonic()
        client = self._client()

        try:
            await self._ensure_authorized(client)
            entity = await client.get_entity(group_id)

            for index, path in enumerate(paths, start=1):
                if cancel_event.is_set():
                    raise UploadCancelled("Upload cancelado pelo usuário.")

                file_total = path.stat().st_size
                last_emit = 0.0
                on_status(f"Enviando {path.name}")

                def progress_callback(sent: int, total: int) -> None:
                    nonlocal last_emit
                    if cancel_event.is_set():
                        raise UploadCancelled("Upload cancelado pelo usuário.")

                    now = time.monotonic()
                    if sent != total and now - last_emit < 0.10:
                        return
                    last_emit = now
                    elapsed = max(now - started_at, 0.001)
                    current_total_sent = completed_bytes + int(sent)
                    on_progress(
                        UploadProgress(
                            file_index=index,
                            file_count=len(paths),
                            file_name=path.name,
                            file_sent=int(sent),
                            file_total=int(total),
                            total_sent=current_total_sent,
                            total_bytes=total_bytes,
                            bytes_per_second=current_total_sent / elapsed,
                        )
                    )

                await client.send_file(
                    entity,
                    str(path),
                    force_document=True,
                    progress_callback=progress_callback,
                )
                completed_bytes += file_total

                elapsed = max(time.monotonic() - started_at, 0.001)
                on_progress(
                    UploadProgress(
                        file_index=index,
                        file_count=len(paths),
                        file_name=path.name,
                        file_sent=file_total,
                        file_total=file_total,
                        total_sent=completed_bytes,
                        total_bytes=total_bytes,
                        bytes_per_second=completed_bytes / elapsed,
                    )
                )
        finally:
            await client.disconnect()

    def upload(
        self,
        files: Iterable[Path],
        group_id: int,
        cancel_event: threading.Event,
        on_progress: ProgressCallback,
        on_status: StatusCallback,
    ) -> None:
        asyncio.run(
            self.upload_async(
                files=files,
                group_id=group_id,
                cancel_event=cancel_event,
                on_progress=on_progress,
                on_status=on_status,
            )
        )
