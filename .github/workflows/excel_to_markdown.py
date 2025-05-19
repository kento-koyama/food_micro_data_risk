import pandas as pd
import re
from pathlib import Path

def df_to_markdown(df):
    header = '| ' + ' | '.join(df.columns) + ' |'
    separator = '| ' + ' | '.join(['---'] * len(df.columns)) + ' |'
    rows = ['| ' + ' | '.join(map(str, row)) + ' |' for row in df.values]
    return '\n'.join([header, separator] + rows)

def replace_tables_in_md(md_text, table_md_blocks):
    for name, md_table in table_md_blocks.items():
        pattern = rf"(<!-- table:{name} -->)(.*?)(<!-- endtable -->)"
        replacement = rf"\1\n{md_table}\n\3"
        md_text = re.sub(pattern, replacement, md_text, flags=re.DOTALL)
    return md_text

md_path = Path("README.md")
in_dir = Path("tables")

with md_path.open("r", encoding="utf-8") as f:
    md_text = f.read()

table_md_blocks = {}

for excel_file in in_dir.glob("*.xlsx"):
    name = excel_file.stem
    df = pd.read_excel(excel_file, engine="openpyxl")
    table_md_blocks[name] = df_to_markdown(df)

updated_md = replace_tables_in_md(md_text, table_md_blocks)

with md_path.open("w", encoding="utf-8") as f:
    f.write(updated_md)
