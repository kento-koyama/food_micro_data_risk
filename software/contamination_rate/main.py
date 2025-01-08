import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ページの設定
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# CSVファイルのURL
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E7%8E%87.csv"
csv_url_gui = "https://github.com/kento-koyama/food_micro_data_risk/blob/main/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E7%8E%87.csv"

# フォントファイルのパスを設定
font_path = 'NotoSansCJKjp-Regular.otf'

# Streamlit のアプリケーション
st.title('食中毒細菌の陽性率の統計値')
st.write("[食中毒細菌汚染実態_汚染率.csv](%s)の可視化です。" % csv_url_gui)
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

# サイドバーで食品カテゴリを選択
food_groups = df['食品カテゴリ'].unique()
options_group = ['入力 または 選択'] + ['すべて'] + list(food_groups)
selected_group = st.sidebar.selectbox('食品カテゴリを入力/選択してください:', options_group, index=0)

# サイドバーで食品名を選択
food_names = df['食品名'].unique()
options_food = ['入力 または 選択'] + ['すべて'] + list(food_names)
selected_food = st.sidebar.selectbox('食品名を入力/選択してください:', options_food, index=0)

# サイドバーで細菌名を選択
bacteria_names = df['細菌名'].unique()
options_bacteria = ['入力 または 選択'] + ['すべて'] + list(bacteria_names)
selected_bacteria = st.sidebar.selectbox('細菌名を入力/選択してください:', options_bacteria, index=0)

# 入力チェック: 少なくとも1つが選択されているか
if selected_group != "入力 または 選択" or selected_food != "入力 または 選択" or selected_bacteria != "入力 または 選択":
    # 未選択の項目を "すべて" に設定
    if selected_group == "入力 または 選択":
        selected_group = "すべて"
    if selected_food == "入力 または 選択":
        selected_food = "すべて"
    if selected_bacteria == "入力 または 選択":
        selected_bacteria = "すべて"

    # フィルタリング処理
    df_filtered = df.copy()
    if selected_group != "すべて":
        df_filtered = df_filtered[df_filtered['食品カテゴリ'] == selected_group]
    if selected_food != "すべて":
        df_filtered = df_filtered[df_filtered['食品名'] == selected_food]
    if selected_bacteria != "すべて":
        df_filtered = df_filtered[df_filtered['細菌名'] == selected_bacteria]

    # 細菌ごとの検体数と陽性数の合計を計算
    bacteria_counts = df_filtered.groupby('細菌名').agg({'検体数': 'sum', '陽性数': 'sum'}).reset_index()
    bacteria_counts.columns = ['バクテリア名', '検体数', '陽性数']

    # 表やグラフを表示
    st.write(f"選択条件: 食品カテゴリ = {selected_group}, 食品名 = {selected_food}, 細菌名 = {selected_bacteria}")
    st.write('細菌ごとの検体数')
    st.dataframe(bacteria_counts)

else:
    # 入力が全く行われていない場合
    st.warning("少なくとも1つの項目を入力または選択してください。")
