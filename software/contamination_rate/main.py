import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ページの設定
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# CSVファイルのURL
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E7%8E%87.csv"

# フォントファイルのパスを設定
font_path = 'NotoSansCJKjp-Regular.otf'

# Streamlit のアプリケーション
st.title('食中毒細菌の陽性率の統計値')
st.write("[食中毒細菌汚染実態_汚染率.csv](%s)の可視化です。" % csv_url)
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

# 必要なカラムの欠損値を削除
df = df[df['検体数'].notna() & df['陽性数'].notna()]

# 細菌名を"Campylobacter spp."でまとめる
df['細菌名_詳細'] = df['細菌名']
df['細菌名'] = df['細菌名'].apply(lambda x: 'Campylobacter spp.' if 'Campylobacter' in str(x) else x)

# 初期状態の選択肢
food_groups = [""] + ["すべて"] + list(df['食品カテゴリ'].unique())
food_names = [""] + ["すべて"] + list(df['食品名'].unique())
bacteria_names = [""] + ["すべて"] + list(df['細菌名'].unique())

# サイドバーで食品カテゴリを選択
selected_group = st.sidebar.selectbox(
    '食品カテゴリを入力/選択してください:',
    food_groups,
    format_func=lambda x: "入力 または 選択" if x == "" else x,
    key="group_selected"
)

# データをフィルタリング（食品カテゴリに基づく）
df_filtered = df if selected_group == "" or selected_group == "すべて" else df[df['食品カテゴリ'] == selected_group]

# サイドバーで食品名を選択
food_names_filtered = [""] + ["すべて"] + list(df_filtered['食品名'].unique())
selected_food = st.sidebar.selectbox(
    '食品名を入力/選択してください:',
    food_names_filtered,
    format_func=lambda x: "入力 または 選択" if x == "" else x,
    key="food_selected"
)

# データをフィルタリング（食品名に基づく）
df_filtered = df_filtered if selected_food == "" or selected_food == "すべて" else df_filtered[df_filtered['食品名'] == selected_food]

# サイドバーで細菌名を選択
bacteria_names_filtered = [""] + ["すべて"] + list(df_filtered['細菌名'].unique())
selected_bacteria = st.sidebar.selectbox(
    '細菌名を入力/選択してください:',
    bacteria_names_filtered,
    format_func=lambda x: "入力 または 選択" if x == "" else x,
    key="bacteria_selected"
)

# 未選択項目を自動的に "すべて" に設定
if selected_group == "" and (selected_food != "" or selected_bacteria != ""):
    selected_group = "すべて"
if selected_food == "" and (selected_group != "" or selected_bacteria != ""):
    selected_food = "すべて"
if selected_bacteria == "" and (selected_group != "" or selected_food != ""):
    selected_bacteria = "すべて"

# データをフィルタリング（細菌名に基づく）
df_filtered = df if selected_group == "すべて" else df[df['食品カテゴリ'] == selected_group]
df_filtered = df_filtered if selected_food == "すべて" else df_filtered[df_filtered['食品名'] == selected_food]
df_filtered = df_filtered if selected_bacteria == "すべて" else df_filtered[df_filtered['細菌名'] == selected_bacteria]

# 表示条件を確認して出力制御
if selected_group == "" and selected_food == "" and selected_bacteria == "":
    st.warning("入力または選択を行ってください。")
else:
    # 細菌ごとの検体数と陽性数の合計を計算
    bacteria_counts = df_filtered.groupby('細菌名').agg({'検体数': 'sum', '陽性数': 'sum'}).reset_index()

    # カラム名の変更
    bacteria_counts.columns = ['バクテリア名', '検体数', '陽性数']

    # タイトルに選択された食品カテゴリと食品名を記載
    group_title = f"（{selected_group} - {selected_food} - {selected_bacteria}）" if selected_group != 'すべて' or selected_food != 'すべて' or selected_bacteria != 'すべて' else "（すべて）"

    # サイドバイサイドのレイアウト for 検体数
    col1, col2 = st.columns(2)

    with col1:
        st.write(f'細菌別の食品検体数 {group_title}')
        st.dataframe(bacteria_counts[['バクテリア名', '検体数']], hide_index=True)

    with col2:
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.barh(bacteria_counts['バクテリア名'], bacteria_counts['検体数'], color='skyblue')
        ax1.set_xlabel('検体数', fontsize=18)
        ax1.set_ylabel('細菌名', fontsize=18)
        ax1.set_title(f'細菌別の食品検体数 {group_title}', fontsize=20)
        ax1.tick_params(axis='both', which='major', labelsize=18)
        ax1.invert_yaxis()
        st.pyplot(fig1)

    st.write('-----------')

    # 陽性割合を計算
    bacteria_counts['陽性率 (%)'] = bacteria_counts['陽性数'] / bacteria_counts['検体数'] * 100

    col3, col4 = st.columns(2)

    with col3:
        st.write(f'細菌の陽性率 {group_title}')
        st.dataframe(bacteria_counts[['バクテリア名', '陽性率 (%)']], hide_index=True)

    with col4:
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.barh(bacteria_counts['バクテリア名'], bacteria_counts['陽性率 (%)'], color='skyblue')
        ax2.set_xlabel('陽性率 (%)', fontsize=18)
        ax2.set_ylabel('細菌名', fontsize=18)
        ax2.set_title(f'細菌の陽性率 {group_title}', fontsize=20)
        ax2.tick_params(axis='both', which='major', labelsize=18)
        ax2.invert_yaxis()
        st.pyplot(fig2)

    st.write('-----------')

    # 選択されたカテゴリと食品名に基づくデータの表示
    st.write(f'選択された食品カテゴリと食品名に該当するデータ {group_title}')
    st.dataframe(df_filtered, hide_index=True)

    st.write('-----------')

    # 陽性数が1以上のデータをフィルタリングして表示
    positive_df = df_filtered[df_filtered['陽性数'] >= 1]
    st.write(f'陽性数が1以上のデータ {group_title}')
    st.dataframe(positive_df, hide_index=True)
