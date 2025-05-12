import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Contamination Data Translator", layout="centered")


st.title("食中毒汚染データ 英語変換アプリ")
st.markdown("CSVファイルをアップロードすると英語版に変換されたCSVをダウンロードできます。")

uploaded_file = st.file_uploader("日本語のCSVファイルをアップロード（汚染率または汚染濃度）", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 修正ポイント: 辞書ファイルの絶対パス（マウントされた外部フォルダを指す）
    translation_path = Path("/app_parent/database/translation_jpn_to_eng.csv")

    if not translation_path.exists():
        st.error(f"翻訳辞書ファイルが見つかりません: {translation_path}")
    else:
        translation_df = pd.read_csv(translation_path, encoding="cp932")
        translation_dict = dict(zip(translation_df["Japanese"], translation_df["English"]))

        # カラム名の翻訳
        df.columns = [translation_dict.get(col, col) for col in df.columns]

        # 値の翻訳（可能な限り）
        df = df.replace(translation_dict)

        # ファイル名の設定
        output_name = "contamination_rate.csv" if "率" in uploaded_file.name else "concentration_of_contamination.csv"

        # ダウンロードボタン
        st.success("変換が完了しました。")
        st.download_button(
            label="英語版CSVをダウンロード",
            data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name=output_name,
            mime="text/csv"
        )
