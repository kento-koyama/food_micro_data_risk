import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import re

# 四捨五入で桁丸めるための関数を定義
def func_round(number, ndigits=0):
    if pd.isna(number):  # NaN チェック
        return np.nan  # NaN をそのまま返す
    p = 10 ** ndigits
    return float(int(number * p + 0.5) / p)

# 細菌名を斜体（属名 種小名）で整形
## LaTeXで表記（グラフ用）
def format_bacteria_name_latex(name):
    if pd.isna(name):
        return name
    spp_match = re.match(r'^([A-Z][a-z]+)\s+(spp?\.)$', name)
    if spp_match:
        genus, spp = spp_match.groups()
        return rf"$\it{{{genus}}}$ {spp}"
    match = re.match(r'^([A-Z][a-z]+)\s+([a-z]+)(.*)$', name)
    if match:
        genus, species, rest = match.groups()
        return rf"$\it{{{genus}\ {species}}}${rest}"
    return rf"$\it{{{name}}}$"

def calc_df_height(df, max_rows=5, row_height=35):
    """
    指定されたデータフレームの行数に基づき、適切な高さを計算します。
    
    Parameters:
        df (pd.DataFrame): 高さを計算する対象のデータフレーム。
        max_rows (int): 表示する最大行数。デフォルトは6行。
        row_height (int): 1行あたりの高さ（ピクセル単位）。デフォルトは35。
        
    Returns:
        int: データフレームの高さ（ピクセル単位）。
    """
    rows_to_display = min(len(df), max_rows)+1
    return row_height * rows_to_display

# ページの設定
st.set_page_config( 
                   page_title="陽性率可視化ソフトウェア", 
                #    page_icon="", 
                   layout="wide", 
                   initial_sidebar_state="expanded"
                   )

st.markdown("""
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/flag-icon-css/6.6.6/css/flag-icons.min.css');
</style>
""", unsafe_allow_html=True)


# フォントファイルのパスを設定
font_path = 'NotoSansCJKjp-Regular.otf'
# フォントの設定
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['text.usetex'] = False

# 図のフォントサイズを一括で設定
size_label = 22
size_title = 24

# CSVファイルのURL
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/database/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E9%99%BD%E6%80%A7%E7%8E%87.csv"
csv_url_gui = "https://github.com/kento-koyama/food_micro_data_risk/blob/main/database/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E9%99%BD%E6%80%A7%E7%8E%87.csv"


# Streamlit のアプリケーション
st.title('食中毒細菌の陽性率可視化ソフトウェア')
st.write("日本国内で流通している食品のうち、2000年から2025年にかけて検査されたものを対象としています。")
st.write("[収録されているデータ](%s)は、行政機関や研究所、大学などが公表した各種行政報告書や学術論文に基づいています。" % csv_url_gui)
st.write('各表をcsvファイルとしてダウンロードできます。')
st.write('-----------')


# データの読み込み
df = pd.read_csv(csv_url, encoding='utf-8-sig')

# --- 数値列（検体数・陽性数）の正規化と数値化 ---
_fw_map = str.maketrans('０１２３４５６７８９．－，', '0123456789.-,')
def _to_num(s):
    s2 = s.astype(str).str.translate(_fw_map).str.replace(',', '', regex=False).str.strip()
    s2 = s2.str.replace(r'[^0-9\.\-]', '', regex=True)   # 例: "6?" -> "6"
    return pd.to_numeric(s2, errors='coerce')

df['検体数'] = _to_num(df['検体数'])
df['陽性数'] = _to_num(df['陽性数'])

# 必要なカラムの欠損値を削除
df = df[df['検体数'].notna() & df['陽性数'].notna()]

# 細菌名を"Campylobacter spp."でまとめる
df['細菌名_詳細'] = df['細菌名']
df['細菌名'] = df['細菌名'].apply(lambda x: 'Campylobacter spp.' if 'Campylobacter' in str(x) else x)
df['細菌名_latex'] = df['細菌名'].apply(format_bacteria_name_latex)

# サイドバーにタイトルを追加
st.sidebar.title("検索")

