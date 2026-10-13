# TG Uploader

**Read this README in other languages:** [Português](README.md) · [Español](README.es.md)

A portable Windows desktop application for uploading files from a local folder to Telegram groups, with a modern interface, real progress tracking, upload history, duplicate prevention, and interrupted queue recovery.

> Independent, unofficial project. TG Uploader uses the Telegram API through Telethon and is not affiliated with Telegram.

---

# For users who only want to run the application

If you are **not comfortable with Terminal, PowerShell, Python, or GitHub**, this is the most important part of the README.

You **do not need to install Python** and **do not need to type commands** to use an already compiled portable build.

## Step 1 — Download the portable version

1. Open the project page on GitHub.
2. Click the **Actions** tab.
3. Open the most recent successful **Build portable Windows app** run.
4. Scroll down to **Artifacts**.
5. Click **TG-Uploader-Windows-Portable**.
6. Your browser will download a `.zip` file.

> If someone already gave you the portable folder, skip this step.

## Step 2 — Extract the ZIP

1. Open the Windows **Downloads** folder.
2. Find the downloaded ZIP.
3. Right-click it.
4. Choose **Extract All...**.
5. Select an easy-to-find location, for example:

```text
C:\Programs\TG-Uploader
```

6. Click **Extract**.

Do not run the application directly from inside the ZIP.

## Step 3 — Open TG Uploader

Open the extracted folder.

Find:

```text
TG-Uploader.exe
```

Double-click it.

Windows may display a security warning because the executable is not yet signed with a commercial code-signing certificate. If you trust the copy downloaded from this repository, use the Windows options to continue.

---

# Before first use: create Telegram API credentials

Telegram requires applications using its API to have:

- an **API ID**
- an **API Hash**

You normally do this only once for your account.

## Step 1 — Sign in to Telegram's website

1. Open your browser.
2. Go to:

<https://my.telegram.org>

3. Enter your Telegram phone number in international format.
4. Telegram will send a code to your account.
5. Enter that code on the website.

## Step 2 — Open API development tools

After signing in:

1. click **API development tools**;
2. create an application if requested.

Example values:

```text
App title: TG Uploader
Short name: tguploader
Platform: Desktop
```

## Step 3 — Save API ID and API Hash

You will see values similar to:

```text
App api_id: 12345678
App api_hash: abcdef1234567890abcdef1234567890
```

Keep both values.

Do not publish your API Hash in screenshots, forum posts, videos, or Git commits.

---

# First use of TG Uploader

## Step 1 — Choose the language

Use the language menu at the top of the window:

- Português (Brasil)
- English
- Español

The choice is saved automatically.

## Step 2 — Enter account details

Under **1. Telegram account**:

1. enter the numeric **API ID**;
2. paste the **API Hash**;
3. enter your phone number in international format.

Example:

```text
+15551234567
```

## Step 3 — Connect to Telegram

Click:

**Connect and load groups**

On first use, Telegram sends a verification code.

TG Uploader opens a small dialog.

Enter the code and click **Confirm**.

If your account uses two-step verification, another dialog asks for that password.

## Step 4 — Choose the destination group

After connecting, TG Uploader loads the groups available to your account.

Under **2. Destination**:

1. open the list;
2. click the group you want.

Your account must be allowed to upload files to that group.

## Step 5 — Choose the local folder

Under **3. Local folder**:

1. click **Browse**;
2. navigate using Windows File Explorer;
3. select the folder containing the files;
4. confirm the folder selection.

The files appear on the right side.

Keep **Include files from subfolders** enabled if you want recursive scanning.

## Step 6 — Check duplicate protection

By default:

**Skip files already uploaded to the same group**

is enabled.

We recommend leaving it enabled.

TG Uploader calculates the SHA-256 of each file and checks whether the same content was already uploaded to that same group.

Renaming a file does not bypass this check.

## Step 7 — Start uploading

Click:

**Start upload**

You will see:

- current file;
- file percentage;
- total progress;
- file count;
- bytes transferred;
- average speed.

You can click **Cancel upload** at any time.

---

# If the application closes or the connection drops

You do not need to start over.

The queue is stored in:

```text
data\tg_uploader.db
```

When you reopen the app, **Resume interrupted queue** becomes available if there is recoverable work.

Completed files are not uploaded again.

## Important recovery limitation

Recovery works per file.

Example:

- file 1 completed: it is not uploaded again;
- file 2 stopped at 50%: that file restarts from the beginning;
- later files remain pending.

