from __future__ import annotations

import queue
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .config import AppConfig, load_api_hash, load_config, save_api_hash, save_config
from .telegram_service import GroupInfo, TelegramService, UploadCancelled, UploadProgress

APP_TITLE = "TG Uploader"


class PromptRequest:
    def __init__(self, title: str, text: str, secret: bool):
        self.title, self.text, self.secret = title, text, secret
        self.response: str | None = None
        self.done = threading.Event()


class InputDialog(ctk.CTkToplevel):
    def __init__(self, master, title: str, text: str, secret: bool):
        super().__init__(master)
        self.result: str | None = None
        self.title(title)
        self.geometry("440x210")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=text, wraplength=390, justify="left").grid(
            row=0, column=0, padx=24, pady=(24, 12), sticky="ew"
        )
        self.entry = ctk.CTkEntry(self, show="•" if secret else "", height=38)
        self.entry.grid(row=1, column=0, padx=24, sticky="ew")
        self.entry.focus_set()
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=2, column=0, padx=24, pady=24, sticky="e")
        ctk.CTkButton(row, text="Cancelar", width=100, fg_color="transparent", border_width=1,
                      command=self.cancel).pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="Confirmar", width=110, command=self.ok).pack(side="left")
        self.bind("<Return>", lambda _e: self.ok())
        self.bind("<Escape>", lambda _e: self.cancel())
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def ok(self):
        self.result = self.entry.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class App(ctk.CTk):
    def __init__(self):
        self.cfg = load_config()
        ctk.set_appearance_mode(self.cfg.theme or "System")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x760")
        self.minsize(1040, 680)

        self.events: queue.Queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.groups: dict[str, GroupInfo] = {}
        self.files: list[Path] = []

        self._build()
        self._restore()
        self.after(60, self._pump)

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="TG Uploader", font=ctk.CTkFont(size=26, weight="bold")).grid(
            row=0, column=0, padx=26, pady=(14, 0), sticky="w"
        )
        ctk.CTkLabel(header, text="Envio de pastas para grupos com progresso real em tempo real.",
                     text_color=("gray35", "gray70")).grid(row=1, column=0, padx=26, pady=(0, 12), sticky="w")
        self.theme = ctk.CTkOptionMenu(header, values=["System", "Dark", "Light"], width=110,
                                       command=self._theme_changed)
        self.theme.grid(row=0, column=1, rowspan=2, padx=24)

        left = ctk.CTkScrollableFrame(self, width=390, corner_radius=0)
        left.grid(row=1, column=0, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)

        self._title(left, 0, "1. Conta Telegram")
        self.api_id = self._entry(left, 1, "API ID")
        self.api_hash = self._entry(left, 2, "API Hash", "•")
        self.phone = self._entry(left, 3, "Telefone (+55...)")
        ctk.CTkLabel(left, text="O API Hash pode ser salvo no gerenciador de credenciais do sistema.",
                     wraplength=330, justify="left", text_color=("gray40", "gray65")).grid(
            row=4, column=0, padx=22, pady=(2, 10), sticky="w"
        )
        self.load_groups_btn = ctk.CTkButton(left, text="Conectar e carregar grupos", height=38,
                                             command=self._load_groups)
        self.load_groups_btn.grid(row=5, column=0, padx=22, pady=(4, 16), sticky="ew")

        self._title(left, 6, "2. Destino")
        self.group_menu = ctk.CTkOptionMenu(left, values=["Conecte a conta primeiro"], height=38)
        self.group_menu.grid(row=7, column=0, padx=22, pady=(6, 16), sticky="ew")

        self._title(left, 8, "3. Pasta local")
        picker = ctk.CTkFrame(left, fg_color="transparent")
        picker.grid(row=9, column=0, padx=22, pady=(6, 8), sticky="ew")
        picker.grid_columnconfigure(0, weight=1)
        self.folder = ctk.CTkEntry(picker, placeholder_text="Selecione uma pasta")
        self.folder.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkButton(picker, text="Procurar", width=92, command=self._pick_folder).grid(row=0, column=1)
        self.recursive = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(left, text="Incluir arquivos das subpastas", variable=self.recursive,
                      command=self._scan).grid(row=10, column=0, padx=22, pady=(2, 12), sticky="w")
        self.scan_btn = ctk.CTkButton(left, text="Atualizar lista de arquivos", fg_color="transparent",
                                      border_width=1, command=self._scan)
        self.scan_btn.grid(row=11, column=0, padx=22, pady=(0, 16), sticky="ew")

        self._title(left, 12, "4. Envio")
        self.start_btn = ctk.CTkButton(left, text="Iniciar upload", height=44,
                                       font=ctk.CTkFont(size=15, weight="bold"), command=self._start)
        self.start_btn.grid(row=13, column=0, padx=22, pady=(8, 8), sticky="ew")
        self.cancel_btn = ctk.CTkButton(left, text="Cancelar upload", height=38, state="disabled",
                                        fg_color="transparent", border_width=1, command=self._cancel)
        self.cancel_btn.grid(row=14, column=0, padx=22, pady=(0, 26), sticky="ew")

        right = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        right.grid(row=1, column=1, padx=24, pady=22, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(4, weight=1)
        ctk.CTkLabel(right, text="Progresso", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, sticky="w")
        self.status = ctk.CTkLabel(right, text="Pronto para começar.", anchor="w",
                                   text_color=("gray35", "gray70"))
        self.status.grid(row=1, column=0, pady=(4, 14), sticky="ew")

        card = ctk.CTkFrame(right)
        card.grid(row=2, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        self.current = ctk.CTkLabel(card, text="Nenhum arquivo em envio",
                                    font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        self.current.grid(row=0, column=0, padx=18, pady=(16, 4), sticky="ew")
        self.file_bar = ctk.CTkProgressBar(card, height=14)
        self.file_bar.set(0)
        self.file_bar.grid(row=1, column=0, padx=18, pady=8, sticky="ew")
        self.file_pct = ctk.CTkLabel(card, text="0%", font=ctk.CTkFont(size=20, weight="bold"))
        self.file_pct.grid(row=1, column=1, padx=(2, 18))
        self.details = ctk.CTkLabel(card, text="—", anchor="w")
        self.details.grid(row=2, column=0, columnspan=2, padx=18, pady=(0, 16), sticky="ew")

        total = ctk.CTkFrame(right, fg_color="transparent")
        total.grid(row=3, column=0, pady=(18, 10), sticky="ew")
        total.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(total, text="Progresso total", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        self.total_pct = ctk.CTkLabel(total, text="0%")
        self.total_pct.grid(row=0, column=1, sticky="e")
        self.total_bar = ctk.CTkProgressBar(total, height=10)
        self.total_bar.set(0)
        self.total_bar.grid(row=1, column=0, columnspan=2, pady=(6, 0), sticky="ew")

        qcard = ctk.CTkFrame(right)
        qcard.grid(row=4, column=0, pady=(12, 0), sticky="nsew")
        qcard.grid_columnconfigure(0, weight=1)
        qcard.grid_rowconfigure(1, weight=1)
        self.queue_title = ctk.CTkLabel(qcard, text="Arquivos encontrados: 0",
                                        font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        self.queue_title.grid(row=0, column=0, padx=18, pady=(14, 8), sticky="ew")
        self.file_list = ctk.CTkTextbox(qcard, wrap="none", font=("Consolas", 12))
        self.file_list.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self.file_list.configure(state="disabled")

    @staticmethod
    def _title(parent, row: int, text: str):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=row, column=0, padx=22, pady=(14, 4), sticky="w")

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
        self.theme.set(self.cfg.theme)
        if self.cfg.last_folder:
            self._scan()

    def _save(self):
        self.cfg = AppConfig(self.api_id.get().strip(), self.phone.get().strip(), self.folder.get().strip(),
                             bool(self.recursive.get()), self.theme.get())
        save_config(self.cfg)
        save_api_hash(self.api_hash.get().strip())

    def _theme_changed(self, value: str):
        ctk.set_appearance_mode(value)
        self._save()

    def _service(self) -> TelegramService:
        try:
            api_id = int(self.api_id.get().strip())
        except ValueError as exc:
            raise ValueError("API ID deve conter apenas números.") from exc
        api_hash, phone = self.api_hash.get().strip(), self.phone.get().strip()
        if not api_hash:
            raise ValueError("Informe o API Hash.")
        if not phone:
            raise ValueError("Informe o telefone no formato internacional, por exemplo +5511999999999.")
        return TelegramService(api_id, api_hash, phone, self._prompt)

    def _prompt(self, title: str, text: str, secret: bool) -> str | None:
        req = PromptRequest(title, text, secret)
        self.events.put(("prompt", req))
        req.done.wait()
        return req.response

    def _pick_folder(self):
        value = filedialog.askdirectory(title="Selecione a pasta que será enviada")
        if value:
            self.folder.delete(0, "end")
            self.folder.insert(0, value)
            self._scan()

    def _scan(self):
        root = Path(self.folder.get().strip())
        if not root.is_dir():
            self.files = []
        else:
            iterator = root.rglob("*") if self.recursive.get() else root.glob("*")
            self.files = sorted((p for p in iterator if p.is_file()), key=lambda p: str(p).casefold())
        self.queue_title.configure(text=f"Arquivos encontrados: {len(self.files)}")
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")
        for i, path in enumerate(self.files, 1):
            try:
                name = path.relative_to(root)
            except ValueError:
                name = path.name
            self.file_list.insert("end", f"{i:04d}  {name}\n")
        self.file_list.configure(state="disabled")
        self._save()

    def _load_groups(self):
        if self._working():
            return
        try:
            service = self._service()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc)); return
        self._save(); self._busy(True, "Conectando à conta e carregando grupos…")
        self._thread(lambda: self.events.put(("groups", service.list_groups())))

    def _start(self):
        if self._working():
            return
        try:
            service = self._service()
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc)); return
        self._scan()
        selected = self.groups.get(self.group_menu.get())
        if not self.files:
            messagebox.showwarning(APP_TITLE, "Nenhum arquivo foi encontrado na pasta selecionada."); return
        if not selected:
            messagebox.showwarning(APP_TITLE, "Conecte a conta e selecione um grupo de destino."); return
        self._save(); self.cancel_event.clear(); self._reset_progress(); self._busy(True, "Preparando upload…", True)

        def work():
            service.upload(
                list(self.files), selected.id, self.cancel_event,
                lambda p: self.events.put(("progress", p)),
                lambda s: self.events.put(("status", s)),
            )
            self.events.put(("complete", None))

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
        self.status.configure(text="Cancelando o upload…")

    def _busy(self, busy: bool, status: str | None = None, uploading: bool = False):
        state = "disabled" if busy else "normal"
        self.load_groups_btn.configure(state=state)
        self.scan_btn.configure(state=state)
        self.start_btn.configure(state=state)
        self.cancel_btn.configure(state="normal" if busy and uploading else "disabled")
        if status:
            self.status.configure(text=status)

    def _reset_progress(self):
        self.file_bar.set(0); self.total_bar.set(0)
        self.file_pct.configure(text="0%"); self.total_pct.configure(text="0%")

    def _show_progress(self, p: UploadProgress):
        self.file_bar.set(p.file_percent / 100); self.total_bar.set(p.total_percent / 100)
        self.file_pct.configure(text=f"{p.file_percent:5.1f}%")
        self.total_pct.configure(text=f"{p.total_percent:5.1f}%")
        self.current.configure(text=f"{p.file_index}/{p.file_count}  ·  {p.file_name}")
        self.details.configure(text=f"{fmt_bytes(p.file_sent)} de {fmt_bytes(p.file_total)}   •   {fmt_bytes(p.bytes_per_second)}/s")

    def _pump(self):
        try:
            while True:
                event, data = self.events.get_nowait()
                if event == "prompt":
                    dialog = InputDialog(self, data.title, data.text, data.secret)
                    self.wait_window(dialog); data.response = dialog.result; data.done.set()
                elif event == "groups":
                    self.groups = {f"{g.title}  ·  {g.id}": g for g in data}
                    values = list(self.groups) or ["Nenhum grupo encontrado"]
                    self.group_menu.configure(values=values); self.group_menu.set(values[0])
                    self.status.configure(text=f"Conectado. {len(self.groups)} grupo(s) encontrado(s).")
                elif event == "progress": self._show_progress(data)
                elif event == "status": self.status.configure(text=str(data))
                elif event == "complete":
                    self.status.configure(text="Upload concluído com sucesso.")
                    messagebox.showinfo(APP_TITLE, "Todos os arquivos foram enviados com sucesso.")
                elif event == "cancelled": self.status.configure(text=data or "Upload cancelado.")
                elif event == "error":
                    self.status.configure(text="Ocorreu um erro."); messagebox.showerror(APP_TITLE, str(data))
                elif event == "busy" and not data: self._busy(False)
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
