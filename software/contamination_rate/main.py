import streamlit as st
import pandas as pd
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



# ページの設定
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# フォントファイルのパスを設定
font_path = 'NotoSansCJKjp-Regular.otf'
# フォントの設定
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['text.usetex'] = False

# CSVファイルのURL
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/database/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E7%8E%87.csv"
csv_url_gui = "https://github.com/kento-koyama/food_micro_data_risk/blob/main/database/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E7%8E%87.csv"


# Streamlit のアプリケーション
st.write('### 食中毒細菌の陽性率の統計値')
st.write("[食中毒細菌汚染実態_汚染率.csv](%s)の可視化です。" % csv_url_gui)
st.write('各表をcsvファイルとしてダウンロードできます。')
st.write('-----------')


# データの読み込み
df = pd.read_csv(csv_url, encoding='utf-8-sig')

# 必要なカラムの欠損値を削除
df = df[df['検体数'].notna() & df['陽性数'].notna()]

# 細菌名を"Campylobacter spp."でまとめる
df['細菌名_詳細'] = df['細菌名']
df['細菌名'] = df['細菌名'].apply(lambda x: 'Campylobacter spp.' if 'Campylobacter' in str(x) else x)
df['細菌名_latex'] = df['細菌名'].apply(format_bacteria_name_latex)

# サイドバーにタイトルを追加
st.sidebar.write("### 検索")



# 初期状態の選択肢
food_groups = [""] + ["すべて"] + list(df['食品カテゴリ'].unique())
food_names = [""] + ["すべて"] + list(df['食品名'].unique())
bacteria_names = [""] + ["すべて"] + list(df['細菌名'].unique())
institutions = [""] + ["すべて"] + list(df['実施機関'].unique())  

# サイドバーで食品カテゴリを選択
selected_group = st.sidebar.selectbox(
    '食品カテゴリを入力 または 選択してください:',
    food_groups,
    format_func=lambda x: "" if x == "" else x,
    key="group_selected"
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

# サイドバーで細菌名を選択（細菌名 → 実データ）
bacteria_names_filtered = [""] + ["すべて"] + list(df_filtered['細菌名'].unique())
selected_bacteria = st.sidebar.selectbox(
    '細菌名を入力 または 選択してください:',
    bacteria_names_filtered,
    format_func=lambda x: "" if x == "" else x,
    key="bacteria_selected"
)
# データをフィルタリング（細菌名に基づく）
df_filtered = df_filtered if selected_bacteria in ["", "すべて"] else df_filtered[df_filtered['細菌名'] == selected_bacteria]


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

# 常に group_title (表示用タイトル) を定義
group_title = f"（{selected_group} - {selected_food} - {selected_bacteria} - {selected_institution}）" \
              if any(v != 'すべて' for v in [selected_group, selected_food, selected_bacteria, selected_institution]) else "（すべて）"

# 表示条件を確認して出力制御
if selected_group == "" and selected_food == "" and selected_bacteria == "" and selected_institution == "":
    st.info("入力または選択を行ってください。")
# データがない場合は処理を中止して警告を表示
elif df_filtered.empty:
    st.warning("該当するデータがありません。条件を変更してください。")
else:
    if selected_bacteria == "すべて":
        # 細菌ごとの集計
        bacteria_counts = df_filtered.groupby(['細菌名', '細菌名_latex']).agg({
            '検体数': 'sum', '陽性数': 'sum'
        }).reset_index()
        bacteria_counts['陽性率 (%)'] = bacteria_counts['陽性数'] / bacteria_counts['検体数'] * 100
        bacteria_counts['陽性率 (%)'] = bacteria_counts['陽性率 (%)'].apply(lambda x: func_round(x, 2))
        # 表示用ラベル
        bacteria_counts.rename(columns={
            '細菌名_latex': '表示名_LaTeX'
        }, inplace=True)

        # 検体数テーブル＆グラフ
        col1, col2 = st.columns(2)
        with col1:
            st.write(f'細菌別の食品検体数 {group_title}')
            st.dataframe(bacteria_counts[['細菌名', '検体数']], hide_index=True)
        with col2:
            fig1, ax1 = plt.subplots(figsize=(6, 6))
            ax1.barh(bacteria_counts['表示名_LaTeX'], bacteria_counts['検体数'], color='skyblue')
            ax1.set_xlabel('検体数', fontsize=18)
            ax1.set_ylabel('細菌名', fontsize=18)
            ax1.set_title(f'細菌別の食品検体数 {group_title}', fontsize=20)
            ax1.tick_params(axis='both', labelsize=14)
            ax1.invert_yaxis()
            st.pyplot(fig1)

        st.write("-----------")

        # 陽性率テーブル＆グラフ
        col3, col4 = st.columns(2)
        with col3:
            st.write(f'細菌の陽性率 {group_title}')
            st.dataframe(bacteria_counts[['細菌名', '陽性率 (%)']], hide_index=True)
        with col4:
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            ax2.barh(bacteria_counts['表示名_LaTeX'], bacteria_counts['陽性率 (%)'], color='skyblue')
            ax2.set_xlabel('陽性率 (%)', fontsize=18)
            ax2.set_ylabel('細菌名', fontsize=18)
            ax2.set_title(f'細菌の陽性率 {group_title}', fontsize=20)
            ax2.tick_params(axis='both', labelsize=14)
            ax2.invert_yaxis()
            st.pyplot(fig2)

        st.write("-----------")

    else:
        # 細菌を指定した場合：カテゴリ別に集計
        category_summary = df_filtered.groupby('食品カテゴリ').agg({'検体数': 'sum', '陽性数': 'sum'}).reset_index()
        category_summary['陽性率 (%)'] = category_summary['陽性数'] / category_summary['検体数'] * 100
        category_summary["陽性率 (%)"] = category_summary["陽性率 (%)"].apply(lambda x: func_round(x, ndigits=2))

        col5, col6 = st.columns(2)
        with col5:
            st.write(f'食品カテゴリごとの陽性率 {group_title}')
            st.dataframe(category_summary, hide_index=True)
        with col6:
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            ax3.barh(category_summary['食品カテゴリ'], category_summary['陽性率 (%)'], color='skyblue')
            ax3.set_xlabel('陽性率 (%)', fontsize=14)
            ax3.set_ylabel('食品カテゴリ', fontsize=14)
            ax3.set_title(f'食品カテゴリごとの陽性率 {group_title}', fontsize=16)
            ax3.tick_params(axis='both', which='major', labelsize=12)
            ax3.invert_yaxis()
            st.pyplot(fig3)

        st.write('-----------')

    # 選択されたカテゴリと食品名に基づくデータの表示
    st.write(f'選択された食品カテゴリと食品名に該当するデータ {group_title}')
    st.dataframe(df_filtered, hide_index=True)

    st.write('-----------')

    # 陽性数が1以上のデータをフィルタリングして表示
    positive_df = df_filtered[df_filtered['陽性数'] >= 1]
    st.write(f'陽性数が1以上のデータ {group_title}')
    st.dataframe(positive_df, hide_index=True)


language_switch_html = """
    <style>
    .language-switch {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        background-color: #f0f0f0;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .language-switch a {
        margin: 0 5px;
        text-decoration: none;
        color: #0366d6;
        font-weight: bold;
    }
    </style>
    <div class="language-switch">
        <a href="/">🇯🇵 Japanese</a> |
        <a href="/Main_eng">🇬🇧 English</a>
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

