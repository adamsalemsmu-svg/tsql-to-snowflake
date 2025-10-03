# converter.py
import sys, re
from pathlib import Path
import sqlglot
from sqlglot.dialects.dialect import Dialect

# --- helpers ---------------------------------------------------------------

def split_batches(sql_text: str) -> list[str]:
    """Split on GO batch separators (MSSQL)."""
    parts = re.split(r"(?im)^\s*GO\s*;?\s*$", sql_text)
    return [p.strip() for p in parts if p.strip()]

def normalize_whitespace(sql: str) -> str:
    sql = re.sub(r"[ \t]+", " ", sql)
    sql = re.sub(r"\n{3,}", "\n\n", sql)
    return sql.strip()

def post_process_snowflake(sql: str) -> str:
    """
    Extra tweaks after sqlglot to match Snowflake conventions.
    Only text replacements that are safe/obvious are applied here.
    """
    # [] identifiers -> "ident"
    sql = re.sub(r"\[([^\]]+)\]", r'"\1"', sql)

    # ISNULL(col, x) -> COALESCE(col, x)
    sql = re.sub(r"(?i)\bISNULL\s*\(", "COALESCE(", sql)

    # IIF(cond, a, b) -> IFF(cond, a, b)
    sql = re.sub(r"(?i)\bIIF\s*\(", "IFF(", sql)

    # GETDATE() -> CURRENT_TIMESTAMP()
    sql = re.sub(r"(?i)\bGETDATE\s*\(\s*\)", "CURRENT_TIMESTAMP()", sql)

    # CONVERT(type, expr [, style]) -> TRY_TO_* or CAST as best-effort
    # Leave to sqlglot first; if leftover patterns remain, simple map:
    sql = re.sub(r"(?i)\bCONVERT\s*\(\s*NVARCHAR\(\d+\)\s*,", "CAST(", sql)

    # NVARCHAR/VARCHAR(MAX) -> VARCHAR
    sql = re.sub(r"(?i)\bN?VARCHAR\s*\(\s*MAX\s*\)", "VARCHAR", sql)

    # TOP n -> LIMIT n (sqlglot handles most cases, but we handle SELECT TOP (n) WITH TIES etc.)
    sql = re.sub(r"(?is)\bSELECT\s+TOP\s*\(\s*(\d+)\s*\)\s*", r"SELECT ", sql)  # drop TOP(); LIMIT added by sqlglot
    sql = re.sub(r"(?is)\bSELECT\s+TOP\s+(\d+)\s*", r"SELECT ", sql)           # drop plain TOP

    # BIT -> BOOLEAN (common in DDL)
    sql = re.sub(r"(?i)\bBIT\b", "BOOLEAN", sql)

    # IDENTITY -> use AUTOINCREMENT-like (Snowflake uses SEQUENCES; here we comment it for manual review)
    sql = re.sub(r"(?i)\bIDENTITY\s*\([^)]*\)", " /* IDENTITY removed: use SEQUENCE + DEFAULT NEXTVAL */ ", sql)

    # COLLATE clauses not supported -> strip
    sql = re.sub(r"(?i)\bCOLLATE\s+\w+", "", sql)

    # NVARCHAR prefix N'string' -> plain 'string'
    sql = re.sub(r"(?i)N'([^']*)'", r"'\1'", sql)

    # ensure LIMIT is present if TOP was removed and no existing LIMIT (handled by sqlglot normally)
    return normalize_whitespace(sql)

def transpile_one(statement: str) -> str:
    """
    Use sqlglot to read as TSQL first; if that fails, try generic ANSI.
    Then write as Snowflake.
    """
    try:
        out = sqlglot.transpile(statement, read="tsql", write="snowflake", identify=True, pretty=True)
    except Exception:
        out = sqlglot.transpile(statement, read="ansi", write="snowflake", identify=True, pretty=True)
    s = ";\n".join(out)
    return post_process_snowflake(s)

def convert_text(sql_text: str) -> str:
    batches = split_batches(sql_text)
    converted = [transpile_one(b) for b in batches]
    return ";\n\n".join(filter(None, converted)) + ";\n"

# --- entrypoint ------------------------------------------------------------

def main():
    if len(sys.argv) == 1:
        # read from STDIN
        src = sys.stdin.read()
        print(convert_text(src))
    else:
        # treat each arg as a path
        for p in sys.argv[1:]:
            sql = Path(p).read_text(encoding="utf-8")
            out = convert_text(sql)
            sys.stdout.write(out)

if __name__ == "__main__":
    main()
