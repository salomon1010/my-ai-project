# Day 1 Learning Guide — AI Executive Reporting System

## What this document is

A complete explanation of every decision, every file, and every line of code built on Day 1. Read this to understand not just WHAT was built, but WHY — so you can explain it to a client, debug it yourself, and extend it later.

---

## The Big Picture First

Before touching any code, you need to understand what you're building and why it's structured this way.

### What the system does

```
Your messy CSV file
        ↓
    Python reads it
        ↓
    Saves it to DuckDB (a database that lives in a single file)
        ↓
    Later: cleans it, calculates KPIs, sends to AI, generates report
```

Day 1 only builds the first two arrows: **read the CSV → save to database**. Everything else (cleaning, AI, reports) comes in later days. This is intentional — you build one solid layer at a time.

### Why a database instead of just keeping data in Python memory?

Great question. You could just read the CSV and keep it in a Python variable. But:

| Memory (Python variable) | Database (DuckDB) |
|---|---|
| Gone when script stops | Persists on disk |
| Hard to query with SQL | Full SQL support |
| One script can't share with another | Streamlit app, reset script, and tests can all read the same data |
| No history of what came in | You can inspect it anytime |

Think of the database as a shared filing cabinet. Every part of your system — the pipeline, the UI, the tests — goes to the same cabinet to get data.

### Why DuckDB specifically?

DuckDB is what's called an "embedded database." It's just a single `.duckdb` file on your computer — no server to install, no network connection needed. It's like SQLite but built for analytics (fast SQL, good Pandas support).

For a demo on a laptop, this is perfect. A client doesn't need to set up anything. One file, everything works.

---

## The Files You Created

Here is every file and why it exists:

```
my-ai-project/
├── requirements.txt          ← "Shopping list" of Python packages
├── .env.example              ← Template showing what secrets are needed
├── .gitignore                ← What NOT to commit to git (secrets, temp files)
├── data/
│   ├── input/
│   │   └── project_data.csv  ← The demo dataset (15 fake projects)
│   └── db/                   ← DuckDB database file lives here
├── src/
│   ├── __init__.py           ← Tells Python "this folder is a package"
│   ├── storage/
│   │   ├── __init__.py
│   │   └── db.py             ← The ONE place DuckDB connection is made
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── csv_loader.py     ← Reads CSV → writes to bronze table
│   ├── transforms/           ← Empty today, used Day 2+
│   ├── llm/                  ← Empty today, used Day 4+
│   └── reporting/            ← Empty today, used Day 6+
├── app/                      ← Empty today, Streamlit UI lives here Day 5+
├── demo/
│   ├── __init__.py
│   └── sample_data.py        ← The 15 fake projects as Python data
└── tests/
    ├── __init__.py
    └── test_ingestion.py     ← Automated tests for csv_loader.py
```

---

## File 1: `requirements.txt`

### What it is

A plain text file that lists every Python package your project needs. Think of it as a shopping list for your Python environment.

### The file

```
duckdb==0.10.3
pandas==2.2.2
anthropic==0.28.0
streamlit==1.35.0
reportlab==4.2.2
python-dotenv==1.0.1
loguru==0.7.2
pytest==8.2.2
pytest-mock==3.14.0
```

### What each package does

