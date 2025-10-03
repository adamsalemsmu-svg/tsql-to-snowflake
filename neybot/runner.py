# neybot/runner.py
from neybot.converter import tsql_to_snowflake

def run_inline(sql: str):
    result = tsql_to_snowflake(sql)
    print(result)
    return result
