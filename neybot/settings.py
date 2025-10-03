# neybot/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

SNOWFLAKE_CONFIG = {
    "user": os.getenv("SF_USER"),
    "password": os.getenv("SF_PASSWORD"),
    "account": os.getenv("SF_ACCOUNT"),
    "warehouse": os.getenv("SF_WAREHOUSE", "COMPUTE_WH"),
    "database": os.getenv("SF_DATABASE", "MY_DB"),
    "schema": os.getenv("SF_SCHEMA", "PUBLIC"),
    "role": os.getenv("SF_ROLE", "ACCOUNTADMIN"),
}
