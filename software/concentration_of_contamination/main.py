import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
from io import BytesIO
import os
import re

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


# 四捨五入で桁丸めるための関数を定義
def func_round(number, ndigits=0):
    if pd.isna(number):  # NaN チェック
        return np.nan  # NaN をそのまま返す
    p = 10 ** ndigits
    return float(int(number * p + 0.5) / p)

# 単位から重量を抽出してMPN/gに変換
def convert_to_mpn_per_g(row):
    """
    単位のフォーマットに応じて汚染濃度をMPN/gに変換する
    """
    if isinstance(row['単位'], str) and 'MPN/' in row['単位']:
        # 単位から基準重量を抽出 (例: 'MPN/100g' -> 100)
        match = re.search(r'MPN/(\d+)g', row['単位'])
        if match:
            weight = int(match.group(1))  # 重量部分を取得
        else:
            weight = 1  # 'MPN/g' の場合は重さを 1 に設定
        return row['汚染濃度'] / weight  # 重量で割ってMPN/gに変換
    return np.nan  # 該当しない場合はNaN


# 表示用フォーマット関数
def format_number(number, ndigits=0):
    formatted = f"{number:.{ndigits}f}".rstrip('0').rstrip('.')
    return formatted

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
                   page_title="汚染濃度可視化ソフトウェア", 
                #    page_icon="", 
                   layout="wide", 
                   initial_sidebar_state="expanded"
                   )
st.markdown("""
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/flag-icon-css/6.6.6/css/flag-icons.min.css');
</style>
""", unsafe_allow_html=True)

# CSVファイルのパス（適宜変更してください）
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/database/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E6%BF%83%E5%BA%A6.csv"
csv_url_gui = "https://github.com/kento-koyama/food_micro_data_risk/blob/main/database/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E6%BF%83%E5%BA%A6.csv"

# 汚染率の可視化アプリURL
app_ratio_url = "https://m7gk8u5qjmoysfsmf5kgqk.streamlit.app/"

# フォントファイルのパスを設定
font_path = 'NotoSansCJKjp-Regular.otf'

# フォントの設定
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['text.usetex'] = False  # LaTeXをmatplotlibで有効に

# 図のフォントサイズを一括で設定
size_label = 18
size_title = 20


# Streamlit のアプリケーション
st.write('### 食中毒細菌の汚染濃度可視化ソフトウェア')
st.write("日本国内で流通している食品のうち、2000年から2025年にかけて検査されたものを対象としています。")
st.write("[収録されているデータ](%s)は、行政機関や研究所、大学などが公表した各種行政報告書や学術論文に基づいています。" % csv_url_gui)
st.write('各表をcsvファイルとしてダウンロードできます。')
st.write('-----------')

# サイドバーにタイトルを追加
st.sidebar.title("検索")


# データの読み込み
df = pd.read_csv(csv_url, encoding='utf-8-sig')

# "不検出" または "-" または NaN または "<" または "未満" を含む値を除外
df = df[~((df['汚染濃度'] == '不検出') | 
          (df['汚染濃度'] == '未検出') | 
          (df['汚染濃度'] == '-') | 
          (df['汚染濃度'].isna()) | 
          (df['汚染濃度'].astype(str).str.contains('<')) | 
          (df['汚染濃度'].astype(str).str.contains('未満')))]
# 食品カテゴリと食品名が共にNaNの行を除外
df = df[~(df['食品カテゴリ'].isna() & df['食品名'].isna())]
# 単位を指定
df = df[(df['単位']!='CFU/と体')&(df['単位']!='log CFU/と体')]
df = df[(df['単位'] == 'log CFU/g')|(df['単位'] == 'CFU/g')|(df['検査方法'] == 'MPN')]

# グラフ用の汚染濃度列を作成し、桁丸めを適用
df['汚染濃度'] = pd.to_numeric(df['汚染濃度'], errors='coerce')  # 汚染濃度を数値に変換（エラーをNaNに設定）

# 汚染濃度を数値型に変換（変換できない値はNaNに）
df['汚染濃度'] = pd.to_numeric(df['汚染濃度'], errors='coerce')
df = df[~((df['汚染濃度'].isna()))]

# MPNを1gあたりに統一
df['汚染濃度_MPN/g'] = df.apply(
    lambda row: convert_to_mpn_per_g(row) if 'MPN' in str(row['単位']) else np.nan, 
    axis=1
)