# =========================
# 相互連動フィルタ（候補は「当該項目以外」の条件で決める）
# 矛盾（交差が空）のときだけ、現行の上流優先で自動リセット
# =========================
MISSING = "不明（欠損値）"
ALL = "すべて"
EMPTY = ""

FILTERS = [
    # (session_key, df_column, label)
    ("category_selected", "食品カテゴリ", "食品カテゴリ"),
    ("food_selected", "食品名", "食品名"),
    ("bacteria_selected", "細菌名", "細菌名"),
    ("institution_selected", "実施機関", "実施機関"),
]

# === 食品取扱区分（チェックボックス）設定 ===
# 注意: 下記のカテゴリ文字列は、実データの「食品取扱区分」列の値と完全一致している必要があります。
HANDLING_CATEGORIES = ["食材", "Ready-to-eat", "非可食部"]

def _handling_key(cat: str) -> str:
    """チェックボックス本体のキー（ウィジェット用。未描画時に破棄され得る）"""
    return f"handling_{cat}"

def _handling_state_key(cat: str) -> str:
    """選択状態を保持する永続キー（ウィジェットに紐づかないため破棄されない）"""
    return f"handling_state_{cat}"

def _sync_handling(cat: str):
    """チェックボックスの値を永続キーへ書き戻す"""
    st.session_state[_handling_state_key(cat)] = st.session_state[_handling_key(cat)]

# 欠損・前後空白の正規化（選択肢と一致させる）
for _, col, _ in FILTERS:
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip().fillna(MISSING)
    else:
        # 想定外の欠損カラム対策（通常は通りません）
        df[col] = MISSING

# 食品取扱区分はチェックボックスで制御するため、ここで個別に正規化（欠損はそのまま）
if "食品取扱区分" in df.columns:
    df["食品取扱区分"] = df["食品取扱区分"].astype("string").str.strip()

def is_active(v: str) -> bool:
    return v not in [EMPTY, ALL]

def apply_constraints(df_in: pd.DataFrame, exclude_key: str | None = None) -> pd.DataFrame:
    """exclude_key 以外の選択条件を df_in に適用"""
    out = df_in
    for key, col, _ in FILTERS:
        if key == exclude_key:
            continue
        v = st.session_state.get(key, EMPTY)
        if is_active(v):
            out = out[out[col] == v]
    return out

# === セレクトボックスの表示順設定 ===
# 先頭に固定するグループ（この順番で上から並べる。主に食品カテゴリ用）
CATEGORY_HEAD_ORDER = ["牛肉", "鶏肉", "豚肉", "肉類（その他）"]
# 末尾に固定する値（"その他" は常に最後）
CATEGORY_TAIL_ORDER = ["その他"]

def _option_sort_key(v: str):
    """選択肢の並び順キー
    1) CATEGORY_HEAD_ORDER の値を指定順で先頭に
    2) CATEGORY_TAIL_ORDER（完全一致の "その他"）を末尾に
    3) それ以外は通常の昇順
    """
    if v in CATEGORY_HEAD_ORDER:
        return (0, CATEGORY_HEAD_ORDER.index(v), "")
    if v in CATEGORY_TAIL_ORDER:
        return (2, 0, v)
    return (1, 0, v)

def make_options(series: pd.Series) -> list[str]:
    vals = sorted(pd.unique(series).tolist(), key=_option_sort_key)
    return [EMPTY, ALL] + vals

def make_food_options(df_in: pd.DataFrame, cat_col: str = "食品カテゴリ", food_col: str = "食品名") -> list[str]:
    """食品名の選択肢を、食品カテゴリのまとまりを維持して並べる。
    カテゴリは CATEGORY_HEAD_ORDER / CATEGORY_TAIL_ORDER の並び順、
    カテゴリ内の食品名は昇順。複数カテゴリに跨る食品名は最初の出現位置を採用。
    """
    pairs = df_in[[cat_col, food_col]].astype(str).drop_duplicates()
    records = list(pairs.itertuples(index=False, name=None))  # (category, food)
    records.sort(key=lambda r: (_option_sort_key(r[0]), r[1]))
    seen: list[str] = []
    for _cat, food in records:
        if food not in seen:
            seen.append(food)
    return [EMPTY, ALL] + seen

