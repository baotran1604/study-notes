# Study Notes

Study Notes is a small Django and SQLite notebook. Create an account, sign in, write a note, and find it later by searching its title. Each account has its own notebook and sign-in history.

The sign-out history demonstrates a logging flaw (A09). Its fix is commented out in the backend. The other four categories have active protections and after-state screenshots. Their vulnerable versions and before-state screenshots are missing from this project.

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

## Five backend checks

The category numbers refer to the [OWASP Top 10 for 2021](https://owasp.org/Top10/2021/). All screenshots use fictional accounts and sample notes. Checks 1–4 used port 8674. The two logging screenshots used separate local databases and the same sequence of actions.

| # | Category | What the backend does and how to check it | Browser evidence |
|---|---|---|---|
| 1 | A01 Broken Access Control | The detail view looks up a note by both its ID and its owner. The list also filters by owner. The test opens the same saved note with two users and checks for a 200 for the owner and a 404 for the other user. See [note views](notes/views.py). | [Owner opens the note](screenshots/flaw-1-after-1.png) · [Second account opens the same URL](screenshots/flaw-1-after-2.png) |
| 2 | A02 Cryptographic Failures | Registration uses Django’s password hashing. The Account page reads the algorithm from the current user’s stored password record. The test registers two accounts with the same password, checks that their encoded values differ, and verifies the password still works. See [registration and account views](notes/views.py). | [Stored password algorithm](screenshots/flaw-2-after-1.png) |
| 3 | A03 Injection | The title search passes the search term to a Django ORM filter as a bound value. The test checks that an apostrophe and a percent sign match the intended title and that a private title from another account stays out of the results. See [notebook search](notes/views.py). | [Literal title search](screenshots/flaw-3-after-1.png) |
| 4 | A07 Identification and Authentication Failures | The registration form runs Django’s password validators before creating an account. The tests check that a common password yields a form error and creates no user, and that a valid registration can sign in and out. See [validators](config/settings.py) and [registration](notes/views.py). | [Registration rejected](screenshots/flaw-4-after-1.png) |
| 5 | A09 Security Logging and Monitoring Failures | A sign-out ends the session but leaves no entry in the account history. The commented fix records the user, event type, and time. See [sign-out handler](notes/signals.py). | [Missing sign-out](screenshots/flaw-5-before-1.png) · [Sign-out recorded](screenshots/flaw-5-after-1.png) |

## Try the sign-out logging fix

1. Sign in with a fresh account, sign out, then sign in again. Open **Activity**. There are two sign-ins. Someone reviewing the history cannot tell when the first session ended.
2. Open `notes/signals.py` and find `record_sign_out`. Uncomment the two lines under **Fix 5** and remove the `pass` below them. Restart the server if auto-reload is off.
3. Sign out and sign in again. Open **Activity**. The latest sign-out now appears between the two most recent sign-ins. The fix records new events. Earlier missing times cannot be recovered.

The two screenshots each start with a fresh account and show the same sign-in, sign-out, sign-in sequence. Django handles session termination in both runs. The difference is the event saved in SQLite.

## Run the tests

On Windows run `.\.venv\Scripts\python.exe manage.py test`. On Linux or macOS run `.venv/bin/python manage.py test`. The [five regression tests](notes/tests.py) use a temporary test database.
