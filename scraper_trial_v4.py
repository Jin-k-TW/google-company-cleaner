# scraper_trial_v4.py

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def extract_company_info(uploaded_file):
    # アップロードファイルをDataFrameに読み込み
    df = pd.read_excel(uploaded_file)

    # 正規表現パターン
    patterns = {
        "従業員数": re.compile(r"従業員数[\s\u3000:\-]*([\d,]{1,5})(名)?"),
        "資本金": re.compile(r"資本金[\s\u3000:\-]*([\d,]{1,5})(万|千|百)?円"),
        "売上高": re.compile(r"売上高[\s\u3000:\-]*([\d,]{1,5})(億|万)?円")
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
                "従業員数": emp.group(1) + (emp.group(2) or "") if emp else "",
                "資本金": cap.group(1) + (cap.group(2) or "") + "円" if cap else "",
                "売上高": rev.group(1) + (rev.group(2) or "") + "円" if rev else "",
                "取得元": "HTML"
            })

        except Exception:
            results.append({
                "企業名": company,
                "URL": url,
                "従業員数": "",
                "資本金": "",
                "売上高": "",
                "取得元": "エラー"
            })

    return pd.DataFrame(results)