# session_state 初期化
for key, _, _ in FILTERS:
    st.session_state.setdefault(key, EMPTY)

# 食品取扱区分の選択状態（永続キーで保持。デフォルト: 全カテゴリ選択）
for cat in HANDLING_CATEGORIES:
    st.session_state.setdefault(_handling_state_key(cat), True)

# 1) 上流フィルタのみで各候補を生成
# 「上流（自分より前のフィルタ）の選択」だけで選択肢を絞る。
# 下流フィルタの変化が上流フィルタの選択肢を狭めないようにすることで、
# 下流を変えても上流の選択がリセットされる問題を防ぐ。
options_map: dict[str, list[str]] = {}
for i, (key, col, _) in enumerate(FILTERS):
    df_up = df.copy()
    for j in range(i):
        up_key, up_col, _ = FILTERS[j]
        v = st.session_state.get(up_key, EMPTY)
        if is_active(v):
            df_up = df_up[df_up[up_col] == v]
    if key == "food_selected":
            # 食品名は食品カテゴリのまとまりを維持して並べる
            options_map[key] = make_food_options(df_up)
    else:
        options_map[key] = make_options(df_up[col])

# 2) 上流の変化で候補から外れた選択だけリセット
for key, _, _ in FILTERS:
    if st.session_state[key] not in options_map[key]:
        st.session_state[key] = EMPTY

# 3) selectbox 描画（順序は表示順。ロジックは順序非依存）
# 「食品カテゴリ」の直後に、食品取扱区分チェックボックス用のコンテナを差し込む
# （スケッチ通りの表示位置。中身は後で any_input が確定してから埋める）
handling_container = None
for key, _, label in FILTERS:
    st.sidebar.selectbox(
        f"{label}を入力 または 選択してください:",
        options_map[key],
        format_func=lambda x: "" if x == EMPTY else x,
        key=key
    )
    if key == "category_selected":
        handling_container = st.sidebar.container()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "[📁 GitHubリポジトリ](https://github.com/kento-koyama/food_micro_data_risk)"
)
st.sidebar.markdown(
    "[🦠 汚染濃度ソフトウェア](https://concentration-of-contamination1-624097414875.asia-northeast1.run.app/)"
)

# 4) 最終的な絞り込み（全条件のAND）
df_filtered = apply_constraints(df, exclude_key=None)

# 5) 矛盾（交差が空）のときだけ「現行の上流優先」で解除して復帰
any_selected = any(is_active(st.session_state[k]) for k, _, _ in FILTERS)
if any_selected and df_filtered.empty:
    df_tmp = df.copy()
    for i, (key, col, label) in enumerate(FILTERS):
        v = st.session_state[key]
        if is_active(v):
            next_df = df_tmp[df_tmp[col] == v]
            if next_df.empty:
                # この階層が矛盾点：ここ以降を未選択に戻す（現行仕様）
                for j in range(i, len(FILTERS)):
                    st.session_state[FILTERS[j][0]] = EMPTY
                st.warning(f"選択条件が矛盾したため、「{label}」以降を未選択に戻しました。")
                st.rerun()
            df_tmp = next_df
    df_filtered = apply_constraints(df, exclude_key=None)

# --- 図が表示される状態か（4フィルタのいずれかが選択されているか）を判定 ---
any_input = any(st.session_state[k] != EMPTY for k, _, _ in FILTERS)

# --- 食品取扱区分チェックボックスの描画（any_input のときだけ・食品カテゴリ直後の位置に） ---
if any_input and handling_container is not None:
    with handling_container:
        # 食品取扱区分
        # 各カテゴリのチェックボックス（食材・Ready-to-eat・非可食部）
        # value で永続キーの状態を初期値に反映し、on_change で永続キーへ書き戻す
        for cat in HANDLING_CATEGORIES:
            st.checkbox(
                cat,
                key=_handling_key(cat),
                value=st.session_state[_handling_state_key(cat)],
                on_change=_sync_handling,
                args=(cat,),
            )

