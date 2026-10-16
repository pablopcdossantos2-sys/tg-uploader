# TG Uploader

*Leia isto em outros idiomas: [Português](README.md)*

**Also available in:** [Español](README.es.md)

A portable Windows desktop application for uploading files from local folders to Telegram groups and topics, with a graphical interface, progress tracking, upload history, duplicate prevention, and interrupted queue recovery.

> Independent, unofficial project. TG Uploader uses the Telegram API through Telethon and is not affiliated with Telegram.

## 👤 Authorship and development

Portable Windows desktop application independently developed by Pablo Phillipe Cândido dos Santos, designed for organized file uploads from local folders to Telegram groups and topics, with progress tracking, history, duplicate prevention, and interrupted queue recovery.

Generative artificial intelligence tools were used as supporting resources during development, while responsibility for the project's conception, implementation, integration, and verification remained with the author.

Lattes CV: [http://lattes.cnpq.br/9500873674712528](http://lattes.cnpq.br/9500873674712528)

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

## If you already have an App api_id and App api_hash

If you previously created a Telegram application and already have:

- **App api_id**
- **App api_hash**

you **do not need to create another application just to use TG Uploader**.

In that case:

1. go to <https://my.telegram.org>;
2. sign in with the same Telegram account;
3. open **API development tools**;
4. locate the **App api_id** and **App api_hash** of the application you already control;
5. copy both values;
6. enter the `App api_id` in TG Uploader's **API ID** field and the `App api_hash` in the **API Hash** field;
7. continue normally with account authentication.

You can then **skip the new-application creation step** below.

> Only reuse credentials from an application you own or are authorized to manage. Do not use credentials found online or provided by unknown third parties.

> There is no benefit in creating multiple Telegram applications unnecessarily. If your existing credentials are valid and accessible to you, simply reuse them.

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
2. first check whether an **App api_id** and **App api_hash** are already displayed;
3. if those values already exist for an application you control, reuse them and **do not create a new application**;
4. only create a new application if you do not already have suitable credentials.

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

By default, the main window opens **maximized** so the queue and progress information are easier to see.

Fields that require typing display an in-field hint with an example or a description of the expected value.

## Step 2 — Enter account details

Under **1. Telegram account**:

1. enter the numeric **API ID**;
2. paste the **API Hash**;
3. enter your phone number in international format.

After you enter **API ID** and **API Hash** for the first time, TG Uploader saves them locally. The next time the application opens, those fields are filled automatically, so you do not need to enter them again.

The **API ID** is stored in `data/config.json` and the **API Hash** in `data/secrets.json`. These files belong to your portable copy of the application.

> If you delete the contents of the `data/` folder or use a clean copy of TG Uploader, you will need to enter the credentials again.

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

## Step 4 — Choose the group and, if needed, a topic

After connecting, TG Uploader loads the groups available to your account.

The list is designed to avoid confusion with Telegram's internal identifiers. Whenever possible, each destination is shown as:

```text
Group name · Type · @username
```

Example:

```text
Project Team · Forum · @projectteam
```

If the group has no `@username`, the application may show a **technical ID**. That number is only used to distinguish Telegram entities with the same name; you do not need to interpret it to choose the destination.

Old groups that Telegram migrated to supergroups are ignored in the list, preventing the old and new entities from appearing as duplicate names.

Under **2. Destination — group and topic**:

1. open the first list;
2. select the destination group;
3. wait a moment while TG Uploader checks whether that group uses topics.

If the group **does not use topics**, the topic field remains disabled.

If the group **uses topics**, the second list becomes available. You may choose:

- **General / no specific topic**; or
- a specific topic identified by its title and ID.

Example:

```text
Announcements · 1234
```

All files in that queue are sent to the selected topic.

The selected topic is saved with the queue. If the upload is interrupted and resumed later, the remaining files continue to the **same original topic**.

Your account must be allowed to upload files to that group.

> Duplicate prevention is also topic-aware. A file previously uploaded to topic A may still be uploaded to topic B in the same group.

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

**Skip files already uploaded to the same destination (group/topic)**

is enabled.

We recommend leaving it enabled.

TG Uploader calculates the SHA-256 of each file and checks whether the same content was already uploaded to that same destination (group/topic).

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

Disable **Skip files already uploaded to the same destination (group/topic)** before creating a new queue if you intentionally want to upload the same content again.

---

# Portable folder structure

```text
TG-Uploader/
├── TG-Uploader.exe
├── _internal/
├── data/
├── README.md
├── README-en.md
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
