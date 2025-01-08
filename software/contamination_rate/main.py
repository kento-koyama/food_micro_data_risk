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
food_groups = df['食品カテゴリ'].unique()  # ユニークな食品カテゴリを取得
options_group = ['入力 または 選択'] + ['すべて'] + list(food_groups)  # 初期値として表示するオプションを追加
selected_group = st.sidebar.selectbox('食品カテゴリを入力/選択してください:', options_group, index=0)

# 選択された食品カテゴリに基づいて食品名を動的に変更
if selected_group not in ['入力 または 選択', 'すべて']:
    df_filtered = df[df['食品カテゴリ'] == selected_group]
elif selected_group == 'すべて':
    df_filtered = df
else:
    df_filtered = pd.DataFrame()  # 選択肢が"入力 または 選択"の場合は空のデータフレーム


# サイドバーで食品名を選択
food_names = df_filtered['食品名'].unique() if not df_filtered.empty else []  # データが空の場合、食品名リストも空にする
options_food = ['入力 または 選択'] + ['すべて'] + list(food_names)  # 初期値として表示するオプションを追加
selected_food = st.sidebar.selectbox('食品名を入力/選択してください:', options_food, index=0)

# 選択された食品名に基づいてデータをフィルタリング
if selected_food not in ['入力 または 選択', 'すべて']:
    df_filtered = df_filtered[df_filtered['食品名'] == selected_food]
elif selected_food == 'すべて':
    df_filtered = df_filtered
else:
    df_filtered = pd.DataFrame()  # 選択肢が"入力 または 選択"の場合は空のデータフレーム

# サイドバーで細菌名を選択
bacteria_names = df_filtered['細菌名'].unique() if not df_filtered.empty else []  # データが空の場合、細菌名リストも空にする
options_bacteria = ['入力 または 選択'] + ['すべて'] + list(bacteria_names)  # 初期値として表示するオプションを追加
selected_bacteria = st.sidebar.selectbox('細菌名を入力/選択してください:', options_bacteria, index=0)

# 選択された細菌名に基づいてデータをフィルタリング
if selected_bacteria not in ['入力 または 選択', 'すべて']:
    df_filtered = df_filtered[df_filtered['細菌名'] == selected_bacteria]
elif selected_bacteria == 'すべて':
    df_filtered = df_filtered
else:
    df_filtered = pd.DataFrame()  # 選択肢が"入力 または 選択"の場合は空のデータフレーム


# 細菌ごとの検体数と陽性数の合計を計算
bacteria_counts = df_filtered.groupby('細菌名').agg({'検体数': 'sum', '陽性数': 'sum'}).reset_index()

# カラム名の変更
bacteria_counts.columns = ['バクテリア名', '検体数', '陽性数']

# タイトルに選択された食品カテゴリと食品名を記載
group_title = f"（{selected_group} - {selected_food}）" if selected_group != 'すべて' and selected_food != 'すべて' else \
              f"（{selected_group}）" if selected_group != 'すべて' else "（すべての食品カテゴリと食品名）"

# サイドバイサイドのレイアウト for 検体数
col1, col2 = st.columns(2)

with col1:
    # 検体数の表の表示
    st.write(f'細菌別の食品検体数 {group_title}')
    st.dataframe(bacteria_counts[['バクテリア名', '検体数']],hide_index=True)

with col2:
    # 検体数の合計をグラフで可視化
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

# サイドバイサイドのレイアウト for 陽性割合
col3, col4 = st.columns(2)

with col3:
    # 陽性割合の表の表示
    st.write(f'細菌の陽性率 {group_title}')
    st.dataframe(bacteria_counts[['バクテリア名', '陽性率 (%)']],hide_index=True)

with col4:
    # 陽性割合をグラフで可視化
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
st.dataframe(df_filtered,hide_index=True)


st.write('-----------')

# 陽性数が1以上のデータをフィルタリングして表示
positive_df = df_filtered[df_filtered['陽性数'] >= 1]
st.write(f'陽性数が1以上のデータ {group_title}')
st.dataframe(positive_df,hide_index=True)