# --- 選択されている食品取扱区分のリストを取得 ---
if any_input:
    # 永続キー（状態の保持元）から選択状態を取得（既定 True）
    selected_handling_list = [
        cat for cat in HANDLING_CATEGORIES if st.session_state.get(_handling_state_key(cat), True)
    ]
else:
    selected_handling_list = list(HANDLING_CATEGORIES)  # 既定値（未表示時は使用しない）

# --- 食品取扱区分でのフィルタ適用 ---
# 全カテゴリ選択時は従来の「すべて」と同じ＝フィルタ無し（欠損やその他値も表示）
# 一部のみ選択時は isin で絞り込み
# 全て未選択時は下の表示制御で警告（フィルタはここでは適用しない）
if any_input and "食品取扱区分" in df_filtered.columns:
    if set(selected_handling_list) == set(HANDLING_CATEGORIES):
        pass  # 全選択 = 絞り込みなし
    elif selected_handling_list:
        df_filtered = df_filtered[df_filtered["食品取扱区分"].isin(selected_handling_list)]

# --- 既存仕様（空欄の扱い）を維持するための「表示・分岐用」正規化 ---
# どれか1つでも入力があれば、未選択("")は「すべて」として扱う（フィルタ自体は変えない）
selected_category = st.session_state["category_selected"]          # ★既存コードの selected_category は「食品カテゴリ」を維持
selected_food = st.session_state["food_selected"]
selected_bacteria = st.session_state["bacteria_selected"]
selected_institution = st.session_state["institution_selected"]

if any_input:
    if selected_category == EMPTY: selected_category = ALL
    if selected_food == EMPTY: selected_food = ALL
    if selected_bacteria == EMPTY: selected_bacteria = ALL
    if selected_institution == EMPTY: selected_institution = ALL

# 食品取扱区分の表示ラベル（group_title 用）
if any_input and selected_handling_list and set(selected_handling_list) != set(HANDLING_CATEGORIES):
    handling_label = "・".join(selected_handling_list)
elif any_input and not selected_handling_list:
    handling_label = "（なし）"
else:
    handling_label = ALL

# 常に group_title を定義（食品取扱区分を先頭に追加）
if all(v == ALL for v in [selected_category, selected_food, selected_bacteria, selected_institution]) and handling_label == ALL:
    group_title = "（すべて）"
else:
    group_title = f"（{handling_label} - {selected_category} - {selected_food} - {selected_bacteria} - {selected_institution}）"


# 表示条件を確認して出力制御
if not any_input:
    st.info("入力または選択を行ってください。")
# 食品取扱区分が一つも選択されていない場合（チェックを全て外した場合）
elif not selected_handling_list:
    st.warning("食品取扱区分が選択されていません。チェックボックスから少なくとも一つ選択してください。")
# データがない場合は処理を中止して警告を表示
elif df_filtered.empty:
    st.warning("該当するデータがありません。条件を変更してください。")
