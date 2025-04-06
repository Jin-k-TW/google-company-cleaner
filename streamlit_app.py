import streamlit as st
import pandas as pd
import tempfile
import os

# scraper_trial_v4.py を関数として読み込む
from scraper_trial_v4 import run_scraper_from_dataframe

st.set_page_config(page_title="Google企業リスト自動整形ツール（企業情報抽出）")

st.title("📊 Google企業リスト自動整形ツール（企業情報抽出）")
st.caption("Excelファイルをアップロードし、企業情報（従業員数・資本金・売上高）を自動で抽出します。")

uploaded_file = st.file_uploader("企業リスト（Excelファイル）をアップロード", type=["xlsx"])

if uploaded_file is not None:
    st.success("✅ ファイルをアップロードしました。抽出処理を開始します…")

    try:
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        # データ読み込み
        df = pd.read_excel(temp_path)

        # スクレイピング処理を呼び出し
        df_result = run_scraper_from_dataframe(df)

        # 結果を表示
        st.success("✅ 抽出が完了しました！")
        st.dataframe(df_result)

        # ダウンロードボタン
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name
        df_result.to_excel(output_path, index=False)
        with open(output_path, "rb") as f:
            st.download_button("📥 抽出結果をダウンロード", f, file_name="企業情報_抽出結果.xlsx")

    except Exception as e:
        st.error(f"❌ 抽出中にエラーが発生しました。\n\n{e}")