| Package | What it does | Used when |
|---|---|---|
| `duckdb` | The database engine (runs SQL on local files) | Day 1+ |
| `pandas` | Reads CSV files, manipulates data in Python | Day 1+ |
| `anthropic` | Official SDK to call Claude AI | Day 4 |
| `streamlit` | Builds the web UI in pure Python | Day 5 |
| `reportlab` | Generates PDF files | Day 6 |
| `python-dotenv` | Reads your `.env` file for secrets | Day 1+ |
| `loguru` | Better logging (replaces Python's `print` for status messages) | Day 1+ |
| `pytest` | Runs your automated tests | Day 1+ |
| `pytest-mock` | Lets tests fake (mock) the Claude AI call so tests don't cost money | Day 4+ |

### Why pin exact versions (`==0.10.3` not just `duckdb`)?

If you just write `duckdb`, pip installs the latest version. In 6 months that version might have breaking changes and your code breaks. Pinning `==0.10.3` guarantees the same version every time anyone installs it — on your laptop, a client's machine, or in the future.

### How to install

```bash
pip install -r requirements.txt
```

This reads the file and installs all packages at once.

---

## File 2: `.env.example`

### What it is

A template showing what environment variables (secrets and settings) your app needs. The actual secrets go in `.env` — this file just shows the structure.

### The file

```
ANTHROPIC_API_KEY=your_key_here
MODEL_ID=claude-haiku-4-5
DB_PATH=data/db/reporting.duckdb
REPORTS_OUTPUT_DIR=outputs/reports
COMPANY_NAME=Acme Corporation
```

### What each variable does

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Your secret key to call Claude AI (never share this) |
| `MODEL_ID` | Which Claude model to use (claude-haiku-4-5 is fast and cheap) |
| `DB_PATH` | Where the DuckDB file lives on disk |
| `REPORTS_OUTPUT_DIR` | Where PDF reports get saved |
| `COMPANY_NAME` | Appears on the PDF cover page (change per client) |

### Why `.env.example` and not just `.env`?

- `.env` contains your **real** API key — it must NEVER be committed to git
- `.env.example` has fake placeholder values — it IS committed to git so other developers (or future you on a new computer) know what to fill in

### The workflow

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your real API key
# (use any text editor — VS Code, nano, etc.)
```

Then `.gitignore` makes sure `.env` is never accidentally committed.

---

## File 3: `.gitignore`

### What it is

Tells git which files to ignore — never track, never commit, never push.

### The file

```
.env
data/db/
outputs/
__pycache__/
.pytest_cache/
*.pyc
*.pyo
.DS_Store
```

### Why each entry

| Entry | Why ignored |
|---|---|
| `.env` | Contains real API keys — if this hits GitHub, someone steals your key |
| `data/db/` | The DuckDB file is generated — not source code, pointless to commit |
| `outputs/` | Generated PDF reports — not source code |
| `__pycache__/` | Python's compiled bytecode — auto-generated, clutters repo |
| `.pytest_cache/` | Test run cache — auto-generated |
| `*.pyc`, `*.pyo` | Compiled Python files — auto-generated |
| `.DS_Store` | macOS folder metadata — irrelevant to other developers |

**The rule:** Commit source code and configuration templates. Never commit secrets, generated files, or OS noise.

---

## File 4: `data/input/project_data.csv`

### What it is

The fake dataset that powers all your demos. 15 projects across 3 departments, designed to have enough variety to make the AI report interesting.

### How it was generated

You created `demo/sample_data.py` with the data as a Python list, then ran:

```bash
python demo/sample_data.py
```

That script wrote the Python list to a CSV file. This way, the source of truth for the data is `sample_data.py` (Python code you can control), and the CSV is generated from it — never edited by hand.

### The columns explained

```
project_name       - What the project is called
department         - Which business unit owns it (IT, Finance, Operations)
planned_cost       - Original budget ($)
actual_cost        - What was actually spent ($)
planned_finish_date - Original target completion date
actual_finish_date  - Actual/forecast completion date
status             - on_track | at_risk | delayed | completed
risk_level         - low | medium | high | critical
issue_description  - Free text notes about problems
owner              - Project manager name
```

### Why 15 projects with this specific mix?

The AI report is only interesting if there's something to report. Your 15 projects were chosen to have:
- **7 over budget** (over 10% threshold) — gives the AI budget concerns to write about
- **8 late** — gives the AI schedule delays to report
- **1 critical risk** (Mobile App Launch) — gives the AI a dramatic story to tell
- **3 completed** — so it's not all doom and gloom
- **3 departments** — gives "issues by department" analysis something to aggregate

If all 15 projects were "on track, on budget," the AI would have nothing to say. Realistic messy data makes the demo compelling.

---

## File 5: `src/storage/db.py` — The Connection Factory

### What it is

The single place in your entire codebase where DuckDB is opened. Every other file calls `get_connection()` instead of opening DuckDB directly.

### The file

```python
import os
import duckdb
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> duckdb.DuckDBPyConnection:
    db_path = os.getenv("DB_PATH", "data/db/reporting.duckdb")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(db_path)
```

### Line by line explanation

**`import os`**
Python's built-in module for reading environment variables and file paths. You use it to read `DB_PATH` from `.env`.

**`import duckdb`**
The DuckDB library. This is what gives you the ability to run SQL against a local file.

**`from pathlib import Path`**
Python's modern way to work with file paths. `Path("data/db/").mkdir(parents=True, exist_ok=True)` creates the directory if it doesn't exist, without crashing if it already does.

**`from dotenv import load_dotenv`**
Reads your `.env` file and loads its contents into environment variables. After this runs, `os.getenv("ANTHROPIC_API_KEY")` will return the value you put in `.env`.

**`load_dotenv()`**
This call at module level means: the moment this file is imported anywhere, your `.env` is loaded. You don't have to remember to call it from other files.

**`def get_connection() -> duckdb.DuckDBPyConnection:`**
A function that returns a DuckDB connection. The `-> duckdb.DuckDBPyConnection` is a type hint — it tells Python (and your editor) what type of object this function returns. Not required, but good practice.

**`db_path = os.getenv("DB_PATH", "data/db/reporting.duckdb")`**
Read the `DB_PATH` environment variable. If it's not set, use `"data/db/reporting.duckdb"` as the default. This is the default value pattern — good because tests can override `DB_PATH` to use a temporary directory.

**`Path(db_path).parent.mkdir(parents=True, exist_ok=True)`**

Let's break this down:
- `Path(db_path)` — converts the string path to a Path object
- `.parent` — gets the directory containing the file (`data/db/` from `data/db/reporting.duckdb`)
- `.mkdir(parents=True, exist_ok=True)` — creates that directory
  - `parents=True` means "create intermediate directories too" (like `mkdir -p`)
  - `exist_ok=True` means "don't crash if it already exists"

Without this line, DuckDB would crash if `data/db/` didn't exist yet.

**`return duckdb.connect(db_path)`**
Opens (or creates) the DuckDB file and returns a connection object. If the file doesn't exist, DuckDB creates it.

### Why this matters architecturally

This is called the **Single Responsibility Principle**. Only one file knows where the database is. If you later want to:
- Change the file path
- Switch to Postgres
- Use an in-memory database for speed
- Use a different database per environment

...you change **only this file**. None of your transform files, aggregation files, or UI code need to change. This is what makes the code maintainable.

**The wrong way** (what NOT to do):
```python
# In csv_loader.py — WRONG
con = duckdb.connect("data/db/reporting.duckdb")  # hardcoded path!

# In bronze_to_silver.py — WRONG
con = duckdb.connect("data/db/reporting.duckdb")  # same hardcoded path again!
```

If you ever need to change the path, you'd have to find and update every file. With `db.py`, you change one line, everything works.

---

## File 6: `demo/sample_data.py` — The Dataset

### What it is

The 15 fake projects stored as a Python list of dictionaries. It also includes a function to write that data to a CSV file.

### Why store data as Python, not just a CSV?

Two reasons:

1. **The reset script needs to regenerate the CSV from scratch.** If you only have a CSV and someone edits it by hand, your demo is broken. With Python as the source of truth, you can always regenerate a clean CSV.

2. **Tests can import the data directly.** Your test file imports `SAMPLE_PROJECTS` to build test CSV files — no file path needed.

### The key parts

```python
SAMPLE_PROJECTS = [
    {
        "project_name": "Cloud Migration Phase 1",
        "department": "IT",
        "planned_cost": 250000,
        "actual_cost": 310000,
        ...
    },
    ...  # 14 more projects
]
```

This is a **list of dictionaries**. Each dictionary represents one project row. The keys match the CSV column headers exactly.

```python
def write_sample_csv(path: str = "data/input/project_data.csv") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SAMPLE_PROJECTS[0].keys())
        writer.writeheader()
        writer.writerows(SAMPLE_PROJECTS)
