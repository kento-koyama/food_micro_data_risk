import pandas as pd
import re
from pathlib import Path

def extract_tables_from_md(md_text):
    pattern = r"<!-- table:(.*?) -->(.*?)<!-- endtable -->"
    matches = re.findall(pattern, md_text, flags=re.DOTALL)
    tables = {}
    for name, content in matches:
        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
        if len(lines) >= 2:
            headers = [h.strip() for h in lines[0].strip('|').split('|')]
            rows = [[cell.strip() for cell in row.strip('|').split('|')] for row in lines[2:]]
            df = pd.DataFrame(rows, columns=headers)
            tables[name.strip()] = df
    return tables

md_path = Path("README.md")
out_dir = Path("tables")
out_dir.mkdir(exist_ok=True)

with md_path.open("r", encoding="utf-8") as f:
    md_text = f.read()

tables = extract_tables_from_md(md_text)

for name, df in tables.items():
    df.to_excel(out_dir / f"{name}.xlsx", index=False)
