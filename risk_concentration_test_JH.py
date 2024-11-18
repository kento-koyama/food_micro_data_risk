import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
from io import BytesIO
import os

# 四捨五入で桁丸めるための関数を定義
def func_round(number, ndigits=0):
    if pd.isna(number):  # NaN チェック
        return np.nan  # NaN をそのまま返す
    p = 10 ** ndigits
    return float(int(number * p + 0.5) / p)

# 表示用フォーマット関数
def format_number(number, ndigits=0):
    formatted = f"{number:.{ndigits}f}".rstrip('0').rstrip('.')
    return formatted

def calc_df_height(df, max_rows=6, row_height=35):
    """
    指定されたデータフレームの行数に基づき、適切な高さを計算します。
    
    Parameters:
        df (pd.DataFrame): 高さを計算する対象のデータフレーム。
        max_rows (int): 表示する最大行数。デフォルトは6行。
        row_height (int): 1行あたりの高さ（ピクセル単位）。デフォルトは35。
        
    Returns:
        int: データフレームの高さ（ピクセル単位）。
    """
    rows_to_display = min(len(df), max_rows)
    return row_height * rows_to_display

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
st.title('食中毒細菌の汚染濃度の統計値')
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

# log CFU/g のみ、汚染濃度が '不検出' または '-' のものを除外
df = df[~((df['汚染濃度'] == '不検出') | (df['汚染濃度'] == '-') | (df['汚染濃度'] == np.nan))]
df = df[(df['単位'] == 'log CFU/g')|(df['単位'] == 'CFU/g')]

# グラフ用の汚染濃度列を作成し、桁丸めを適用
df['汚染濃度'] = pd.to_numeric(df['汚染濃度'], errors='coerce')  # 汚染濃度を数値に変換（エラーをNaNに設定）
df['汚染濃度_logCFU/g'] = np.where(df['単位'] == 'CFU/g', np.log10(df['汚染濃度']), df['汚染濃度'])
df['汚染濃度_logCFU/g'] = df['汚染濃度_logCFU/g'].apply(lambda x: func_round(x, ndigits=2))
df = df.iloc[:, [0,1,2,3,4,5,6,7,8,9,10,15,11,12,13,14]]

# サイドバーで食品カテゴリを選択
selected_group = st.sidebar.selectbox('食品カテゴリを選択してください:', ['すべて'] + list(df['食品カテゴリ'].unique()))

# 選択された食品カテゴリに基づいて食品名を動的に変更
if selected_group != 'すべて':
    df_filtered = df[df['食品カテゴリ'] == selected_group]
else:
    df_filtered = df

selected_food = st.sidebar.selectbox('食品名を選択してください:', ['すべて'] + list(df_filtered['食品名'].unique()))

# 選択された食品カテゴリと食品名でデータをフィルタリング
if selected_group != 'すべて':
    df_filtered = df[df['食品カテゴリ'] == selected_group]
else:
    df_filtered = df

if selected_food != 'すべて':
    df_filtered = df_filtered[df_filtered['食品名'] == selected_food]


# タイトルに選択された食品カテゴリと食品名を記載
group_title = f"（{selected_group} - {selected_food}）" if selected_group != 'すべて' and selected_food != 'すべて' else \
              f"（{selected_food}）" if selected_group == 'すべて' and selected_food != 'すべて' else \
              f"（{selected_group}）" if selected_group != 'すべて' else "（すべての食品カテゴリと食品名）"

# 細菌ごとの検体数の合計を表示
st.subheader(f'細菌ごとの検体数{group_title}')
col1, col2 = st.columns(2)

with col1:
    bacteria_samplesize = df_filtered['細菌名'].value_counts().reset_index()
    bacteria_samplesize.columns = ['細菌名', '検体数']
    st.dataframe(bacteria_samplesize, hide_index=True)
    st.write('陽性率の可視化アプリは[こちら](%s)から' % app_ratio_url)

with col2:
    fig1, ax1 = plt.subplots(figsize=(8,6))
    ax1.barh(bacteria_samplesize['細菌名'], bacteria_samplesize['検体数'], color='skyblue')
    ax1.set_xlabel('検体数', fontsize=size_label)
    ax1.set_ylabel('細菌名', fontsize=size_label)
    ax1.set_title(f'細菌ごとの検体数{group_title}', fontsize=size_title)
    ax1.tick_params(axis='both', which='major', labelsize=size_label)
    st.pyplot(fig1)

st.write('-----------')