```

- `csv.DictWriter` — Python's built-in CSV writer that takes dictionaries
- `fieldnames=SAMPLE_PROJECTS[0].keys()` — gets the column names from the first project's keys
- `writer.writeheader()` — writes the header row (column names)
- `writer.writerows(SAMPLE_PROJECTS)` — writes all 15 project rows

```python
if __name__ == "__main__":
    write_sample_csv()
    print("Sample CSV written to data/input/project_data.csv")
```

`if __name__ == "__main__":` means: this code only runs if you execute this file directly (`python demo/sample_data.py`). If another file imports `sample_data`, this block is skipped. It's the standard Python pattern for making a file both importable and runnable.

---

## File 7: `src/ingestion/csv_loader.py` — The Bronze Ingestion

### What it is

Reads a CSV file and writes it verbatim into a DuckDB table called `bronze_project_raw`. This is the "bronze layer" in medallion architecture.

### What is medallion architecture?

It's a data engineering pattern with three layers:

```
Bronze — Raw data, copied exactly as received (no changes)
Silver — Cleaned and normalized (dates parsed, nulls handled, status normalized)
Gold   — Business-ready KPIs (budget_variance, is_late, etc.)
```

Why three layers instead of one? Because:
- **Bronze** gives you a recovery point. If your cleaning logic has a bug, you can re-clean from bronze without re-ingesting.
- **Silver** gives downstream users clean data without knowing the cleaning rules.
- **Gold** gives business users pre-computed metrics without knowing the calculation formulas.

Companies like Databricks, Snowflake, and Delta Lake are built around this pattern. By naming your DuckDB tables `bronze_project_raw`, `silver_project_clean`, and `gold_project_kpi`, you're demonstrating the exact same concept — which is exactly what impresses enterprise clients.

### The file

```python
import pandas as pd
from loguru import logger
from src.storage.db import get_connection


