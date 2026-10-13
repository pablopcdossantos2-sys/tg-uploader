# TG Uploader

**Read this README in other languages:** [Português](README.md) · [Español](README.es.md)

A portable Windows desktop application written in Python for uploading files from a local folder to Telegram groups, with a modern GUI, real progress tracking, upload history, duplicate prevention, and interrupted queue recovery.

> Independent, unofficial project. TG Uploader uses the Telegram API through Telethon and is not affiliated with Telegram.

## Features

- modern `CustomTkinter` interface;
- **Português (Brasil)**, **English**, and **Español**;
- persistent language preference;
- Telegram account authentication inside the GUI;
- verification-code and two-step-password support;
- automatic listing of groups available to the connected account;
- local folder selection using the Windows file picker;
- optional recursive subfolder scanning;
- queue preview;
- real progress for the current file;
- total queue progress;
- average transfer speed;
- upload cancellation;
- **persistent upload history**;
- **duplicate-file prevention**;
- **interrupted queue recovery**;
- portable distribution with no installer;
- compiled version that does not require Python on the destination computer;
- local build through `build_portable.bat`;
- automatic Windows build through GitHub Actions.

## Upload history

TG Uploader stores its local history in:

```text
data\tg_uploader.db
```

The SQLite database records information such as:

- date and time;
- destination group;
- file;
- file size;
- SHA-256 hash;
- upload status;
- Telegram message ID when available.

The history is available directly in the GUI through **View upload history**.

## Duplicate prevention

By default, this option is enabled:

**Skip files already uploaded to the same group**

Before uploading a file, TG Uploader calculates its **SHA-256** and checks the local history.

A file is considered a duplicate when:

1. it has the same content, represented by the same SHA-256; and
2. that content has already been uploaded to the same Telegram group.

Renaming a file therefore does not bypass duplicate detection.

The same file can still be uploaded normally to a different group.

To deliberately upload identical content again to the same group, disable duplicate prevention before creating a new queue.

## Interrupted queue recovery

The queue is written to SQLite before the upload begins.

Each item is updated after processing. If the application closes, the computer restarts, or the connection fails:

- completed files remain completed;
- previously skipped duplicates remain completed;
- pending files remain pending;
- a file that was actively uploading returns to pending state;
- failed files can be attempted again.

When a recoverable queue exists, **Resume interrupted queue** becomes available the next time the application starts.

### Important limitation

Recovery works **at file level**, not from an arbitrary byte offset inside a file.

For example, if a 2 GB file is interrupted after 1 GB, that individual file starts again from the beginning. Files completed earlier in the queue are not uploaded again.

## Languages

Use the language selector in the application header:

- Português (Brasil);
- English;
- Español.

The preference is saved in `data/config.json`.

## Portable version

The compiled distribution has approximately this structure:

```text
TG-Uploader/
├── TG-Uploader.exe
├── _internal/
├── data/
├── README.md
├── README.en.md
├── README.es.md
└── PORTABLE.md
```

The whole folder can be moved to another directory, an external drive, or a USB flash drive.

The destination computer **does not need Python installed**.

See [PORTABLE.md](PORTABLE.md) for additional portable-mode details.

## Portable data and security

The `data/` folder travels with the application and may contain:

- configuration;
- upload history and queues;
- API ID;
- API Hash;
- the authenticated Telegram session.

**Do not share or publish the `data/` folder.**

It is already excluded by `.gitignore`.

If a copy containing your session is lost, revoke that session under:

**Telegram → Settings → Devices**

To give someone else a clean copy, distribute the application with an empty `data/` folder.

## Requirements for a ready-to-use portable build

- Windows 10 or Windows 11;
- internet access;
- a Telegram account that can access the destination group;
- your own `api_id` and `api_hash` from <https://my.telegram.org>.

Python is not required on the computer running an already compiled build.

## Create Telegram API credentials

1. Open <https://my.telegram.org>.
2. Sign in with the account you will use with TG Uploader.
3. Open **API development tools**.
4. Create an application.
5. Save the **App api_id** and **App api_hash** values.

Never publish your API Hash, verification code, password, or session file.

## Build the portable version with two clicks

The computer used for building needs Python 3.11 or newer.

After downloading or cloning the repository, run:

```text
build_portable.bat
```

The finished application will be created in:

```text
dist\TG-Uploader
```

Copy the complete `TG-Uploader` folder.

## Build with GitHub Actions

The workflow:

```text
.github/workflows/build-windows.yml
```

creates the artifact:

```text
TG-Uploader-Windows-Portable
```

It can also be started manually from the repository's **Actions** tab.

## Run from source

Clone the project:

```powershell
git clone https://github.com/pablopcdossantos2-sys/tg-uploader.git
cd tg-uploader
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run:

```powershell
python main.py
```

## First use

1. Open TG Uploader.
2. Choose your language.
3. Enter **API ID**.
4. Enter **API Hash**.
5. Enter the phone number in international format.
6. Click **Connect and load groups**.
7. Enter the code sent by Telegram.
8. Enter the two-step password if required.
9. Select the destination group.
10. Select the local folder.
11. Review the queue.
12. Keep duplicate protection enabled or disable it as needed.
13. Click **Start upload**.

## Project structure

```text
tg-uploader/
├── .github/
│   └── workflows/
│       └── build-windows.yml
├── build_portable.bat
├── main.py
├── PORTABLE.md
├── README.md
├── README.en.md
├── README.es.md
├── requirements.txt
└── src/
    ├── __init__.py
    ├── config.py
    ├── i18n.py
    ├── storage.py
    ├── telegram_service.py
    └── ui.py
```

## References

- Telegram — API ID and API Hash: <https://core.telegram.org/api/obtaining_api_id>
- Telegram — API Terms of Service: <https://core.telegram.org/api/terms>
- Telethon: <https://docs.telethon.dev/>
- PyInstaller: <https://pyinstaller.org/>

## License

Not defined yet. Add an appropriate license before distributing public releases.
