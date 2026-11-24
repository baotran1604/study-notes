# Study Notes

Study Notes is a small Django and SQLite notebook. Create an account, sign in, write a note, and find it later by searching its title. Each account has its own notebook and sign-in history.

The five examples below use the OWASP Top 10 for 2021. Each fix sits beside the relevant backend code as a comment. Start with the code as shipped, try the action, then uncomment the indicated fix and restart Django. The fixes can be enabled independently.

## Run locally

Install Python 3.13 from [Python downloads](https://www.python.org/downloads/) or your OS package manager. On Debian or Ubuntu, install the matching Python venv package if virtual environment creation reports that ensurepip is missing. SQLite comes with the standard Python installer.

Open a terminal in the folder containing `manage.py`. On **Windows** run the following in PowerShell.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe init_local.py
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

On **Linux or macOS** run the following.

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python init_local.py
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Open [the notebook](http://127.0.0.1:8000/). Choose **Create an account**, register, then sign in. Enter a title and some text under **New note** and choose **Save note**. The local SQLite file keeps your notes between restarts. The setup script creates a private signing key and preserves it on later runs. Stop the local server with Ctrl+C.

## Review the five examples

| # | Category | Observed before the fix | Observed after the fix |
|---|---|---|---|
| 1 | A06 Vulnerable and Outdated Components | [Staff inventory lists Django only](screenshots/flaw-1-before-1.png) | [Inventory includes its installed dependencies](screenshots/flaw-1-after-1.png) |
| 2 | A02 Cryptographic Failures | [Note verifies on save](screenshots/flaw-2-before-1.png), then [fails after a restart](screenshots/flaw-2-before-2.png) | [The receipt still verifies after a restart](screenshots/flaw-2-after-1.png) |
| 3 | A08 Software and Data Integrity Failures | [The Weekly Review guide has no release checksum](screenshots/flaw-3-before-1.png) | [Both guides pass verification and open](screenshots/flaw-3-after-1.png) |
| 4 | A07 Identification and Authentication Failures | [Registration rejects a long passphrase](screenshots/flaw-4-before-1.png) | [The same reader registers and signs in](screenshots/flaw-4-after-1.png) |
| 5 | A09 Security Logging and Monitoring Failures | [The sign-out is missing from account history](screenshots/flaw-5-before-1.png) | [The history records the sign-out](screenshots/flaw-5-after-1.png) |

### 1. The staff package inventory misses dependencies

A staff member checking a security advisory needs to know which packages and versions the app runs. The inventory reads the installed Django distribution but overlooks packages Django uses, including `asgiref` and `sqlparse`. OWASP explicitly includes missing version information for nested dependencies under A06. This example demonstrates the inventory gap. It makes no claim about known vulnerabilities in the installed packages. [OWASP A06](https://top10.owasp.org/2021/A06_2021-Vulnerable_and_Outdated_Components/)

With the server stopped, run `.venv/bin/python manage.py createsuperuser` on Linux or macOS, or `.\.venv\Scripts\python.exe manage.py createsuperuser` on Windows. Choose your own credentials. Start the server, sign in with this account, and open **Account → Python package inventory**. Compare the one-row report with `python -m pip list` using the same virtual environment. Uncomment the assignment under **Fix 1**, restart, and refresh. The report now reads all Python distributions in that environment. Package counts vary by installation. [Inventory view](notes/reports.py)

### 2. Restarting the server loses the note receipt key

When you save a note, the backend stores an HMAC receipt covering its ID, owner, title, and text. Opening the note checks its contents against that receipt. The original settings generate a new secret at each process start. An unchanged note therefore loses its verifiable history when the process ends. OWASP includes cryptographic key management under A02. [Receipt code](notes/models.py) · [OWASP A02](https://top10.owasp.org/2021/A02_2021-Cryptographic_Failures/)

Save a new note. Check that it says **Verified**, stop Django with Ctrl+C, start it again, and refresh the same URL. The text survives, but verification fails. Uncomment the assignment under **Fix 2**, restart, and save a **new** note. Restart once more and reopen that note. Its receipt now verifies because the HMAC uses a persistent local secret and a receipt-specific context. Receipts made with a previously discarded key cannot be recovered. [Key settings](config/settings.py)

### 3. A published guide is missing its integrity record

The application ships two plain-text guides. The release manifest supplies an expected SHA-256 digest for only one of them. Readers therefore have no trusted value against which to check the Weekly Review handout. The reader refuses to display it. This example concerns coverage of the released data by the integrity manifest. It assumes the installed application and its manifest are trusted. [Release manifest and guide reader](notes/reports.py) · [OWASP A08](https://top10.owasp.org/2021/A08_2021-Software_and_Data_Integrity_Failures/)

Sign in and open **Guides**. Reading Plan is available, but Weekly Review is unavailable. Uncomment the manifest entry under **Fix 3**, restart, and refresh. The backend compares the shipped guide bytes with the recorded release digest before displaying the text. The expected digest is a fixed release value, so editing a guide on disk cannot silently update its expected value. [Bundled guides](notes/guides/)

### 4. Registration rejects long passphrases

The registration form caps passwords at 48 characters. A reader using a longer generated passphrase must shorten or replace it. OWASP refers to modern password-length guidance under A07. NIST recommends allowing a maximum of at least 64 characters. [OWASP A07](https://top10.owasp.org/2021/A07_2021-Identification_and_Authentication_Failures/) · [NIST SP 800-63B-4, section 3.1.1.2](https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver)

Open **Create an account** with an unused username. Enter a passphrase between 64 and 128 characters in both password fields. Submit it and read the server’s length error. Uncomment the limit under **Fix 4**, restart, and repeat with the same username and passphrase. Registration now succeeds. Sign in and open **Account** to confirm the new account works. The other Django password validators and password hashing run in both cases. [Registration form](notes/forms.py)

### 5. The account history omits sign-outs

Sign in with a fresh account, sign out, then sign in again and open **Activity**. There are two sign-ins with no record of the session ending between them. Someone reviewing this history cannot establish that the user explicitly signed out. Django still ends the actual session. [Event handlers](notes/signals.py) · [OWASP A09](https://top10.owasp.org/2021/A09_2021-Security_Logging_and_Monitoring_Failures/)

Uncomment both lines under **Fix 5** and remove the `pass` beneath them. Restart, sign out and sign in again, then open **Activity**. The latest sign-out now appears between the two most recent sign-ins. The fix records new events. The timestamps of earlier missing events cannot be reconstructed.

## Run the tests

On Windows run `.\.venv\Scripts\python.exe manage.py test`. On Linux or macOS run `.venv/bin/python manage.py test`. The eight tests use a temporary database. The browser screenshots use fictional accounts and two local installations, one with the original code and one with the five commented fixes enabled. [Backend tests](notes/tests.py)
