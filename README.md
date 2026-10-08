# Qantara Data Engineering
## Intro
### 0.Overview
This repo is for my coding environment and versioning for a company called qantara.
### 1.Goal
The end goal is having dashboards that show consistent numbers, kpis and charts, utilizing pipelines and automation to minimize human-errors.
### 2.Roadmap
I'm currently being onboarded, I'm starting out with making a branch for every new feature and making a pr into main where it gets reviewed, then i'll work on more features till I reach the end goal, examples include: 
- source extraction
- loading
- integration
- transformation
- warehousing
- dashboards with correct numbers
- improving: idempotency, data quality checks, testing etc...

## Getting started
### 0.tools
Installed on your laptop: Git, Python 3.11, `uv`, Docker Desktop, GNU make, GitHub CLI (`gh`).
Install yourself, whichever you prefer:
- A SQL client: SSMS 21, VS Code with the *SQL Server (mssql)* extension, or DBeaver Community.
- **Microsoft ODBC Driver 18 for SQL Server** if you'll connect from Python (`pyodbc`, SQLAlchemy).
### 1.prepare
have docker desktop open, in CLI run: make -C upstream up