# すべての細菌の汚染濃度を表示
st.subheader(f'すべての細菌の汚染濃度{group_title}')
col3, col4 = st.columns(2)

with col3:
    df_bacteria_counts = df_filtered.copy()
    df_bacteria_counts = df_bacteria_counts.iloc[:, [0, 8, 11, 5, 6]]
    df_bacteria_counts.columns = ['調査年', '細菌名', '汚染濃度 [log CFU/g]', '食品名', '食品詳細']
    st.dataframe(df_bacteria_counts, height=calc_df_height(df_bacteria_counts), hide_index=True)

    # 汚染濃度の平均と標本標準偏差の計算
    mean_concentration = func_round(df_bacteria_counts['汚染濃度 [log CFU/g]'].mean(), ndigits=2)
    std_concentration = func_round(df_bacteria_counts['汚染濃度 [log CFU/g]'].std(ddof=1), ndigits=2)
    # 平均と標準偏差の表示用データフレームを作成
    stats_df = pd.DataFrame({
        '平均 [log CFU/g]': [format_number(mean_concentration, ndigits=2)],
        '標準偏差': [format_number(std_concentration, ndigits=2)]
    })
    # 統計情報を表示
    st.dataframe(stats_df, hide_index=True)

with col4:
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.hist(df_filtered['汚染濃度_logCFU/g'].astype(float), bins=range(int(df_filtered['汚染濃度_logCFU/g'].astype(float).min()), int(df_filtered['汚染濃度_logCFU/g'].astype(float).max()) + 2, 1), color='lightgreen', edgecolor='black')
    ax2.set_xlim([0,10])
    ax2.set_xlabel('汚染濃度 [log CFU/g]', fontsize=size_label)
    ax2.set_ylabel('頻度', fontsize=size_label)
    ax2.set_title(f'汚染濃度の分布{group_title}', fontsize=size_title)
    ax2.tick_params(axis='both', which='major', labelsize=size_label)
    st.pyplot(fig2)

# 特定の細菌のデータを取得
df_Campylobacter_counts = df_filtered[df_filtered['細菌名'].str.contains('Campylobacter')]
df_Listeria_counts = df_filtered[df_filtered['細菌名'].str.contains('Listeria')]
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
            df_bacteria_conc = df_bacteria.iloc[:, [0, 8, 11, 5, 6]]
            df_bacteria_conc.columns = ['調査年', '細菌名', '汚染濃度 [log CFU/g]', '食品名', '食品詳細']
            st.dataframe(df_bacteria_conc, height=calc_df_height(df_bacteria_conc), hide_index=True)

            # 汚染濃度の平均と標本標準偏差の計算
            mean_conc = func_round(df_bacteria_conc['汚染濃度 [log CFU/g]'].mean(), ndigits=2)
            std_conc = func_round(df_bacteria_conc['汚染濃度 [log CFU/g]'].std(ddof=1), ndigits=2)
            # 平均と標準偏差の表示用データフレームを作成
            stats_df = pd.DataFrame({
                '平均 [log CFU/g]': [format_number(mean_conc, ndigits=2)],
                '標準偏差': [format_number(std_conc, ndigits=2)]
            })
            # 統計情報を表示
            st.dataframe(stats_df, hide_index=True)

        with col6:
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            ax3.set_xlim([0,10])
            ax3.hist(df_bacteria['汚染濃度_logCFU/g'].astype(float), bins=range(int(df_bacteria['汚染濃度_logCFU/g'].astype(float).min()), int(df_bacteria['汚染濃度_logCFU/g'].astype(float).max()) + 2, 1), color='lightgreen', edgecolor='black')
            ax3.set_xlabel('汚染濃度 [log CFU/g]', fontsize=size_label)
            ax3.set_ylabel('頻度', fontsize=size_label)
            ax3.set_title(f'{bacteria_name}の汚染濃度の分布{group_title}', fontsize=size_title)
            ax3.tick_params(axis='both', which='major', labelsize=size_label)
            st.pyplot(fig3)

# 選択された食品カテゴリと食品名に該当するデータを表示
st.write('-----------')
st.subheader(f'選択された食品カテゴリと食品名に該当するデータ{group_title}')
df_filtered.reset_index(inplace=True, drop=True)
st.dataframe(df_filtered)
st.write("*現在報告書から取得した統計処理済みの文献値（最大値・最小値・平均値など）が混在しているためグラフは参考。今後データ収集を行い分布を可視化していく")