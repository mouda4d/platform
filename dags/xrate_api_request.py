from datetime import date, timedelta
import os
import sys
import pyodbc
import requests

# 1. Fetch Credentials & Environment
xrate_api_key = os.getenv("xrate_api_key")
API_URL = os.getenv("API_URL")

server = os.getenv("DB_SERVER", "qantara-core-db-1,1433")
database = os.getenv("DB_NAME", "DE_SANDBOX")
username = os.getenv("DB_USER", "sa")
password = os.getenv("DB_PASSWORD")
driver = "{ODBC Driver 18 for SQL Server}"

# 2. Fetch API Data
yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
url = f"{API_URL}/{yesterday}"
headers = {"X-API-KEY": xrate_api_key}

try:
  response = requests.get(url, headers=headers, timeout=30)
  response.raise_for_status()
  payload = response.json()
except (requests.RequestException, ValueError) as e:
  print(f"[ERROR] API Request failed: {e}")
  sys.exit(1)

# 3. SQL Connection
connection_string = (
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate=yes;"
)

# DDL Queries (Idempotent)
CREATE_SCHEMA_QUERY = """
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'fin')
BEGIN
    EXEC('CREATE SCHEMA fin');
END
"""

CREATE_TABLE_QUERY = """
IF OBJECT_ID('fin.xrates', 'U') IS NULL
BEGIN
    CREATE TABLE fin.xrates (
        rate_date DATE NOT NULL,
        currency VARCHAR(3) NOT NULL,
        bid DECIMAL(18, 4) NOT NULL,
        ask DECIMAL(18, 4),
        mid DECIMAL(18, 4),
        revision INT NOT NULL DEFAULT 1,
        published_at DATETIMEOFFSET NULL,
        CONSTRAINT PK_xrates PRIMARY KEY (rate_date, currency)
    );
END
"""

MERGE_QUERY = """
MERGE INTO fin.xrates AS target
USING (SELECT ? AS rate_date, ? AS currency, ? AS bid, ? AS ask, ? AS mid, ? AS revision, ? AS published_at) AS source
ON target.rate_date = source.rate_date AND target.currency = source.currency
WHEN MATCHED THEN
    UPDATE SET bid = source.bid, ask=source.ask, mid=source.mid, revision=source.revision, published_at=source.published_at
WHEN NOT MATCHED THEN
    INSERT (rate_date, currency, bid, ask, mid, revision, published_at)
    VALUES (source.rate_date, source.currency, source.bid, source.ask, source.mid, source.revision, source.published_at);
"""

cnxn = None
cursor = None

try:
  cnxn = pyodbc.connect(connection_string)
  cursor = cnxn.cursor()

  # Automate DDL (Ensures schema & table exist dynamically in DB_NAME)
  cursor.execute(CREATE_SCHEMA_QUERY)
  cursor.execute(CREATE_TABLE_QUERY)
  cnxn.commit()

  # Insert/Merge Data
  rate_date = payload["date"]
  for rate in payload["rates"]:
    cursor.execute(
        MERGE_QUERY,
        rate_date,
        rate["currency"],
        rate["bid"],
        rate["ask"],
        rate["mid"],
        rate["revision"],
        rate["published_at"],
    )

  cnxn.commit()
  print(
      f"[SUCCESS] Ingested {len(payload['rates'])} records into"
      f" {database}.fin.xrates for {rate_date}."
  )

except (KeyError, pyodbc.Error) as e:
  print(f"[ERROR] Ingestion failed: {e}")
  sys.exit(1)
finally:
  if cursor:
    cursor.close()
  if cnxn:
    cnxn.close()