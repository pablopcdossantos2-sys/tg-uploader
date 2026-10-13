from __future__ import annotations

import queue
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .config import AppConfig, load_api_hash, load_config, save_api_hash, save_config
from .i18n import SUPPORTED_LANGUAGES, tr
from .storage import HistoryEntry, QueueStore
from .telegram_service import (
    GroupInfo,
    TopicInfo,
    TelegramService,
    UploadCancelled,
    UploadProgress,
    UploadSummary,
)

APP_TITLE = "TG Uploader"

THEME_LABELS = {
    "pt-BR": {"System": "Sistema", "Dark": "Escuro", "Light": "Claro"},
    "en": {"System": "System", "Dark": "Dark", "Light": "Light"},
    "es": {"System": "Sistema", "Dark": "Oscuro", "Light": "Claro"},
}


class PromptRequest:
    def __init__(self, title: str, text: str, secret: bool):
        self.title, self.text, self.secret = title, text, secret
        self.response: str | None = None
        self.done = threading.Event()


class InputDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, text: str, secret: bool, language: str):
        super().__init__(master)
        self.result: str | None = None
        self.language = language
        self.title(title)
        self.geometry("440x210")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text=text, wraplength=390, justify="left").grid(
            row=0, column=0, padx=24, pady=(24, 12), sticky="ew"
        )
        placeholder = tr(
            language,
            "password_placeholder" if secret else "verification_placeholder",
        )
        self.entry = ctk.CTkEntry(
            self,
            show="•" if secret else "",
            placeholder_text=placeholder,
            height=38,
        )
        self.entry.grid(row=1, column=0, padx=24, sticky="ew")
        self.entry.focus_set()

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=2, column=0, padx=24, pady=24, sticky="e")
        ctk.CTkButton(
            row,
            text=tr(language, "cancel"),
            width=100,
            fg_color="transparent",
            border_width=1,
            command=self.cancel,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            row,
            text=tr(language, "confirm"),
            width=110,
            command=self.ok,
        ).pack(side="left")

        self.bind("<Return>", lambda _e: self.ok())
        self.bind("<Escape>", lambda _e: self.cancel())
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def ok(self):
        self.result = self.entry.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, master, language: str, entries: list[HistoryEntry]):
        super().__init__(master)
        self.language = language
        self.title(tr(language, "history_title"))
        self.geometry("980x560")
        self.minsize(760, 420)
        self.transient(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text=tr(language, "history_title"),
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, padx=22, pady=(20, 10), sticky="w")

        box = ctk.CTkTextbox(self, wrap="none", font=("Consolas", 12))
        box.grid(row=1, column=0, padx=22, pady=(0, 14), sticky="nsew")

        if not entries:
            box.insert("end", tr(language, "history_empty"))
        else:
            box.insert("end", tr(language, "history_header") + "\n")
            box.insert("end", "-" * 120 + "\n")
            for entry in entries:
                box.insert("end", self._line(entry) + "\n")
        box.configure(state="disabled")

        ctk.CTkButton(
            self,
            text=tr(language, "close"),
            width=110,
            command=self.destroy,
        ).grid(row=2, column=0, padx=22, pady=(0, 20), sticky="e")

    def _line(self, entry: HistoryEntry) -> str:
        try:
            date = datetime.fromisoformat(entry.occurred_at).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            date = entry.occurred_at

        status_key = {
            "uploaded": "uploaded_status",
            "skipped_duplicate": "duplicate_status",
            "failed": "failed_status",
        }.get(entry.status, entry.status)

        destination = entry.group_title
        if entry.topic_title:
            destination = f"{destination} › {entry.topic_title}"

        return (
            f"{date} | "
            f"{tr(self.language, status_key):10.10} | "
            f"{destination[:38]:38} | "
            f"{entry.file_name[:42]:42} | "
            f"{fmt_bytes(entry.size):>10}"
        )