This version does not resume from the exact byte offset inside a partially uploaded file.

---

# View upload history

Click:

**View upload history**

The window shows information such as:

- date and time;
- status;
- group;
- filename;
- size.

History is stored locally in:

```text
data\tg_uploader.db
```

---

# About the data folder

The folder:

```text
data\
```

may contain:

- settings;
- language choice;
- upload history;
- pending queues;
- API ID;
- API Hash;
- authenticated Telegram session.

**Do not share this folder.**

To give somebody a clean copy:

1. close TG Uploader;
2. copy the complete application folder;
3. empty the `data\` folder in the copy;
4. give them that clean copy.

They can authenticate their own account.

---

# Use TG Uploader from a USB drive

TG Uploader is portable.

Copy the entire:

```text
TG-Uploader
```

folder to a USB drive, external HDD, or external SSD.

Do not copy only `TG-Uploader.exe`.

The `_internal` folder is also required.

---

# Build the portable version yourself

This section is for developers or users who want to produce their own executable.

If you only want to use TG Uploader, you can ignore this entire section.

## Easiest method: build_portable.bat

### Step 1 — Install Python

1. Go to <https://www.python.org/downloads/>.
2. Download a recent Python 3 version.
3. Open the installer.
4. On the first screen, enable:

```text
Add Python to PATH
```

5. Click **Install Now**.
6. Wait for installation to finish.

### Step 2 — Download the source code

On the GitHub repository page:

1. click the green **Code** button;
2. choose **Download ZIP**;
3. open Downloads;
4. right-click the ZIP;
5. choose **Extract All...**.

### Step 3 — Run the build script

Inside the extracted folder, find:

```text
build_portable.bat
```

Double-click it.

A black window opens. This is normal.

You **do not need to type anything**.

The script automatically:

- prepares the build environment;
- installs libraries;
- validates the source;
- runs tests;
- compiles the application;
- prepares the portable folder.

When you see:

```text
Build concluido com sucesso.
```

the portable application is available in:

```text
dist\TG-Uploader
```

---

# Run from source — beginner-friendly PowerShell tutorial

Only use this section if you want to develop or directly test the Python source.

## Step 1 — Open PowerShell in the correct folder

1. Open the project folder in **File Explorer**.
2. Click the address bar at the top.
3. Delete the current path.
4. Type:

```text
powershell
```

5. Press **Enter**.

A blue or black window opens already pointing to the correct folder.

You may see something like:

```text
PS C:\Users\YourName\Downloads\tg-uploader-main>
```

Your path will probably be different. That is normal.

## Step 2 — Create a virtual environment

Copy:

```powershell
python -m venv .venv
```

Paste it into PowerShell and press **Enter**.

A new `.venv` folder should be created.

## Step 3 — Activate it

Run:

```powershell
.\.venv\Scripts\Activate.ps1
```

If successful, the prompt starts with something similar to:

```text
(.venv) PS C:\...
```

### If PowerShell blocks script execution

You can skip activation and use the virtual-environment Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Step 4 — Install dependencies

Run:

```powershell
python -m pip install --upgrade pip
```

Wait until it finishes.

Then run:

```powershell
python -m pip install -r requirements.txt
```

Many lines will appear. This is normal.

Wait until PowerShell displays a new prompt line.

## Step 5 — Start TG Uploader

Run:

```powershell
python main.py
```

The TG Uploader window should open.

---

# Common problems

## “python is not recognized”

Try:

```powershell
py --version
```

If that works, replace `python` with `py` in the commands.

If neither works, reinstall Python and enable **Add Python to PATH**.

## PowerShell opened in the wrong folder

Close it and repeat:

1. open the correct folder in File Explorer;
2. click the address bar;
3. type `powershell`;
4. press Enter.

## The group is missing

Check that:

- the authenticated account is a member of the group;
- the account has access to it;
- you authenticated the intended Telegram account.

## “Resume interrupted queue” is unavailable

It only becomes available when an incomplete queue exists in the local database.

## A duplicate file was skipped

That is expected when duplicate protection is enabled.

Disable **Skip files already uploaded to the same group** before creating a new queue if you intentionally want to upload the same content again.

---

# Portable folder structure

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

# References

- Telegram — API ID and API Hash: <https://core.telegram.org/api/obtaining_api_id>
- Telegram — API Terms of Service: <https://core.telegram.org/api/terms>
- Telethon: <https://docs.telethon.dev/>
- PyInstaller: <https://pyinstaller.org/>

# License

Not defined yet. Add an appropriate license before distributing public releases.
