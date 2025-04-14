import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
from io import BytesIO
import os
import re

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


def format_bacteria_name(name):
    """
    細菌名を学名に応じて斜体のLaTeX形式に変換する。
    - Escherichia coli O157 → Escherichia coli を斜体、O157は通常
    - Salmonella spp. → Salmonella のみ斜体
    - Listeria monocytogenes → 全部斜体
    """
    if pd.isna(name):
        return name

    # 正規表現で属名と種小名を抽出
    match = re.match(r'^([A-Z][a-z]+)\s+([a-z]+)(.*)$', name)  # Ex: Escherichia coli O157
    spp_match = re.match(r'^([A-Z][a-z]+)\s+(spp?\.)$', name)  # Ex: Salmonella spp.

    if spp_match:
        genus, spp = spp_match.groups()
        return rf"$\it{{{genus}}}$ {spp}"
    elif match:
        genus, species, rest = match.groups()
        return rf"$\it{{{genus} {species}}}${rest}"
    else:
        # 属名だけある場合や、それ以外のケース
        return rf"$\it{{{name}}}$"


# ページの設定
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# CSVファイルのパス（適宜変更してください）
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E6%BF%83%E5%BA%A6.csv"
csv_url_gui = "https://github.com/kento-koyama/food_micro_data_risk/blob/main/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E6%BF%83%E5%BA%A6.csv"

# 汚染率の可視化アプリURL
app_ratio_url = "https://m7gk8u5qjmoysfsmf5kgqk.streamlit.app/"

# フォントファイルのパスを設定
font_path = 'NotoSansCJKjp-Regular.otf'

# 図のフォントサイズを一括で設定
size_label = 18
size_title = 20



# Streamlit のアプリケーション
st.write('### 食中毒細菌の汚染濃度の統計値')
st.write("[食中毒細菌汚染実態_汚染濃度.csv](%s)の可視化です。" % csv_url_gui)
st.write('各表をcsvファイルとしてダウンロードできます。')
st.write('-----------')

# サイドバーにタイトルを追加
st.sidebar.title("検索")

# フォントの設定
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

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
df['細菌名_表示'] = df['細菌名'].apply(format_bacteria_name)
# 細菌名マッピング（元の名前 <-> 表示名）
bacteria_display_map = dict(zip(df['細菌名_表示'], df['細菌名']))
bacteria_inverse_map = {v: k for k, v in bacteria_display_map.items()}


df = df.iloc[:, [0,1,2,3,4,5,6,7,8,17,9,10,16,15,11,12,13,14]]

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
selected_bacteria_display = st.sidebar.selectbox(
    '細菌名を入力 または 選択してください:',
    bacteria_names_filtered,
    format_func=lambda x: "" if x == "" else x,
    key="bacteria_selected"
)

# 選択された斜体表記から元の細菌名に変換
selected_bacteria = bacteria_display_map.get(selected_bacteria_display, selected_bacteria_display)

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
            bacteria_samplesize = df_filtered['細菌名_表示'].value_counts().reset_index()
            bacteria_samplesize.columns = ['細菌名', '検体数']
            st.dataframe(bacteria_samplesize, hide_index=True)

        with col2:
            fig1, ax1 = plt.subplots(figsize=(8,6))
            ax1.barh(bacteria_samplesize['細菌名_表示'], bacteria_samplesize['検体数'], color='skyblue')
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
            df_bacteria_counts = df_bacteria_counts.iloc[:, [0, 8, 12, 5, 6]]
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

        # 各細菌のデータフレームとその行数をリストに格納
        bacteria_data = [
            ('カンピロバクター', df_Campylobacter_counts),
            ('リステリア', df_Listeria_counts),
            ('腸管出血性大腸菌', df_EHEC_counts),
            ('サルモネラ', df_Salmonella_counts)
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
                    df_bacteria_conc = df_bacteria.iloc[:, [0, 8, 12, 5, 6]]
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
    df_filtered.reset_index(inplace=True, drop=True)
    st.dataframe(df_filtered)
    st.write("*現在報告書から取得した統計処理済みの文献値（最大値・最小値・平均値など）が混在しているためグラフは参考。今後データ収集を行い分布を可視化していく")


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
