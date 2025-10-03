# tsql_to_snowflake.py
# Full script converter: T-SQL (SQL Server) -> Snowflake
# Handles multi-statement scripts and GO batch separators.

from __future__ import annotations
from pathlib import Path
import argparse
import re
import sys

import sqlglot


GO_PATTERN = re.compile(r"(?mi)^\s*GO\s*(?:--.*)?$")


def split_batches(text: str) -> list[str]:
    """Split a script into batches on GO lines (like SSMS)."""
    parts: list[str] = []
    last = 0
    for m in GO_PATTERN.finditer(text):
        parts.append(text[last:m.start()].rstrip())
        last = m.end()
    tail = text[last:].rstrip()
    if tail:
        parts.append(tail)
    return [p for p in parts if p.strip()]


def transpile_block(
    sql_text: str,
    read_dialect: str = "tsql",
    write_dialect: str = "snowflake",
    pretty: bool = True,
) -> str:
    """
    Transpile one block of SQL using sqlglot.
    Returns Snowflake SQL (possibly multiple statements).
    """
    # sqlglot.transpile returns a list of SQL strings (one per statement)
    stmts = sqlglot.transpile(
        sql_text,
        read=read_dialect,
        write=write_dialect,
        pretty=pretty,
    )
    if not stmts:
        return ""
    # Join statements with a single trailing semicolon and newline
    out = ";\n\n".join(s.rstrip(" ;") for s in stmts)
    return out + ";\n"


def convert_script(
    text: str,
    read_dialect: str = "tsql",
    write_dialect: str = "snowflake",
    pretty: bool = True,
    on_error: str = "comment",  # 'comment' | 'raise' | 'skip'
) -> str:
    """
    Convert an entire script (multiple batches).
    Splits on GO, converts batch-by-batch, rejoins with spacing.
    """
    batches = split_batches(text) or [text]
    outputs: list[str] = []

    for i, batch in enumerate(batches, start=1):
        try:
            converted = transpile_block(
                batch, read_dialect=read_dialect, write_dialect=write_dialect, pretty=pretty
            )
            if converted.strip():
                outputs.append(converted.rstrip())
        except Exception as e:
            if on_error == "raise":
                raise
            elif on_error == "skip":
                # Drop the batch but keep a marker so user knows
                outputs.append(f"-- [sqlglot] skipped batch {i} due to: {e}")
            else:
                # Comment the original T-SQL so you can manually fix it later
                commented = "\n".join(f"-- {line}" for line in batch.splitlines())
                outputs.append(
                    f"-- [sqlglot] failed to convert batch {i}: {e}\n{commented}"
                )

    # Two newlines between batches for readability
    return "\n\n".join(outputs).rstrip() + "\n"


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Transpile SQL from one dialect to another (script-aware, splits on GO)."
    )
    p.add_argument("infile", nargs="?", help="Input .sql (omit to read from stdin)")
    p.add_argument("outfile", nargs="?", help="Output .sql (omit to print to stdout)")
    p.add_argument(
        "--from",
        dest="from_dialect",
        default="tsql",
        help="Input dialect (default: tsql)",
    )
    p.add_argument(
        "--to",
        dest="to_dialect",
        default="snowflake",
        help="Output dialect (default: snowflake)",
    )
    p.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print output SQL (default: on)",
    )
    p.add_argument(
        "--no-pretty",
        dest="pretty",
        action="store_false",
        help="Disable pretty-print formatting",
    )
    p.add_argument(
        "--on-error",
        choices=["comment", "skip", "raise"],
        default="comment",
        help="What to do if a batch fails: comment (default), skip, or raise.",
    )
    return p


def main() -> None:
    args = build_argparser().parse_args()

    # Read
    if args.infile:
        inp = Path(args.infile)
        if not inp.exists():
            print(f"Input file not found: {inp}", file=sys.stderr)
            sys.exit(1)
        text = inp.read_text(encoding="utf-8", errors="ignore")
    else:
        text = sys.stdin.read()

    # Convert
    out_text = convert_script(
        text,
        read_dialect=args.from_dialect,
        write_dialect=args.to_dialect,
        pretty=args.pretty,
        on_error=args.on_error,
    )

    # Write
    if args.outfile:
        outp = Path(args.outfile)
        outp.write_text(out_text, encoding="utf-8")
        print(f"Wrote Snowflake SQL -> {outp}")
    else:
        print(out_text)


if __name__ == "__main__":
    main()