# 汚染濃度_logCFU/gの計算
df['汚染濃度_logCFU/g'] = np.where(
    df['単位'].str.contains('MPN', na=False),  # 単位がMPNの場合
    np.log10(df['汚染濃度_MPN/g']),  # MPNを常用対数に変換
    np.where(
        df['単位'] == 'CFU/g',  # 単位がCFUの場合
        np.log10(df['汚染濃度']),  # CFUを常用対数に変換
        df['汚染濃度']  # その他（例: log CFU/g）はそのまま利用
    )
)

# 小数点以下を2桁に丸める
df['汚染濃度_logCFU/g'] = df['汚染濃度_logCFU/g'].apply(lambda x: func_round(x, ndigits=2))
# 細菌名を"Campylobacter spp."でまとめる
df['細菌名_詳細'] = df['細菌名']
df['細菌名'] = df['細菌名'].apply(lambda x: 'Campylobacter spp.' if 'Campylobacter' in str(x) else x)
# 細菌名を整形し、latex表記列を作成
df['細菌名_latex'] = df['細菌名'].apply(format_bacteria_name_latex)

df = df.iloc[:, [0,1,2,3,4,5,6,7,8,17,9,10,16,15,11,12,13,14,18]]

# 初期状態の選択肢
food_categories = [""] + ["すべて"] + list(df['食品カテゴリ'].unique())
food_names = [""] + ["すべて"] + list(df['食品名'].unique())
bacteria_names = [""] + ["すべて"] + list(df['細菌名'].unique())
institutions = [""] + ["すべて"] + list(df['実施機関'].unique())  

# サイドバーで食品カテゴリを選択
selected_group = st.sidebar.selectbox(
    '食品カテゴリを入力 または 選択してください:',
    food_categories,
    format_func=lambda x: "" if x == "" else x,
    key="category_selected"
)

# データをフィルタリング（食品カテゴリに基づく）
df_filtered = df if selected_group == "" or selected_group == "すべて" else df[df['食品カテゴリ'] == selected_group]

# サイドバーで食品名を選択
food_names_filtered = [""] + ["すべて"] + list(df_filtered['食品名'].unique())
selected_food = st.sidebar.selectbox(
    '食品名を入力 または 選択してください:',
    food_names_filtered,
    format_func=lambda x: "" if x == "" else x,
    key="food_selected"
)

# データをフィルタリング（食品名に基づく）
df_filtered = df_filtered if selected_food == "" or selected_food == "すべて" else df_filtered[df_filtered['食品名'] == selected_food]

# サイドバーで細菌名を選択
bacteria_names_filtered = [""] + ["すべて"] + list(df_filtered['細菌名'].unique())
selected_bacteria = st.sidebar.selectbox(
    '細菌名を入力 または 選択してください:',
    bacteria_names_filtered,
    format_func=lambda x: "" if x == "" else x,
    key="bacteria_selected"
)

# データをフィルタリング（細菌名に基づく）
df_filtered = df_filtered if selected_bacteria == "" or selected_bacteria == "すべて" else df_filtered[df_filtered['細菌名'] == selected_bacteria]

# サイドバーで実施機関を選択
institutions_filtered = [""] + ["すべて"] + list(df_filtered['実施機関'].unique())
selected_institution = st.sidebar.selectbox(
    '実施機関を入力 または 選択してください:',
    institutions_filtered,
    format_func=lambda x: "" if x == "" else x,
    key="institution_selected"
)

# データをフィルタリング（実施機関に基づく）
df_filtered = df_filtered if selected_institution == "" or selected_institution == "すべて" else df_filtered[df_filtered['実施機関'] == selected_institution]

# --- 可食部のみ表示（鶏・豚・牛カテゴリ選択時のみ） ---
MEAT_CATEGORIES = {"鶏肉", "豚肉", "牛肉", "その他の肉類", "ソーセージ"}

# 「鶏・豚・牛」を選んだときだけチェックボックスを表示
show_edible_checkbox = (selected_group in MEAT_CATEGORIES)

if show_edible_checkbox:
    edible_only = st.sidebar.checkbox(
        "可食部のみ表示", value=False,
        help="消化管内容物などの非可食部を除外して表示します"
    )
else:
    edible_only = False

