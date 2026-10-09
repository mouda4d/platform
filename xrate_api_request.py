import requests
from dotenv import load_dotenv
import os
from datetime import date, timedelta
import pyodbc

load_dotenv()
xrate_api_key = os.getenv("XRATE_API_KEY")
yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
url = f"http://localhost:8701/v1/rates/{yesterday}"
headers = {
    "X-API-KEY": xrate_api_key
}
try:
    response = requests.get(url, headers=headers)
    print(response.status_code)
    print(response.json())
except requests.RequestException as e:
    print(f"Error occurred while making the request: {e}")

server = os.getenv("DB_SERVER", "localhost,1433")
database = os.getenv("DB_NAME", "DE_SANDBOX")
username = os.getenv("DB_USER", "sa")
password = os.getenv("DB_PASSWORD")
driver = "{ODBC Driver 18 for SQL Server}"

# Construct DSN-less connection string using an f-string
connection_string = (
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate=yes;"  # Required for ODBC Driver 18 on local/Docker instances
)

cnxn = pyodbc.connect(connection_string)
cursor = cnxn.cursor()

merge_query = """
MERGE INTO fin.xrates AS target
USING (SELECT ? AS rate_date, ? AS currency, ? AS bid, ? AS ask, ? AS mid, ? AS revision, ? AS published_at) AS source
ON target.rate_date = source.rate_date AND target.currency = source.currency
WHEN MATCHED THEN
    UPDATE SET bid = source.bid, ask=source.ask, mid=source.mid, revision=source.revision, published_at=source.published_at
WHEN NOT MATCHED THEN
    INSERT (rate_date, currency, bid, ask, mid, revision, published_at)
    VALUES (source.rate_date, source.currency, source.bid, source.ask, source.mid, source.revision, source.published_at);
"""
try:
    rate_date = response.json()["date"]
    for rate in response.json()["rates"]:
        cursor.execute(merge_query, rate_date, rate["currency"], rate["bid"], rate["ask"], rate["mid"], rate["revision"], rate["published_at"])

    cnxn.commit()
    cursor.close()
    cnxn.close()

except KeyError as e:
    print(f"Error occurred while extracting rate data from the response: {e}")
    cursor.close()
    cnxn.close()
except pyodbc.Error as e:
    print(f"Database error occurred: {e}")
    cursor.close()
    cnxn.close()