else:
    if selected_bacteria in ["", "すべて"]:
        # --- Ensure numeric types for counts (cleans full-width digits, commas, stray chars) ---
        fw_map = str.maketrans('０１２３４５６７８９．－，', '0123456789.-,')
        def _coerce_numeric_col(s):
            s2 = s.astype(str).str.translate(fw_map) \
                               .str.replace(',', '', regex=False) \
                               .str.replace(r'[^0-9\.\-]', '', regex=True)  # 例: "6?" -> "6"
            return pd.to_numeric(s2, errors='coerce')

        df_filtered = df_filtered.assign(
            検体数=_coerce_numeric_col(df_filtered['検体数']),
            陽性数=_coerce_numeric_col(df_filtered['陽性数'])
        )
        # 細菌ごとの集計
        bacteria_counts = df_filtered.groupby(['細菌名', '細菌名_latex']).agg({
            '検体数': 'sum', '陽性数': 'sum'
        }).reset_index()
        den = bacteria_counts['検体数'].replace(0, pd.NA)
        bacteria_counts['陽性率 (%)'] = (bacteria_counts['陽性数'] / den * 100)
        bacteria_counts['陽性率 (%)'] = bacteria_counts['陽性率 (%)'].apply(lambda x: func_round(x, 2))
        # 表示用ラベル
        bacteria_counts.rename(columns={
            '細菌名_latex': '表示名_LaTeX'
        }, inplace=True)


        # 検体数テーブル＆グラフ
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f'細菌別の食品検体数 {group_title}')
            st.dataframe(bacteria_counts[['細菌名', '検体数']], height=calc_df_height(bacteria_counts), hide_index=True)
        with col2:
            fig1, ax1 = plt.subplots(figsize=(8, 8))
            ax1.barh(bacteria_counts['表示名_LaTeX'], bacteria_counts['検体数'], color='skyblue')
            ax1.set_xlabel('検体数', fontsize=size_label)
            ax1.set_ylabel('細菌名', fontsize=size_label)
            ax1.set_title(f'細菌別の食品検体数\n{group_title}', fontsize=size_title)
            ax1.tick_params(axis='both', labelsize=size_label)
            ax1.invert_yaxis()
            ax1.set_box_aspect(1)
            st.pyplot(fig1)

        st.write("-----------")

        # 陽性率テーブル＆グラフ
        col3, col4 = st.columns(2)
        with col3:
            st.subheader(f'細菌の陽性率 {group_title}')
            st.dataframe(bacteria_counts[['細菌名', '陽性率 (%)']], height=calc_df_height(bacteria_counts), hide_index=True)
        with col4:
            fig2, ax2 = plt.subplots(figsize=(8, 8))
            ax2.barh(bacteria_counts['表示名_LaTeX'], bacteria_counts['陽性率 (%)'], color='skyblue')
            ax2.set_xlim([0,100])
            ax2.set_xlabel('陽性率 (%)', fontsize=size_label)
            ax2.set_ylabel('細菌名', fontsize=size_label)
            ax2.set_title(f'細菌の陽性率\n{group_title}', fontsize=size_title)
            ax2.tick_params(axis='both', labelsize=size_label)
            ax2.invert_yaxis()
            ax2.set_box_aspect(1)
            st.pyplot(fig2)

        st.write("-----------")

    else:
        # 細菌を指定した場合：カテゴリ別に集計
        category_summary = df_filtered.groupby('食品カテゴリ').agg({'検体数': 'sum', '陽性数': 'sum'}).reset_index()
        den_cat = category_summary['検体数'].replace(0, pd.NA)
        category_summary['陽性率 (%)'] = (category_summary['陽性数'] / den_cat * 100)
        category_summary["陽性率 (%)"] = category_summary["陽性率 (%)"].apply(lambda x: func_round(x, ndigits=2))

        col5, col6 = st.columns(2)
        with col5:
            st.subheader(f'食品カテゴリごとの陽性率 {group_title}')
            st.dataframe(category_summary, height=calc_df_height(category_summary), hide_index=True)
        with col6:
            fig3, ax3 = plt.subplots(figsize=(8, 8))
            ax3.barh(category_summary['食品カテゴリ'], category_summary['陽性率 (%)'], color='skyblue')
            ax3.set_xlim([0,100])
            ax3.set_xlabel('陽性率 (%)', fontsize=size_label)
            ax3.set_ylabel('食品カテゴリ', fontsize=size_label)
            ax3.set_title(f'食品カテゴリごとの陽性率\n{group_title}', fontsize=size_title)
            ax3.tick_params(axis='both', which='major', labelsize=size_label)
            ax3.invert_yaxis()
            ax3.set_box_aspect(1)
            st.pyplot(fig3)

        st.write('-----------')

    # 選択されたカテゴリと食品名に基づくデータの表示
    st.subheader(f'選択された食品カテゴリと食品名に該当するデータ {group_title}')
    df_filtered_display = df_filtered.copy()
    df_filtered_display = df_filtered_display[['調査年', '食品取扱区分', '食品カテゴリ', '食品名', '細菌名', '細菌名_詳細',
                                            '検体数', '陽性数', '実施機関', '調査名', 'Source URL', '閲覧日', '備考']]

    # URL整形（空/NaN対策 + 前後空白除去）
    df_filtered_display["Source URL"] = (
        df_filtered_display["Source URL"].astype("string").fillna("").str.strip()
    )

    link_cfg = {
        "Source URL": st.column_config.LinkColumn("Source URL")
    }

    st.dataframe(df_filtered_display, hide_index=True, column_config=link_cfg)

    st.write('-----------')

    # 陽性数が1以上のデータをフィルタリングして表示
    positive_df = df_filtered_display[df_filtered_display['陽性数'] >= 1]
    st.subheader(f'陽性数が1以上のデータ {group_title}')
    st.dataframe(positive_df, hide_index=True, column_config=link_cfg)