# チェック時は『食品名』に「内容物」を含む行を除外（= 非可食部を除外）
if edible_only:
    if '食品名' in df_filtered.columns:
        df_filtered = df_filtered[~df_filtered['食品名'].astype(str).str.contains("内容物", na=False)]

# 未選択項目を自動的に "すべて" に設定
if selected_group == "" and (selected_food != "" or selected_bacteria != "" or selected_institution != ""):
    selected_group = "すべて"
if selected_food == "" and (selected_group != "" or selected_bacteria != "" or selected_institution != ""):
    selected_food = "すべて"
if selected_bacteria == "" and (selected_group != "" or selected_food != "" or selected_institution != ""):
    selected_bacteria = "すべて"
if selected_institution == "" and (selected_group != "" or selected_food != "" or selected_bacteria != ""):
    selected_institution = "すべて"

# 常に group_title を定義
group_title = f"（{selected_group} - {selected_food} - {selected_bacteria} - {selected_institution}）" if selected_group != 'すべて' or selected_food != 'すべて' or selected_bacteria != 'すべて' or selected_institution != 'すべて' else "（すべて）"

# 表示条件を確認して出力制御
if selected_group == "" and selected_food == "" and selected_bacteria == "" and selected_institution == "":
    st.info("入力または選択を行ってください。")

# データがない場合は処理を中止して警告を表示
elif df_filtered.empty:
    st.warning("該当するデータがありません。条件を変更してください。")
