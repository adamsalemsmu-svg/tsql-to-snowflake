import pandas as pd
import psycopg2
import matplotlib.pyplot as plt

# --- DB connection ---
conn = psycopg2.connect(
    dbname="realestate",
    user="postgres",
    password="YOUR_POSTGRES_PASSWORD",  # replace with your real password
    host="localhost",
    port="5432"
)

# Helper function: run SQL -> DataFrame
def q(sql):
    return pd.read_sql_query(sql, conn)

# ---
