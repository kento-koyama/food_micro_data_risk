"""
sync_readme_en.py

README.md のテーブルブロック（<!-- table:name --> ... <!-- endtable -->）を
translation_jpn_to_eng.csv を使って翻訳し、README.en.md の対応ブロックを上書きする。

翻訳の適用ルール（誤訳防止のため文脈を限定）:
  - 実施機関名 (CSV rows 244–279) → **bold** テキストのみに適用
  - 調査名     (CSV rows 218–239) → [リンクテキスト](url) のみに適用
    ※リンクテキストとのマッチングはスペース・アンダースコアを除いた形で比較（書式の揺れを吸収）
  - 食品名等   (CSV rows 1–217)   → 適用しない（論文タイトルへの誤変換を防止）
  - テーブルのカラムヘッダ: 固定マッピングで翻訳
  - 整理状況・備考: 固定マッピングで翻訳

テーブル外の English 説明文には一切触れない。
"""

import re
import csv
import unicodedata
from pathlib import Path

# ─── CSV loading ──────────────────────────────────────────────────────────────

def load_csv_by_rowrange(csv_path: Path, start_row: int, end_row: int) -> dict:
    """
    1-indexed の行番号 [start_row, end_row] の範囲のみ読み込む。
    行番号はヘッダ行を Row 1 として数える。
    """
    translations = {}
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            row_num = i + 1
            if row_num == 1:
                continue  # ヘッダスキップ
            if row_num > end_row:
                break
            if row_num < start_row:
                continue
            if len(row) >= 2 and row[0].strip() and row[1].strip():
                translations[row[0].strip()] = row[1].strip()
    return translations

# ─── Fixed translation maps ───────────────────────────────────────────────────

HEADER_MAP = {
    "年度": "Year",
    "報告機関 ／ 報告プロジェクト": "Reporting Agency / Reporting Project",
    "整理状況": "Status",
}

STATUS_MAP = {
    "総説のため、元文献登録後削除": "Review article; to be removed after original literature is registered",
    "検査内容不明のため未登録": "Not yet registered (details unknown)",
    "web上に公開されていない": "Not available on the web",
    "陽性率のみ反映": "positivity rate only",
    "未登録": "Not yet registered",
    "不明": "Unknown",
    "済": "Done",
}

# ─── Normalization for fuzzy matching ────────────────────────────────────────

def compact(text: str) -> str:
    """
    マッチング比較用に正規化する。
    - Unicode 全角/半角を統一
    - スペースをすべて除去
    - アンダースコア（markdown イタリック記号）をすべて除去
    """
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\s_]", "", text)
    return text

def build_normalized_lookup(translations: dict) -> dict:
    """{compact(jpn): eng} の辞書を返す。キーの衝突は長いほうを優先。"""
    lookup = {}
    for jpn, eng in translations.items():
        key = compact(jpn)
        if key not in lookup or len(jpn) > len(min(lookup.get(key, ""), jpn)):
            lookup[key] = eng
    return lookup

# ─── Utilities ────────────────────────────────────────────────────────────────

def apply_map(text: str, mapping: dict) -> str:
    """キーの長い順に部分文字列置換（長いキーを先に処理して誤マッチを防ぐ）。"""
    for jpn, eng in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
        if jpn in text:
            text = text.replace(jpn, eng)
    return text

# ─── Table extraction / replacement ──────────────────────────────────────────

def extract_tables(md_text: str) -> dict:
    """{テーブル名: ブロック内テキスト} を返す。"""
    pattern = r"<!-- table:(.*?) -->(.*?)<!-- endtable -->"
    return {m.group(1).strip(): m.group(2) for m in re.finditer(pattern, md_text, re.DOTALL)}

def replace_table_block(md_text: str, table_name: str, new_block: str) -> str:
    pattern = rf"(<!-- table:{re.escape(table_name)} -->)(.*?)(<!-- endtable -->)"
    replacement = rf"\1\n{new_block}\n\3"
    return re.sub(pattern, replacement, md_text, flags=re.DOTALL)

# ─── Table translation ────────────────────────────────────────────────────────

def translate_row(
    line: str,
    inst_exact: dict,
    survey_norm: dict,
) -> str:
    """
    データ行を翻訳する。

    - **bold** テキスト → 実施機関名（完全一致）
    - [リンクテキスト](url) → 調査名（正規化マッチング）
    - 行全体 → STATUS_MAP（整理状況、備考など）
    """
    # 1. **bold** 内の実施機関名を翻訳（完全一致）
    def replace_bold(m: re.Match) -> str:
        content = m.group(1)
        return "**" + apply_map(content, inst_exact) + "**"
    line = re.sub(r"\*\*(.+?)\*\*", replace_bold, line)

    # 2. [リンクテキスト](url) 内の調査名を翻訳（正規化マッチング）
    def replace_link(m: re.Match) -> str:
        text = m.group(1)
        url  = m.group(2)
        key = compact(text)
        if key in survey_norm:
            return f"[{survey_norm[key]}]({url})"
        return m.group(0)  # マッチなし → 変更しない
    line = re.sub(r"\[(.+?)\]\((.+?)\)", replace_link, line)

    # 3. 整理状況・備考語句を翻訳
    line = apply_map(line, STATUS_MAP)

    return line

def translate_table_block(
    block: str,
    inst_exact: dict,
    survey_norm: dict,
) -> str:
    lines = block.split("\n")
    result = []
    header_done = False
    separator_done = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            result.append(line)
            continue

        if stripped.startswith("|") and not header_done:
            line = apply_map(line, HEADER_MAP)
            header_done = True
        elif stripped.startswith("|") and header_done and not separator_done:
            separator_done = True  # セパレータ行はそのまま
        elif stripped.startswith("|"):
            line = translate_row(line, inst_exact, survey_norm)

        result.append(line)

    return "\n".join(result)

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    base = Path(__file__).parent.parent.parent  # リポジトリルート

    csv_path = base / "database" / "translation_jpn_to_eng.csv"
    jp_path  = base / "README.md"
    en_path  = base / "README.en.md"

    # Row 218–239: 調査名, Row 244–279: 実施機関名
    surveys_raw  = load_csv_by_rowrange(csv_path, start_row=218, end_row=239)
    inst_exact   = load_csv_by_rowrange(csv_path, start_row=244, end_row=279)
    survey_norm  = build_normalized_lookup(surveys_raw)

    jp_text = jp_path.read_text(encoding="utf-8")
    en_text = en_path.read_text(encoding="utf-8")

    jp_tables = extract_tables(jp_text)
    en_tables  = extract_tables(en_text)

    updated = False
    for name, block in jp_tables.items():
        translated = translate_table_block(block, inst_exact, survey_norm).strip()

        if name not in en_tables:
            print(f"  [SKIP]   '{name}' は README.en.md に存在しません（手動で追加してください）")
            continue

        if en_tables[name].strip() != translated:
            en_text = replace_table_block(en_text, name, translated)
            print(f"  [UPDATE] {name}")
            updated = True
        else:
            print(f"  [OK]     {name} — 変更なし")

    if updated:
        en_path.write_text(en_text, encoding="utf-8")
        print("README.en.md を更新しました。")
    else:
        print("変更はありませんでした。")

if __name__ == "__main__":
    main()
