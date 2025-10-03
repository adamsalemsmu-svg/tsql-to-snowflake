from __future__ import annotations
import re
from typing import List
import sqlglot

def _clean_tsql(raw: str) -> List[str]:
    """
    Preprocess T-SQL text:
    - Remove /* ... */ block comments
    - Remove -- line comments
    - Split batches on GO lines
    - Return non-empty chunks ready for transpile
    """
    text = raw.replace("\r\n", "\n")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)     # block comments
    text = re.sub(r"--.*?$", "", text, flags=re.M)        # line comments
    batches = re.split(r"(?im)^\s*GO\s*;?\s*$", text)     # GO delimiters
    return [b.strip() for b in batches if b.strip()]

def tsql_to_snowflake(tsql_text: str) -> str:
    """
    Transpile T-SQL to Snowflake SQL, automatically ignoring GO and comments.
    Returns a single Snowflake script string.
    """
    out_chunks: List[str] = []
    for chunk in _clean_tsql(tsql_text):
        if not chunk:
            continue
        try:
            rendered = sqlglot.transpile(
                chunk,
                read="tsql",
                write="snowflake",
                pretty=True,
                identify=True,  # keep quoted identifiers
            )
            if rendered:
                out_chunks.append(";\n".join(s.strip().rstrip(";") for s in rendered) + ";")
        except Exception as e:
            out_chunks.append(f"-- [neybot] skipped chunk due to parse error: {e}")
    return "\n\n".join(out_chunks)
