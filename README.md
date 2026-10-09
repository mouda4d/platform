# Qantara Data Engineering Platform

A production-ready data ingestion pipeline built on Apache Airflow, Docker, and Microsoft SQL Server. This platform extracts daily exchange rates from upstream APIs, applies automated schema migrations, and merges data into target environments with full idempotency.

---

## 🛠️ Tech Stack & Prerequisites

### Required System Tools
* **Containerization:** Docker Desktop & Docker Compose
* **Automation:** GNU `make`
* **Version Control:** Git & GitHub CLI (`gh`)
* **Python Runtime:** Python 3.11+ (or `uv` package manager)
* **Database Driver:** [Microsoft ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Recommended SQL Clients
* SQL Server Management Studio (SSMS 21+)
* VS Code (with *SQL Server / mssql* extension)
* DBeaver Community Edition

---

## 🏗️ Platform Architecture

```text
               +-------------------------------------------+
               |            Airflow Orchestration          |
               | (Standalone 2.8.1 Container on Port 8080) |
               +---------------------+---------------------+
                                     |
                                     | Triggers BashOperator
                                     v
                        +-------------------------+
                        |  xrate_api_request.py   |
                        +------------+------------+
                                     |
                 +-------------------+-------------------+
                 |                                       |
                 v (HTTP GET)                            v (pyodbc / MERGE)
   +---------------------------+           +---------------------------+
   | Upstream API Container    |           |  SQL Server Container     |
   | (qantara-ratebridge)      |           |  (qantara-core-db-1:1433) |
   +---------------------------+           +---------------------------+
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites Setup
Ensure Docker Desktop is running and verify the shared Docker network exists:
```bash
# Create shared external network if it doesn't exist
docker network create qantara_default

# Start upstream services (if applicable)
make -C upstream up
```

### 2. Environment Selection & Stack Initialization
Initialize the stack for either Development or Production. The build process automatically copies the appropriate `.env` file and provisions the Airflow container:

* **Development (`DE_SANDBOX` database):**
  ```bash
  make dev
  ```
* **Production (`DATA_PROD` database):**
  ```bash
  make prod
  ```

### 3. Access Airflow
* **URL:** [http://localhost:8080](http://localhost:8080)
* **Username:** `admin`
* **Password:** `admin`

---

## 🔄 Ingestion & Auto-Provisioning Mechanics

The core ingestion script (`dags/xrate_api_request.py`) is fully **self-healing** and **idempotent**:

1. **Automated DDL (Schema & Table Creation):** You do **not** need to manually execute DDL scripts on fresh database instances. Upon execution, the script automatically verifies and creates the schema (`fin`) and target table (`fin.xrates`) if they do not exist.
2. **Upsert Logic:** Uses T-SQL `MERGE` statements on `(rate_date, currency)` primary keys. Re-running the pipeline for the same execution date updates existing records without creating duplicates.
3. **Environment Isolation:** Database target selection (`DE_SANDBOX` vs `DATA_PROD`) and API endpoints dynamically adapt based on the active environment initialized via `make dev` or `make prod`.

---

## 📋 Makefile Reference Commands

| Command | Description |
| :--- | :--- |
| `make dev` | Switches config to `.env.dev` and force-recreates the container stack |
| `make prod` | Switches config to `.env.prod` and force-recreates the container stack |

---

## 🛣️ Development Roadmap

- [x] Dockerized Airflow deployment & persistent SQLite metadata store
- [x] Dynamic environment switching (`dev` / `prod`) via `Makefile`
- [x] Automated schema and table DDL initialization
- [x] Idempotent exchange rate API extraction & `MERGE` loading logic
- [ ] Automated data quality checks (Great Expectations / SQL assertions)
- [ ] Data transformation layer & staging tables (dbt / SQL procedures)
- [ ] Dimensional data warehousing model (Star Schema)
- [ ] BI Dashboard integration & metrics validation