class App(ctk.CTk):
    def __init__(self):
        self.cfg = load_config()
        self.language = self.cfg.language
        ctk.set_appearance_mode(self.cfg.theme or "System")
        ctk.set_default_color_theme("blue")
        super().__init__()

        self.store = QueueStore()
        self.events: queue.Queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.groups: dict[str, GroupInfo] = {}
        self.topics: dict[str, TopicInfo] = {}
        self.files: list[Path] = []
        self.active_job_id: str | None = None

        self.title(APP_TITLE)
        self.geometry("1220x800")
        self.minsize(1060, 700)
        self.after(0, self._maximize_window)

        self._build()
        self._restore()
        self._refresh_resume(show_status=True)
        self.after(60, self._pump)

    def _maximize_window(self):
        try:
            self.state("zoomed")
        except Exception:
            try:
                self.attributes("-zoomed", True)
            except Exception:
                pass

    def _t(self, key: str, **kwargs) -> str:
        return tr(self.language, key, **kwargs)

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="TG Uploader",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, padx=26, pady=(14, 0), sticky="w")
        ctk.CTkLabel(
            header,
            text=self._t("app_subtitle"),
            text_color=("gray35", "gray70"),
        ).grid(row=1, column=0, padx=26, pady=(0, 12), sticky="w")

        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.grid(row=0, column=1, rowspan=2, padx=22, pady=10, sticky="e")

        ctk.CTkLabel(controls, text=self._t("language")).grid(row=0, column=0, padx=(0, 6))
        lang_values = list(SUPPORTED_LANGUAGES.values())
        self.language_menu = ctk.CTkOptionMenu(
            controls,
            values=lang_values,
            width=150,
            command=self._language_changed,
        )
        self.language_menu.grid(row=0, column=1, padx=(0, 14))
        self.language_menu.set(SUPPORTED_LANGUAGES[self.language])

        ctk.CTkLabel(controls, text=self._t("theme")).grid(row=0, column=2, padx=(0, 6))
        theme_values = list(THEME_LABELS[self.language].values())
        self.theme = ctk.CTkOptionMenu(
            controls,
            values=theme_values,
            width=100,
            command=self._theme_changed,
        )
        self.theme.grid(row=0, column=3)
        self.theme.set(THEME_LABELS[self.language][self.cfg.theme])

        left = ctk.CTkScrollableFrame(self, width=405, corner_radius=0)
        left.grid(row=1, column=0, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)

        self._title(left, 0, self._t("telegram_account"))
        self.api_id = self._entry(left, 1, self._t("api_id"))
        self.api_hash = self._entry(left, 2, self._t("api_hash"), "•")
        self.phone = self._entry(left, 3, self._t("phone"))
        ctk.CTkLabel(
            left,
            text=self._t("portable_secret_note"),
            wraplength=350,
            justify="left",
            text_color=("gray40", "gray65"),
        ).grid(row=4, column=0, padx=22, pady=(2, 10), sticky="w")

        self.load_groups_btn = ctk.CTkButton(
            left,
            text=self._t("connect_groups"),
            height=38,
            command=self._load_groups,
        )
        self.load_groups_btn.grid(row=5, column=0, padx=22, pady=(4, 16), sticky="ew")

        self._title(left, 6, self._t("destination"))
        destination_box = ctk.CTkFrame(left, fg_color="transparent")
        destination_box.grid(row=7, column=0, padx=22, pady=(6, 16), sticky="ew")
        destination_box.grid_columnconfigure(0, weight=1)

        self.group_menu = ctk.CTkOptionMenu(
            destination_box,
            values=[self._t("connect_first")],
            height=38,
            command=self._group_changed,
        )
        self.group_menu.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            destination_box,
            text=self._t("topic_label"),
            anchor="w",
            text_color=("gray40", "gray65"),
        ).grid(row=1, column=0, pady=(10, 4), sticky="ew")

        self.topic_menu = ctk.CTkOptionMenu(
            destination_box,
            values=[self._t("no_topics_group")],
            height=38,
            state="disabled",
        )
        self.topic_menu.grid(row=2, column=0, sticky="ew")

        self._title(left, 8, self._t("local_folder"))
        picker = ctk.CTkFrame(left, fg_color="transparent")
        picker.grid(row=9, column=0, padx=22, pady=(6, 8), sticky="ew")
        picker.grid_columnconfigure(0, weight=1)

        self.folder = ctk.CTkEntry(picker, placeholder_text=self._t("select_folder"))
        self.folder.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkButton(
            picker,
            text=self._t("browse"),
            width=92,
            command=self._pick_folder,
        ).grid(row=0, column=1)

        self.recursive = ctk.BooleanVar(value=True)
        self.recursive_switch = ctk.CTkSwitch(
            left,
            text=self._t("include_subfolders"),
            variable=self.recursive,
            command=self._scan,
        )
        self.recursive_switch.grid(row=10, column=0, padx=22, pady=(2, 10), sticky="w")

        self.scan_btn = ctk.CTkButton(
            left,
            text=self._t("refresh_files"),
            fg_color="transparent",
            border_width=1,
            command=self._scan,
        )
        self.scan_btn.grid(row=11, column=0, padx=22, pady=(0, 16), sticky="ew")

        self._title(left, 12, self._t("upload_section"))

        self.skip_duplicates = ctk.BooleanVar(value=True)
        self.skip_switch = ctk.CTkSwitch(
            left,
            text=self._t("skip_duplicates"),
            variable=self.skip_duplicates,
            command=self._save,
        )
        self.skip_switch.grid(row=13, column=0, padx=22, pady=(4, 12), sticky="w")

        self.start_btn = ctk.CTkButton(
            left,
            text=self._t("start_upload"),
            height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._start,
        )
        self.start_btn.grid(row=14, column=0, padx=22, pady=(4, 8), sticky="ew")

        self.resume_btn = ctk.CTkButton(
            left,
            text=self._t("resume_queue"),
            height=40,
            fg_color="transparent",
            border_width=1,
            command=self._resume,
        )
        self.resume_btn.grid(row=15, column=0, padx=22, pady=(0, 8), sticky="ew")

        self.cancel_btn = ctk.CTkButton(
            left,
            text=self._t("cancel_upload"),
            height=38,
            state="disabled",
            fg_color="transparent",
            border_width=1,
            command=self._cancel,
        )
        self.cancel_btn.grid(row=16, column=0, padx=22, pady=(0, 8), sticky="ew")

        self.history_btn = ctk.CTkButton(
            left,
            text=self._t("view_history"),
            height=38,
            fg_color="transparent",
            border_width=1,
            command=self._open_history,
        )
        self.history_btn.grid(row=17, column=0, padx=22, pady=(0, 26), sticky="ew")

        right = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        right.grid(row=1, column=1, padx=24, pady=22, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            right,
            text=self._t("progress"),
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.status = ctk.CTkLabel(
            right,
            text=self._t("ready"),
            anchor="w",
            text_color=("gray35", "gray70"),
        )
        self.status.grid(row=1, column=0, pady=(4, 14), sticky="ew")

        card = ctk.CTkFrame(right)
        card.grid(row=2, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        self.current = ctk.CTkLabel(
            card,
            text=self._t("no_current_file"),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        self.current.grid(row=0, column=0, padx=18, pady=(16, 4), sticky="ew")

        self.file_bar = ctk.CTkProgressBar(card, height=14)
        self.file_bar.set(0)
        self.file_bar.grid(row=1, column=0, padx=18, pady=8, sticky="ew")

        self.file_pct = ctk.CTkLabel(
            card,
            text="0%",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.file_pct.grid(row=1, column=1, padx=(2, 18))

        self.details = ctk.CTkLabel(card, text="—", anchor="w")
        self.details.grid(row=2, column=0, columnspan=2, padx=18, pady=(0, 16), sticky="ew")

        total = ctk.CTkFrame(right, fg_color="transparent")
        total.grid(row=3, column=0, pady=(18, 10), sticky="ew")
        total.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            total,
            text=self._t("total_progress"),
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.total_pct = ctk.CTkLabel(total, text="0%")
        self.total_pct.grid(row=0, column=1, sticky="e")

        self.total_bar = ctk.CTkProgressBar(total, height=10)
        self.total_bar.set(0)
        self.total_bar.grid(row=1, column=0, columnspan=2, pady=(6, 0), sticky="ew")

        qcard = ctk.CTkFrame(right)
        qcard.grid(row=4, column=0, pady=(12, 0), sticky="nsew")
        qcard.grid_columnconfigure(0, weight=1)
        qcard.grid_rowconfigure(1, weight=1)

        self.queue_title = ctk.CTkLabel(
            qcard,
            text=self._t("files_found", count=0),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        self.queue_title.grid(row=0, column=0, padx=18, pady=(14, 8), sticky="ew")

        self.file_list = ctk.CTkTextbox(qcard, wrap="none", font=("Consolas", 12))
        self.file_list.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self.file_list.configure(state="disabled")

    @staticmethod
    def _title(parent, row: int, text: str):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=row, column=0, padx=22, pady=(14, 4), sticky="w")

    @staticmethod
    def _entry(parent, row: int, placeholder: str, show: str = ""):
        widget = ctk.CTkEntry(parent, placeholder_text=placeholder, show=show, height=38)
        widget.grid(row=row, column=0, padx=22, pady=5, sticky="ew")
        return widget

    def _restore(self):
        self.api_id.insert(0, self.cfg.api_id)
        self.api_hash.insert(0, load_api_hash())
        self.phone.insert(0, self.cfg.phone)
        self.folder.insert(0, self.cfg.last_folder)
        self.recursive.set(self.cfg.recursive)
        self.skip_duplicates.set(self.cfg.skip_duplicates)

        if self.groups:
            self._set_groups(self.groups.values())
        if self.cfg.last_folder:
            self._scan()

    def _save(self):
        if not hasattr(self, "api_id"):
            return

        theme_reverse = {label: key for key, label in THEME_LABELS[self.language].items()}
        current_theme = theme_reverse.get(self.theme.get(), self.cfg.theme)

        self.cfg = AppConfig(
            api_id=self.api_id.get().strip(),
            phone=self.phone.get().strip(),
            last_folder=self.folder.get().strip(),
            recursive=bool(self.recursive.get()),
            theme=current_theme,
            language=self.language,
            skip_duplicates=bool(self.skip_duplicates.get()),
        )
        save_config(self.cfg)
        save_api_hash(self.api_hash.get().strip())

    def _language_changed(self, label: str):
        if self._working():
            return
        reverse = {name: code for code, name in SUPPORTED_LANGUAGES.items()}
        new_language = reverse.get(label, self.language)
        if new_language == self.language:
            return

        self._save()
        self.language = new_language
        self.cfg.language = new_language
        save_config(self.cfg)

        for child in self.winfo_children():
            child.destroy()

        self._build()
        self._restore()
        self._refresh_resume(show_status=False)

    def _theme_changed(self, label: str):
        reverse = {name: key for key, name in THEME_LABELS[self.language].items()}
        value = reverse.get(label, "System")
        ctk.set_appearance_mode(value)
        self.cfg.theme = value
        self._save()

    def _service(self) -> TelegramService:
        try:
            api_id = int(self.api_id.get().strip())
        except ValueError as exc:
            raise ValueError(self._t("api_id_numeric")) from exc

        api_hash = self.api_hash.get().strip()
        phone = self.phone.get().strip()
        if not api_hash:
            raise ValueError(self._t("api_hash_required"))
        if not phone:
            raise ValueError(self._t("phone_format_required"))

        return TelegramService(
            api_id,
            api_hash,
            phone,
            self._prompt,
            language=self.language,
        )

    def _prompt(self, title: str, text: str, secret: bool) -> str | None:
        req = PromptRequest(title, text, secret)
        self.events.put(("prompt", req))
        req.done.wait()
        return req.response

    def _pick_folder(self):
        value = filedialog.askdirectory(title=self._t("choose_folder_title"))
        if value:
            self.folder.delete(0, "end")
            self.folder.insert(0, value)
            self._scan()

    def _scan(self):
        folder_text = self.folder.get().strip()
        if not folder_text:
            self.files = []
            self.queue_title.configure(text=self._t("files_found", count=0))
            self.file_list.configure(state="normal")
            self.file_list.delete("1.0", "end")
            self.file_list.configure(state="disabled")
            self._save()
            return

        root = Path(folder_text)
        if not root.is_dir():
            self.files = []
        else:
            iterator = root.rglob("*") if self.recursive.get() else root.glob("*")
            self.files = sorted(
                (p for p in iterator if p.is_file()),
                key=lambda p: str(p).casefold(),
            )

        self.queue_title.configure(text=self._t("files_found", count=len(self.files)))
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")

        for index, path in enumerate(self.files, 1):
            try:
                name = path.relative_to(root)
            except ValueError:
                name = path.name
            self.file_list.insert("end", f"{index:04d}  {name}\n")

        self.file_list.configure(state="disabled")
        self._save()

    def _show_job_queue(self, job_id: str):
        items = self.store.items_for_job(job_id)
        self.queue_title.configure(text=self._t("files_found", count=len(items)))
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")

        marker = {
            "completed": "✓",
            "skipped_duplicate": "↷",
            "failed": "!",
            "uploading": "→",
            "pending": "·",
        }
        for item in items:
            self.file_list.insert(
                "end",
                f"{item.position:04d} [{marker.get(item.status, '·')}] {item.relative_path}\n",
            )
        self.file_list.configure(state="disabled")

    def _load_groups(self):
        if self._working():
            return
        try:
            service = self._service()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return

        self._save()
        self._busy(True, self._t("connecting"))
        self._thread(lambda: self.events.put(("groups", service.list_groups())))

    def _set_groups(self, groups):
        group_list = list(groups)
        self.groups = {f"{g.title}  ·  {g.id}": g for g in group_list}
        values = list(self.groups) or [self._t("no_groups")]
        self.group_menu.configure(values=values)
        self.group_menu.set(values[0])
        self.topics = {}
        self.topic_menu.configure(
            values=[self._t("no_topics_group")],
            state="disabled",
        )
        self.topic_menu.set(self._t("no_topics_group"))

    def _group_changed(self, _value: str | None = None):
        selected = self.groups.get(self.group_menu.get())
        self.topics = {}

        if not selected:
            self.topic_menu.configure(
                values=[self._t("no_topics_group")],
                state="disabled",
            )
            self.topic_menu.set(self._t("no_topics_group"))
            return

        if not selected.has_topics:
            self.topic_menu.configure(
                values=[self._t("no_topics_group")],
                state="disabled",
            )
            self.topic_menu.set(self._t("no_topics_group"))
            return

        self.topic_menu.configure(
            values=[self._t("general_topic")],
            state="disabled",
        )
        self.topic_menu.set(self._t("general_topic"))

        if self._working():
            self.after(120, self._group_changed)
            return

        try:
            service = self._service()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return

        group_id = selected.id
        self._busy(True, self._t("loading_topics"))

        def work():
            try:
                topics = service.list_topics(group_id)
                self.events.put(("topics", (group_id, topics)))
            except Exception as exc:
                self.events.put(("topic_error", (group_id, str(exc))))

        self._thread(work)

    def _set_topics(self, group_id: int, topics):
        selected = self.groups.get(self.group_menu.get())
        if not selected or selected.id != group_id:
            return

        topic_list = list(topics)
        self.topics = {f"{t.title}  ·  {t.id}": t for t in topic_list}
        values = [self._t("general_topic"), *self.topics.keys()]
        self.topic_menu.configure(values=values, state="normal")
        self.topic_menu.set(values[0])
        self.status.configure(text=self._t("topics_loaded", count=len(topic_list)))

    def _destination_name(self, group_title: str, topic_title: str | None) -> str:
        return group_title if not topic_title else f"{group_title} › {topic_title}"

    def _start(self):
        if self._working():
            return
        try:
            service = self._service()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return

        self._scan()
        selected = self.groups.get(self.group_menu.get())
        selected_topic = self.topics.get(self.topic_menu.get())
        if not self.files:
            messagebox.showwarning(APP_TITLE, self._t("no_files_warning"))
            return
        if not selected:
            messagebox.showwarning(APP_TITLE, self._t("choose_group_warning"))
            return

        root = Path(self.folder.get().strip())
        self._save()
        job_id = self.store.create_job(
            self.files,
            root,
            selected.id,
            selected.title,
            bool(self.recursive.get()),
            topic_id=selected_topic.id if selected_topic else None,
            topic_title=selected_topic.title if selected_topic else None,
        )
        self._show_job_queue(job_id)
        self._run_job(job_id, service, self._t("preparing"))

    def _resume(self):
        if self._working():
            return

        job = self.store.latest_resumable_job()
        if not job:
            messagebox.showinfo(APP_TITLE, self._t("resume_missing"))
            self._refresh_resume(show_status=False)
            return

        destination = self._destination_name(job.group_title, job.topic_title)
        if not messagebox.askyesno(
            self._t("resume_confirm_title"),
            self._t("resume_confirm_text", group=destination),
        ):
            return

        try:
            service = self._service()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return

        self._save()
        self._show_job_queue(job.id)
        self._run_job(
            job.id,
            service,
            self._t("resume_started", group=destination),
        )

    def _run_job(self, job_id: str, service: TelegramService, initial_status: str):
        self.active_job_id = job_id
        self.cancel_event.clear()
        self._reset_progress()
        skip_duplicates = bool(self.skip_duplicates.get())
        self._busy(True, initial_status, uploading=True)

        def work():
            summary = service.upload_job(
                store=self.store,
                job_id=job_id,
                cancel_event=self.cancel_event,
                skip_duplicates=skip_duplicates,
                on_progress=lambda p: self.events.put(("progress", p)),
                on_status=lambda s: self.events.put(("status", s)),
            )
            self.events.put(("complete", summary))

        self._thread(work)

    def _thread(self, fn):
        def runner():
            try:
                fn()
            except UploadCancelled as exc:
                self.events.put(("cancelled", str(exc)))
            except Exception as exc:
                self.events.put(("error", str(exc)))
            finally:
                self.events.put(("busy", False))

        self.worker = threading.Thread(target=runner, daemon=True)
        self.worker.start()

    def _working(self) -> bool:
        return bool(self.worker and self.worker.is_alive())

    def _cancel(self):
        self.cancel_event.set()
        self.cancel_btn.configure(state="disabled")
        self.status.configure(text=self._t("cancelling"))

    def _busy(self, busy: bool, status: str | None = None, uploading: bool = False):
        state = "disabled" if busy else "normal"
        self.load_groups_btn.configure(state=state)
        self.scan_btn.configure(state=state)
        self.start_btn.configure(state=state)
        self.history_btn.configure(state=state)
        self.language_menu.configure(state=state)
        self.group_menu.configure(state=state)
        if busy:
            self.topic_menu.configure(state="disabled")
        else:
            selected = self.groups.get(self.group_menu.get())
            self.topic_menu.configure(
                state="normal" if selected and selected.has_topics else "disabled"
            )
        self.resume_btn.configure(
            state="disabled" if busy else ("normal" if self.store.latest_resumable_job() else "disabled")
        )
        self.cancel_btn.configure(state="normal" if busy and uploading else "disabled")
        if status:
            self.status.configure(text=status)

    def _reset_progress(self):
        self.file_bar.set(0)
        self.total_bar.set(0)
        self.file_pct.configure(text="0%")
        self.total_pct.configure(text="0%")
        self.current.configure(text=self._t("no_current_file"))
        self.details.configure(text="—")

    def _show_progress(self, progress: UploadProgress):
        self.file_bar.set(progress.file_percent / 100)
        self.total_bar.set(progress.total_percent / 100)
        self.file_pct.configure(text=f"{progress.file_percent:5.1f}%")
        self.total_pct.configure(text=f"{progress.total_percent:5.1f}%")
        self.current.configure(
            text=f"{progress.file_index}/{progress.file_count}  ·  {progress.file_name}"
        )
        self.details.configure(
            text=self._t(
                "summary_details",
                sent=fmt_bytes(progress.file_sent),
                total=fmt_bytes(progress.file_total),
                speed=fmt_bytes(progress.bytes_per_second),
            )
        )

    def _refresh_resume(self, show_status: bool):
        job = self.store.latest_resumable_job()
        if job:
            self.resume_btn.configure(state="normal" if not self._working() else "disabled")
            if show_status:
                self.status.configure(
                    text=self._t(
                        "resume_available",
                        done=job.done_files,
                        total=job.total_files,
                        group=self._destination_name(job.group_title, job.topic_title),
                    )
                )
        else:
            self.resume_btn.configure(state="disabled")

    def _open_history(self):
        try:
            entries = self.store.history()
            HistoryWindow(self, self.language, entries)
        except Exception as exc:
            messagebox.showerror(
                APP_TITLE,
                self._t("history_open_error", error=str(exc)),
            )

    def _pump(self):
        try:
            while True:
                event, data = self.events.get_nowait()

                if event == "prompt":
                    dialog = InputDialog(
                        self,
                        data.title,
                        data.text,
                        data.secret,
                        self.language,
                    )
                    self.wait_window(dialog)
                    data.response = dialog.result
                    data.done.set()

                elif event == "groups":
                    self._set_groups(data)
                    self.status.configure(text=self._t("connected", count=len(self.groups)))
                    self.after(120, self._group_changed)

                elif event == "topics":
                    group_id, topics = data
                    self._set_topics(group_id, topics)

                elif event == "topic_error":
                    group_id, error = data
                    selected = self.groups.get(self.group_menu.get())
                    if selected and selected.id == group_id:
                        self.topic_menu.configure(
                            values=[self._t("general_topic")],
                            state="normal",
                        )
                        self.topic_menu.set(self._t("general_topic"))
                        self.status.configure(
                            text=self._t("topic_load_error", error=error)
                        )

                elif event == "progress":
                    self._show_progress(data)

                elif event == "status":
                    self.status.configure(text=str(data))

                elif event == "complete":
                    summary: UploadSummary = data
                    if self.active_job_id:
                        self._show_job_queue(self.active_job_id)

                    if summary.failed:
                        text = self._t("upload_with_failures", failed=summary.failed)
                        self.status.configure(text=text)
                        messagebox.showwarning(APP_TITLE, text)
                    else:
                        text = self._t(
                            "upload_success",
                            uploaded=summary.uploaded,
                            skipped=summary.skipped,
                        )
                        self.status.configure(text=text)
                        messagebox.showinfo(APP_TITLE, text)

                elif event == "cancelled":
                    if self.active_job_id:
                        self._show_job_queue(self.active_job_id)
                    self.status.configure(text=data or self._t("cancelled"))

                elif event == "error":
                    if self.active_job_id:
                        self._show_job_queue(self.active_job_id)
                    self.status.configure(text=self._t("error_status"))
                    messagebox.showerror(APP_TITLE, str(data))

                elif event == "busy" and not data:
                    self._busy(False)
                    self._refresh_resume(show_status=False)

        except queue.Empty:
            pass

        self.after(60, self._pump)


def fmt_bytes(value: float) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def run_app():
    App().mainloop()