def load_csv_to_bronze(file_path: str) -> tuple[int, int]:
    df = pd.read_csv(file_path, dtype=str)

    required = {"project_name", "planned_cost"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise ValueError(f"CSV is missing required columns: {missing}")

    initial_count = len(df)
    df = df[df["project_name"].notna() & (df["project_name"].str.strip() != "")]
    skipped = initial_count - len(df)

    con = get_connection()
    con.execute("CREATE OR REPLACE TABLE bronze_project_raw AS SELECT * FROM df")
    con.close()

    loaded = len(df)
    logger.info(f"Loaded {loaded} rows into bronze_project_raw ({skipped} skipped)")
    return loaded, skipped
```

### Line by line

**`import pandas as pd`**
Pandas is the standard Python library for working with tabular data (like spreadsheets). `as pd` is just a common abbreviation everyone uses.

**`from loguru import logger`**
Loguru's logger is better than `print()` because it adds timestamps, log levels (INFO, WARNING, ERROR), and can be directed to files. Using it from Day 1 means your logs look professional when a client is watching.

**`from src.storage.db import get_connection`**
This imports the connection function from `db.py`. Notice: NOT `import duckdb`. This respects the single-connection-point pattern.

**`def load_csv_to_bronze(file_path: str) -> tuple[int, int]:`**
The function takes a file path string and returns a tuple of two integers: `(rows_loaded, rows_skipped)`. This return value lets the pipeline know what happened without reading log output.

**`df = pd.read_csv(file_path, dtype=str)`**
Read the CSV into a pandas DataFrame. `dtype=str` is critical: it reads EVERY column as a string, no matter what the values look like.

Why? Because in the bronze layer, you want raw data as-is. If pandas tries to be clever and auto-detect types, it might:
- Parse `"250000"` as integer 250000
- Parse `"2024-03-31"` as a datetime object using its own assumptions
- Interpret `"N/A"` as `NaN`

All of these "helpful" conversions happen before you've validated the data. Bronze = raw = strings only.

**`required = {"project_name", "planned_cost"}`**
A Python set of column names that MUST exist. Using a set (with `{}`) instead of a list (with `[]`) makes the `issubset` check efficient.

**`if not required.issubset(df.columns):`**
`df.columns` is the list of column names in the CSV. `.issubset()` checks if all required columns exist in that list. If any are missing, raise an error immediately.

**`raise ValueError(f"CSV is missing required columns: {missing}")`**
`ValueError` is the right exception type for "invalid input" — the data doesn't meet requirements. The f-string shows exactly which columns are missing. This is called a **boundary check** — validate input at the entry point so errors are caught early with clear messages.

**`initial_count = len(df)`**
Save the total row count BEFORE filtering. You need this to calculate how many rows were skipped.

**`df = df[df["project_name"].notna() & (df["project_name"].str.strip() != "")]`**

This is a pandas filter. Let's unpack it:
- `df["project_name"]` — the project_name column
- `.notna()` — True for rows where project_name is not NaN (not empty/null)
- `df["project_name"].str.strip() != ""` — True for rows where project_name is not just whitespace
- `&` — both conditions must be True
- `df[...]` — keep only the rows where the condition is True

Real client data often has blank rows at the bottom of a spreadsheet. This filter drops them silently.

**`skipped = initial_count - len(df)`**
How many rows were dropped. The caller can log or display this.

**`con = get_connection()`**
Opens the DuckDB connection via the factory function.

**`con.execute("CREATE OR REPLACE TABLE bronze_project_raw AS SELECT * FROM df")`**

This is DuckDB magic. `df` is a pandas DataFrame — and DuckDB can reference it directly by name in a SQL statement. So this one line:
1. Creates a new DuckDB table called `bronze_project_raw`
2. Selects all columns and rows from the pandas DataFrame
3. `CREATE OR REPLACE` means: if the table already exists, drop it and recreate (safe for re-runs)

No manual column definitions needed. No INSERT loops. DuckDB infers everything from the DataFrame.

**`con.close()`**
Always close the connection when done. DuckDB is a file-based database — leaving connections open can cause issues if another process tries to access the same file.

**`logger.info(f"Loaded {loaded} rows into bronze_project_raw ({skipped} skipped)")`**
This log line appears in the terminal when the pipeline runs. During a client demo, seeing this message fly past reassures people that things are happening.

**`return loaded, skipped`**
Returns a tuple. In Python, `return 15, 0` is the same as `return (15, 0)`. The caller can unpack it: `loaded, skipped = load_csv_to_bronze(path)`.

---

## File 8: `tests/test_ingestion.py` — Automated Tests

### What tests are and why they matter

A test is code that checks whether your other code works correctly. You run tests after making changes to make sure you didn't break anything.

**Without tests:** You manually click through the app after every change hoping nothing broke.
**With tests:** You run `pytest` and it tells you in 2 seconds if anything broke.

For consulting work, tests are proof that your system is reliable. Clients with IT departments will ask: "Do you have tests?" — and you can say yes.

### The file structure

```python
import pytest
import csv


@pytest.fixture
def sample_csv(tmp_path):
    ...

@pytest.fixture(autouse=True)
def set_test_db(tmp_path, monkeypatch):
    ...

def test_load_happy_path(sample_csv):
    ...

def test_missing_required_column(tmp_path):
    ...

def test_empty_project_name_rows_skipped(tmp_path):
    ...
```

### Understanding pytest fixtures

A **fixture** is a reusable piece of test setup. Instead of repeating setup code in every test, you define it once as a fixture and pytest injects it automatically.

**`tmp_path`** — a built-in pytest fixture that gives you a temporary directory unique to each test. Files created here are automatically deleted after the test. This means your tests never interfere with each other or with your real data.

**`@pytest.fixture`** — the decorator that tells pytest "this function is a fixture."

### The `set_test_db` fixture

```python
@pytest.fixture(autouse=True)
def set_test_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.duckdb"))
```

`autouse=True` means this fixture runs automatically for EVERY test in the file — you don't have to request it.

What it does: overrides the `DB_PATH` environment variable to point to a fresh temporary DuckDB file inside `tmp_path`. This means:
- Each test gets a completely fresh, empty database
- Tests never write to your real `data/db/reporting.duckdb`
- After the test, the temporary file is cleaned up

`monkeypatch.setenv` is pytest's way of temporarily setting an environment variable for the duration of a test. After the test ends, the variable is restored to its original value.

### The `sample_csv` fixture

```python
@pytest.fixture
def sample_csv(tmp_path):
    from demo.sample_data import SAMPLE_PROJECTS
    csv_path = tmp_path / "test_projects.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SAMPLE_PROJECTS[0].keys())
        writer.writeheader()
        writer.writerows(SAMPLE_PROJECTS)
    return str(csv_path)
```

This creates a temporary CSV file from `SAMPLE_PROJECTS` and returns its path. Any test that needs a ready-made CSV just declares `sample_csv` as a parameter and gets the path handed to it.

Notice: the import is inside the function (`from demo.sample_data import SAMPLE_PROJECTS`). This is intentional — it imports fresh on each test run, avoiding any module-level caching issues.

### Test 1: The Happy Path

```python
def test_load_happy_path(sample_csv):
    from src.ingestion.csv_loader import load_csv_to_bronze
    from src.storage.db import get_connection

    loaded, skipped = load_csv_to_bronze(sample_csv)
    assert loaded == 15
    assert skipped == 0

    con = get_connection()
    count = con.execute("SELECT COUNT(*) FROM bronze_project_raw").fetchone()[0]
    con.close()
    assert count == 15
```

**What it tests:** When you load a valid 15-row CSV, exactly 15 rows end up in the database.

**Why two assertions?** First, you check the return value of `load_csv_to_bronze`. Then you open the database and run a SQL query to verify the data actually made it there. The function could return `15` while secretly writing 0 rows — the SQL check catches that.

**`fetchone()[0]`** — `fetchone()` returns a tuple like `(15,)`. `[0]` gets the first (and only) element: the count.

### Test 2: Missing Required Column

```python
def test_missing_required_column(tmp_path):
    from src.ingestion.csv_loader import load_csv_to_bronze

    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("project_name,department\nProject A,IT\n")
    with pytest.raises(ValueError, match="missing required columns"):
        load_csv_to_bronze(str(bad_csv))
```

**What it tests:** A CSV without `planned_cost` raises a clear error.

`pytest.raises(ValueError, match="missing required columns")` is a context manager that:
- Expects the code inside to raise `ValueError`
- Checks that the error message contains "missing required columns"
- If no exception is raised, the test FAILS
- If a different exception is raised, the test FAILS

This tests your boundary check — "bad input produces a clear error, not a confusing crash."

### Test 3: Empty Project Names Skipped

```python
def test_empty_project_name_rows_skipped(tmp_path):
    from src.ingestion.csv_loader import load_csv_to_bronze

    rows = "project_name,planned_cost,...\n"
    rows += ",50000,...\n"          # empty project_name
    rows += ",60000,...\n"          # empty project_name
    rows += "Real Project,70000,...\n"  # valid row

    csv_path = tmp_path / "empty_names.csv"
    csv_path.write_text(rows)
    loaded, skipped = load_csv_to_bronze(str(csv_path))
    assert loaded == 1
    assert skipped == 2
```

**What it tests:** Rows with blank `project_name` are silently dropped and counted as skipped.

This simulates real-world client data where someone exported a spreadsheet with blank trailing rows. Your system handles it gracefully.

---

## How It All Connects

Here is the full execution flow when the ingestion layer runs:

```
1. Someone calls: load_csv_to_bronze("data/input/project_data.csv")

2. csv_loader.py reads the CSV with pandas
   → All 15 rows, all columns as strings
   → DataFrame has shape (15, 10)

3. Validates required columns exist
   → "project_name" ✓  "planned_cost" ✓

4. Filters out blank project names
   → All 15 are valid, none dropped
   → skipped = 0

5. Calls get_connection() from db.py
   → db.py reads DB_PATH from .env
   → Creates data/db/ directory if needed
   → Opens (or creates) data/db/reporting.duckdb
   → Returns a DuckDB connection

6. Executes SQL:
   CREATE OR REPLACE TABLE bronze_project_raw AS SELECT * FROM df
   → DuckDB reads the pandas DataFrame
   → Creates a table with 15 rows, 10 columns, all strings

7. Closes the connection
   → File is written to disk

8. Logs: "Loaded 15 rows into bronze_project_raw (0 skipped)"

9. Returns (15, 0)
```

After this runs, you can open `data/db/reporting.duckdb` with any DuckDB client and see your 15 projects in the `bronze_project_raw` table.

---

## How the Tests Work

```
1. pytest starts

2. For each test, set_test_db runs automatically (autouse=True)
   → DB_PATH is set to /tmp/pytest-xxx/test.duckdb (a fresh temp file)
   → This means each test has a clean, empty database

3. For tests that declare sample_csv:
   → sample_csv fixture creates a temp CSV from SAMPLE_PROJECTS
   → Returns the path to that CSV

4. The test function runs
   → Calls load_csv_to_bronze()
   → Makes assertions about the results

5. After the test:
   → monkeypatch restores DB_PATH to original value
   → tmp_path files are cleaned up
   → No side effects remain
```

---

## What You Can Do Right Now

### 1. Inspect the DuckDB table

```bash
python -c "
from src.storage.db import get_connection
from dotenv import load_dotenv
load_dotenv()

con = get_connection()
result = con.execute('SELECT project_name, department, planned_cost, actual_cost FROM bronze_project_raw LIMIT 5').fetchdf()
print(result)
con.close()
"
```

This lets you see the raw data exactly as it sits in the bronze table.

### 2. Check column types

```bash
python -c "
from src.storage.db import get_connection
from dotenv import load_dotenv
load_dotenv()

con = get_connection()
result = con.execute('DESCRIBE bronze_project_raw').fetchdf()
print(result)
con.close()
"
```

You'll see all columns are `VARCHAR` (string) type. This confirms the bronze layer stores everything raw. Day 2 will convert them to proper types.

### 3. Count over-budget projects manually

```bash
python -c "
from src.storage.db import get_connection
from dotenv import load_dotenv
load_dotenv()

con = get_connection()
# Note: CAST needed because costs are stored as strings in bronze
result = con.execute('''
    SELECT project_name, planned_cost, actual_cost
    FROM bronze_project_raw
    WHERE CAST(actual_cost AS DOUBLE) > CAST(planned_cost AS DOUBLE)
''').fetchdf()
print(f'{len(result)} projects are over budget')
print(result)
con.close()
"
```

This gives you a preview of what Day 2's gold layer will calculate automatically.

---

## Key Concepts to Remember

**1. Separation of concerns**
Each file does one thing: `db.py` connects, `csv_loader.py` loads, `sample_data.py` holds the data. This makes bugs easier to find and code easier to change.

**2. Single connection point**
`db.py` is the only file that calls `duckdb.connect()`. Everything else calls `get_connection()`. This makes the database location easy to change.

**3. Bronze = raw**
The bronze layer stores data exactly as received — all strings, no transforms. This is your recovery point if anything goes wrong downstream.

**4. `dtype=str` when reading CSV**
Never let pandas auto-detect types at the ingestion layer. Parse types explicitly in the silver layer where you control the logic.

**5. Fixtures over setup methods**
pytest fixtures (`tmp_path`, `monkeypatch`, your custom ones) are the modern way to set up and tear down test state. `autouse=True` ensures isolation without repeating code.

**6. Test the real thing, not just the function**
`test_load_happy_path` doesn't just check the return value — it also queries the database to verify data was actually written. Test the outcome, not just the call.

---

## Day 1 Completion Checklist

- [x] Folder structure created (`src/`, `app/`, `demo/`, `tests/`, `data/`)
- [x] Python packages installed (`pip install -r requirements.txt`)
- [x] Environment variable template (`.env.example`) created
- [x] `.env` file created with real API key (you do this manually)
- [x] `.gitignore` protecting secrets and generated files
- [x] `db.py` — single DuckDB connection factory
- [x] `sample_data.py` — 15 projects as Python data
- [x] `project_data.csv` — generated sample dataset
- [x] `csv_loader.py` — CSV → bronze_project_raw
- [x] `test_ingestion.py` — 3 tests, all passing

**`pytest tests/test_ingestion.py -v` → 3 passed**

---

## What Day 2 Will Build On This

Day 1 left `bronze_project_raw` with all strings. Day 2 (`/ai-executive-reporting-day-2`) will:

1. Read `bronze_project_raw`
2. Parse dates from strings to proper DATE type
3. Cast costs from strings to DOUBLE type
4. Normalize status values (`"On Track"` → `"on_track"`)
5. Handle null values gracefully
6. Write `silver_project_clean` — the cleaned version
7. Then compute KPI columns and write `gold_project_kpi`

The cleaning intentionally happens in a separate step so you can inspect `bronze_project_raw` anytime and see exactly what came in — before any transformation touched it.
