# neybot/cli.py
import click
from neybot.converter import tsql_to_snowflake

@click.command()
@click.argument("input_file", type=click.File("r"))
@click.argument("output_file", type=click.File("w"))
def main(input_file, output_file):
    """
    Convert T-SQL queries from INPUT_FILE to Snowflake SQL in OUTPUT_FILE.
    """
    tsql = input_file.read()
    snowflake_sql = tsql_to_snowflake(tsql)
    output_file.write(snowflake_sql)
    click.echo(f"✅ Converted -> {output_file.name}")

if __name__ == "__main__":
    main()
# neybot/cli.py (snippet)

@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path())
def main(input_path, output_path):
    text = Path(input_path).read_text(encoding="utf-8", errors="ignore")
    result = tsql_to_snowflake(text)
    Path(output_path).write_text(result, encoding="utf-8")
    click.echo(f"Converted -> {output_path}")
