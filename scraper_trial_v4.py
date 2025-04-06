# scraper_trial_v4.py

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def run_scraper_from_dataframe(uploaded_file):
    df = pd.read_excel(uploaded_file)

    # 正規表現パターン定義
    patterns = {
        "従業員数": re.compile(r"従業員[数員]\s*[:：]?\s*([\d,]+)\s*人"),
        "資本金": re.compile(r"資本金\s*[:：]?\s*([\d,]+)\s*(百万円|万円|円)?"),
        "売上高": re.compile(r"売上高\s*[:：]?\s*([\d,]+)\s*(百万円|万円|億円|円)?")
    }

    results = []

    for _, row in df.iterrows():
        company = row.get("企業名", "")
        url = row.get("URL", "")

        if not isinstance(url, str) or not url.startswith("http"):
            results.append({
                "企業名": company,
                "URL": url,
                "従業員数": "",
                "資本金": "",
                "売上高": "",
                "取得元": "エラー"
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
                "従業員数": emp.group(1) + "人" if emp else "",
                "資本金": cap.group(1) + (cap.group(2) or "") if cap else "",
                "売上高": rev.group(1) + (rev.group(2) or "") if rev else "",
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
