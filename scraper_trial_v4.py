import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# DataFrameから情報抽出する関数
def run_scraper_from_dataframe(df):
    patterns = {
        "従業員数": re.compile(r"(従業員数|社員数)[：: ]*([\d,]+)人"),
        "資本金": re.compile(r"(資本金)[：: ]*([\d,]+[百千億万円]*)"),
        "売上高": re.compile(r"(売上高)[：: ]*([\d,]+[百千億万円]*)")
    }

    results = []

    for _, row in df.iterrows():
        company = row.get("企業名", "")
        url = row.get("WebサイトURL", "")

        if not isinstance(url, str) or not url.startswith("http"):
            results.append({
                "企業名": company,
                "URL": url,
                "従業員数": "",
                "資本金": "",
                "売上高": "",
                "取得元": "URL不正"
            })
            continue

        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "lxml")
            text = soup.get_text(separator="\n")

            emp = patterns["従業員数"].search(text)
            cap = patterns["資本金"].search(text)
            rev = patterns["売上高"].search(text)

            results.append({
                "企業名": company,
                "URL": url,
                "従業員数": emp.group(2) if emp else "",
                "資本金": cap.group(2) if cap else "",
                "売上高": rev.group(2) if rev else "",
                "取得元": "HTML"
            })

        except Exception as e:
            results.append({
                "企業名": company,
                "URL": url,
                "従業員数": "",
                "資本金": "",
                "売上高": "",
                "取得元": "エラー"
            })

    return pd.DataFrame(results)
