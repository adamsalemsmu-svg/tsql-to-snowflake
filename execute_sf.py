# execute_sf.py
import os
import snowflake.connector

# Fill these from env vars or hard-code while testing
cfg = dict(
    user=os.getenv("SF_USER", "YOUR_USER"),
    password=os.getenv("SF_PASSWORD", "YOUR_PASSWORD"),
    account=os.getenv("SF_ACCOUNT", "YOUR_ACCOUNT"),   # e.g. xy12345.us-east-1
    warehouse=os.getenv("SF_WAREHOUSE", "COMPUTE_WH"),
    database=os.getenv("SF_DATABASE", "MY_DB"),
    schema=os.getenv("SF_SCHEMA", "PUBLIC"),
    role=os.getenv("SF_ROLE", "ACCOUNTADMIN"),
)

def run_sql(sql: str):
    conn = snowflake.connector.connect(**cfg)
    try:
        cs = conn.cursor()
        for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
            cs.execute(stmt)
        print("Executed OK")
    finally:
        cs.close(); conn.close()

if __name__ == "__main__":
    import sys
    if not sys.stdin.isatty():
        run_sql(sys.stdin.read())
    else:
        print("Pipe SQL into me, e.g.: type ready_for_snowflake.sql | python execute_sf.py")