else:
    if selected_bacteria == "すべて":  # 細菌名の絞り込みがない場合に表示
        # 細菌ごとの検体数の合計を表示
        st.subheader(f'細菌ごとの食品検体数{group_title}')
        col1, col2 = st.columns(2)

        with col1:
            bacteria_samplesize = df_filtered['細菌名'].value_counts().reset_index()
            bacteria_samplesize.columns = ['細菌名', '検体数']
            st.dataframe(bacteria_samplesize, height=calc_df_height(bacteria_samplesize), hide_index=True)

        with col2:
            fig1, ax1 = plt.subplots(figsize=(8,6))
            # ラベルもlatex用に変換
            if '細菌名_latex' not in df_filtered.columns:
                df_filtered = df_filtered.assign(細菌名_latex=df_filtered['細菌名'].apply(format_bacteria_name_latex))
            bacteria_samplesize = bacteria_samplesize.merge(df_filtered[['細菌名', '細菌名_latex']].drop_duplicates(), on='細菌名', how='left')
            ax1.barh(bacteria_samplesize['細菌名_latex'], bacteria_samplesize['検体数'], color='skyblue')
            ax1.set_xlabel('検体数', fontsize=size_label)
            ax1.set_ylabel('細菌名', fontsize=size_label)
            ax1.set_title(f'細菌ごとの食品検体数{group_title}', fontsize=size_title)
            ax1.tick_params(axis='both', which='major', labelsize=size_label)
            st.pyplot(fig1)

        st.write('-----------')

        # すべての細菌の汚染濃度を表示
        st.subheader(f'すべての細菌の汚染濃度{group_title}')
        col3, col4 = st.columns(2)

        with col3:
            df_bacteria_counts = df_filtered.copy()
            df_bacteria_counts = df_bacteria_counts.loc[:, ['調査年', '細菌名', '汚染濃度_logCFU/g', '食品名', '食品詳細']]
            df_bacteria_counts.columns = ['調査年', '細菌名', '汚染濃度 [log CFU/g]', '食品名', '食品詳細']
            st.dataframe(df_bacteria_counts, height=calc_df_height(df_bacteria_counts), hide_index=True)

            # 汚染濃度の平均と標本標準偏差の計算
            n_bacteria_conc = len(df_bacteria_counts['汚染濃度 [log CFU/g]'])
            mean_conc = func_round(df_bacteria_counts['汚染濃度 [log CFU/g]'].mean(), ndigits=2)
            std_conc = df_bacteria_counts['汚染濃度 [log CFU/g]'].std(ddof=1)
            std_conc = func_round(std_conc, ndigits=2) if not pd.isna(std_conc) else np.nan
            # 平均と標準偏差の表示用データフレームを作成
            stats_df = pd.DataFrame({
                '平均 [log CFU/g]': [format_number(mean_conc, ndigits=2)],
                '標準偏差': [format_number(std_conc, ndigits=2)],
                'n':n_bacteria_conc
            })
            # 統計情報を表示
            st.dataframe(stats_df, hide_index=True)

        with col4:
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.hist(df_filtered['汚染濃度_logCFU/g'].astype(float), bins=range(int(df_filtered['汚染濃度_logCFU/g'].astype(float).min()), int(df_filtered['汚染濃度_logCFU/g'].astype(float).max()) + 2, 1), color='lightsalmon', edgecolor='black')
            ax2.set_xlim([0,10])
            ax2.set_xlabel('汚染濃度 [log CFU/g]', fontsize=size_label)
            ax2.set_ylabel('頻度', fontsize=size_label)
            ax2.set_title(f'汚染濃度の分布{group_title}', fontsize=size_title)
            ax2.tick_params(axis='both', which='major', labelsize=size_label)
            st.pyplot(fig2)

        # 特定の細菌のデータを取得
        df_Campylobacter_counts = df_filtered[df_filtered['細菌名'].str.contains('Campylobacter')]
        df_Listeria_counts = df_filtered[df_filtered['細菌名'].str.contains('Listeria monocytogenes')]
        df_EHEC_counts = df_filtered[df_filtered['細菌名'].str.contains('Escherichia coli')]
        df_Salmonella_counts = df_filtered[df_filtered['細菌名'].str.contains('Salmonella')]
        df_Staphylococcus_counts = df_filtered[df_filtered['細菌名'].str.contains('Staphylococcus aureus')]

        # 各細菌のデータフレームとその行数をリストに格納
        bacteria_data = [
            ('カンピロバクター', df_Campylobacter_counts),
            ('リステリア', df_Listeria_counts),
            ('腸管出血性大腸菌', df_EHEC_counts),
            ('サルモネラ', df_Salmonella_counts),
            ('黄色ブドウ球菌', df_Staphylococcus_counts)
        ]

        # 行数が多い順にソート
        bacteria_data.sort(key=lambda x: len(x[1]), reverse=True)

        # データ数が多い順に表示
        for bacteria_name, df_bacteria in bacteria_data:
            if not df_bacteria.empty:
                st.write('-----------')
                st.subheader(f'{bacteria_name}の汚染濃度{group_title}')
                col5, col6 = st.columns(2)

                with col5:
                    df_bacteria_conc = df_bacteria.loc[:, ['調査年', '細菌名', '汚染濃度_logCFU/g', '食品名', '食品詳細']]
                    df_bacteria_conc.columns = ['調査年', '細菌名', '汚染濃度 [log CFU/g]', '食品名', '食品詳細']
                    st.dataframe(df_bacteria_conc, height=calc_df_height(df_bacteria_conc), hide_index=True)

                    # 汚染濃度の平均と標本標準偏差、サンプルサイズの計算
                    n_bacteria_conc = len(df_bacteria_conc['汚染濃度 [log CFU/g]'])
                    mean_conc = func_round(df_bacteria_conc['汚染濃度 [log CFU/g]'].mean(), ndigits=2)
                    std_conc = df_bacteria_conc['汚染濃度 [log CFU/g]'].std(ddof=1)
                    std_conc = func_round(std_conc, ndigits=2) if not pd.isna(std_conc) else np.nan
                    # 平均と標準偏差の表示用データフレームを作成
                    stats_df = pd.DataFrame({
                        '平均 [log CFU/g]': [format_number(mean_conc, ndigits=2)],
                        '標準偏差': [format_number(std_conc, ndigits=2)], 
                        'n': n_bacteria_conc
                    })
                    # 統計情報を表示
                    st.dataframe(stats_df, hide_index=True)

                with col6:
                    fig3, ax3 = plt.subplots(figsize=(8, 6))
                    ax3.set_xlim([0,10])
                    ax3.hist(df_bacteria['汚染濃度_logCFU/g'].astype(float), bins=range(int(df_bacteria['汚染濃度_logCFU/g'].astype(float).min()), int(df_bacteria['汚染濃度_logCFU/g'].astype(float).max()) + 2, 1), color='lightsalmon', edgecolor='black')
                    ax3.set_xlabel('汚染濃度 [log CFU/g]', fontsize=size_label)
                    ax3.set_ylabel('頻度', fontsize=size_label)
                    ax3.set_title(f'{bacteria_name}の汚染濃度の分布{group_title}', fontsize=size_title)
                    ax3.tick_params(axis='both', which='major', labelsize=size_label)
                    st.pyplot(fig3)
        st.write('-----------')
    
    else:
        st.subheader(f'{selected_bacteria} の汚染濃度の分布')
        # 細菌ごとのデータ抽出
        df_bacteria = df_filtered[df_filtered['細菌名'] == selected_bacteria]
        
        if not df_bacteria.empty:
            col5, col6 = st.columns(2)
            
            with col5:
                # 汚染濃度データ表示
                df_bacteria_conc = df_bacteria[['調査年', '食品名', '汚染濃度_logCFU/g']]
                df_bacteria_conc.columns = ['調査年', '食品名', '汚染濃度 [log CFU/g]']
                st.dataframe(df_bacteria_conc, height=calc_df_height(df_bacteria_conc), hide_index=True)

                # 統計情報（平均・標準偏差・サンプルサイズ）
                n_bacteria_conc = len(df_bacteria_conc['汚染濃度 [log CFU/g]'])
                mean_conc = func_round(df_bacteria_conc['汚染濃度 [log CFU/g]'].mean(), ndigits=2)
                std_conc = df_bacteria_conc['汚染濃度 [log CFU/g]'].std(ddof=1)
                std_conc = func_round(std_conc, ndigits=2) if not pd.isna(std_conc) else np.nan
                
                stats_df = pd.DataFrame({
                    '平均 [log CFU/g]': [format_number(mean_conc, ndigits=2)],
                    '標準偏差': [format_number(std_conc, ndigits=2)], 
                    'n': n_bacteria_conc
                })
                st.dataframe(stats_df, hide_index=True)
            
            with col6:
                # 汚染濃度のヒストグラム
                fig3, ax3 = plt.subplots(figsize=(8, 6))
                ax3.set_xlim([0,10])
                ax3.hist(df_bacteria['汚染濃度_logCFU/g'].astype(float), bins=range(int(df_bacteria['汚染濃度_logCFU/g'].astype(float).min()), int(df_bacteria['汚染濃度_logCFU/g'].astype(float).max()) + 2, 1), color='lightsalmon', edgecolor='black')
                ax3.set_xlabel('汚染濃度 [log CFU/g]', fontsize=size_label)
                ax3.set_ylabel('頻度', fontsize=size_label)
                ax3.set_title(f'{selected_bacteria} の汚染濃度分布', fontsize=size_title)
                ax3.tick_params(axis='both', which='major', labelsize=size_label)
                st.pyplot(fig3)
    
    # 選択された食品カテゴリと食品名に該当するデータを表示
    st.subheader(f'選択された食品カテゴリと食品名に該当するデータ{group_title}')
    df_filtered_display = df_filtered.copy()
    df_filtered_display.reset_index(inplace=True, drop=True)
    df_filtered_display = df_filtered_display.loc[:, ['調査年', '食品カテゴリ', '食品名', '食品詳細', '細菌名', '細菌名_詳細', '汚染濃度_logCFU/g', '汚染濃度', '単位', '実施機関', '調査名', 'source URL', '閲覧日', '備考']]
    st.dataframe(df_filtered_display)
    st.write("*現在報告書から取得した統計処理済みの文献値（最大値・最小値・平均値など）が混在しているためグラフは参考。今後データ収集を行い分布を可視化していく")


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
        position: relative;
        padding-left: 1.4em; /* アイコン分の余白 */
    }
    .footer a::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0.15em;
        width: 1em;
        height: 1em;
        background-repeat: no-repeat;
        background-size: contain;
        /* SVG（質問マーク丸）をそのまま埋め込み。# は %23 にエスケープ */
        background-image: url("data:image/svg+xml;utf8,\
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230366d6' stroke-width='2'>\
<circle cx='12' cy='12' r='10'/>\
<path d='M9.1 9a3 3 0 1 1 5.8 0c0 2-3 2-3 4'/>\
<circle cx='12' cy='17' r='1.2'/>\
</svg>");
    }
    </style>
    <div class="footer">
        お問い合わせは
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSf2FwkiAWmr3g_50BpPAx5_87w3pwLMPRYeKwCFSfqgSJ1iTA/viewform?usp=header"
           target="_blank" rel="noopener noreferrer">こちら</a>
        から
    </div>
"""
st.markdown(contact_link, unsafe_allow_html=True)
