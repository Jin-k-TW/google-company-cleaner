import streamlit as st
import pandas as pd
import tempfile
import subprocess
from pathlib import Path

st.set_page_config(page_title="Google企業リスト自動整形ツール", layout="wide")

st.title("📊 Google企業リスト自動整形ツール（企業情報抽出）")
st.markdown("Excelファイルをアップロードし、企業情報（従業員数・資本金・売上高）を自動で抽出します。")

uploaded_file = st.file_uploader("企業リスト（Excelファイル）をアップロード", type=["xlsx"])

if uploaded_file is not None:
    try:
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_path = tmp.name

        st.success("✅ ファイルをアップロードしました。抽出処理を開始します...")

        # scraper_trial_v4.py を実行（ファイルパスを引数に）
        result = subprocess.run(
            ["python", "scraper_trial_v4.py", temp_path],
            capture_output=True,
            text=True
        )

        # 結果表示
        if result.returncode == 0:
            output_path = Path(temp_path).with_name("企業情報_抽出結果.xlsx")
            if output_path.exists():
                df_result = pd.read_excel(output_path)
                st.success("✅ 抽出完了！結果を下記に表示します。")
                st.dataframe(df_result)

                with open(output_path, "rb") as f:
                    st.download_button("⬇️ 抽出結果をダウンロード", f, file_name="企業情報_抽出結果.xlsx")
            else:
                st.error("❌ 抽出結果ファイルが見つかりませんでした。")
        else:
            st.error("❌ 抽出中にエラーが発生しました。")
            st.text(result.stderr)

    except Exception as e:
        st.error("❌ 処理中に予期しないエラーが発生しました。")
        st.exception(e)