# 現在のページを指定
current_page = "jp"

language_switch_html = f"""
    <style>
    .language-switch {{
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        background-color: transparent;  /* 背景を透明に */
        border: none;                   /* 枠線なし */
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 14px;
    }}
    .language-switch a {{
        margin: 0 5px;
        text-decoration: none;
        font-weight: bold;
    }}
    .language-switch .inactive {{
        color: #ccc;
        pointer-events: none;
        cursor: default;
    }}
    .language-switch .active {{
        color: #000;
    }}
    .language-switch .active:hover {{
        color: #0366d6;
    }}
    </style>
    <div class="language-switch">
        <a href="/" target="_self" class="{ 'inactive' if current_page == 'jp' else 'active' }">
            <span class="fi fi-jp"></span> Japanese
        </a> |
        <a href="/main_eng" target="_self" class="{ 'inactive' if current_page == 'en' else 'active' }">
            <span class="fi fi-gb"></span> English
        </a>
    </div>
"""
st.markdown(language_switch_html, unsafe_allow_html=True)

# デフォルトのメニューバーを非表示
HIDE_UI_STYLE = """
<style>
/* ----------------------------
   1) ヘッダーは残す（サイドバー開閉トグルのため）
---------------------------- */
header, header[data-testid="stHeader"] {
    visibility: visible !important;
    height: auto !important;
}

/* ----------------------------
   2) MainMenu（…/kebab）を隠す
   - 新しめ: data-testid="stMainMenu"
   - 旧: #MainMenu
---------------------------- */
[data-testid="stMainMenu"] { 
    display: none !important; 
}
#MainMenu { 
    visibility: hidden; 
}

/* ----------------------------
   3) ついでに不要UI
   - Deployボタン/StatusWidget を隠す（ある場合のみ）
---------------------------- */
[data-testid="stDeployButton"] {
    display: none !important;
}
[data-testid="stStatusWidget"] {
    display: none !important;
}

/* ----------------------------
   4) フッター
---------------------------- */
footer {
    visibility: hidden;
}

/* ----------------------------
   5) サイドバー開閉トグルを明示的に残す
   - バージョンによって data-testid が違うことがあるので複数指定
---------------------------- */
button[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] {
    display: inline-flex !important;
    visibility: visible !important;
}

/* 見た目が崩れる場合の保険（トグル周辺のコンテナが潰れるのを防ぐ） */
div[data-testid="stToolbar"] {
    visibility: visible !important;
}
</style>
"""
st.markdown(HIDE_UI_STYLE, unsafe_allow_html=True)

# お問い合わせリンクの追加
contact_link = """
    <style>
    .footer {
        position: fixed;
        bottom: 10px;
        right: 10px;
        font-size: 16px;
    }
    .footer a {
        text-decoration: none;
        color: #0366d6;
    }
    </style>
    <div class="footer">
        お問い合わせは
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSf2FwkiAWmr3g_50BpPAx5_87w3pwLMPRYeKwCFSfqgSJ1iTA/viewform?usp=header" target="_blank">
        こちら</a>
        から
    </div>
"""
st.markdown(contact_link, unsafe_allow_html=True)

