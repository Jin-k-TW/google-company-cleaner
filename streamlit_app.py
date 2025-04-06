import streamlit as st
import pandas as pd
import tempfile
import os
import subprocess

st.set_page_config(page_title="Google企業リスト自動整形ツール", layout="wide")

st.title("📊 Google企業リスト自動整形ツール（企業情報抽出）")
st.markdown("Excelファイルをアップロードし、企業情報（従業員数・資本金・売上高）を自動で抽出します。")

uploaded_file = st.file_uploader("企業リスト（Excelファイル）をアップロード", type=["xlsx"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(uploaded_file.read())
        input_path = tmp.name

    # scraper_trial_v4.py を実行
    output_path = os.path.join(os.path.dirname(input_path), "企業情報_抽出結果_v4.xlsx")
    command = f"python scraper_trial_v4.py {input_path} {output_path}"

    try:
        subprocess.run(command, shell=True, check=True)
        st.success("✅ 抽出が完了しました！")
        with open(output_path, "rb") as f:
            st.download_button("📥 結果をダウンロード", f, file_name="企業情報_抽出結果_v4.xlsx")

    except subprocess.CalledProcessError:
        st.error("❌ 抽出中にエラーが発生しました。コードやファイル内容をご確認ください。")
