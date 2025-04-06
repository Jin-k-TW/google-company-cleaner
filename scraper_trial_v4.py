import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# 正規表現パターン
patterns = {
    "従業員数": re.compile(r"(従業員数|社員数)[：:\s]*([0-9,]+)\s*人?"),
    "資本金": re.compile(r"(資本金)[：:\s]*([0-9,億万円千]+)"),
    "売上高": re.compile(r"(売上高)[：:\s]*([0-9,億万円千]+)")
}

# 会社概要ページを探す
def find_overview_url(soup, base_url):
    keywords = ["会社概要", "企業情報", "会社情報", "会社案内"]
    for link in soup.find_all("a", href=True):
        for word in keywords:
            if word in link.text:
                href = link.get("href")
                if href.startswith("http"):
                    return href
                elif href.startswith("/"):
                    return base_url.rstrip("/") + href
    return None

# HTML取得
def get_html(url):
    try:
        res = requests.get(url, timeout=10, verify=False)
        res.encoding = res.apparent_encoding
        return BeautifulSoup(res.text, "lxml")
    except Exception:
        return None

# Streamlitから呼び出せるメイン関数
def run_scraper_from_dataframe(df):
    results = []

    for index, row in df.iterrows():
        company = row.get("企業名", "")
        url = row.get("URL", "")

        print(f"▶️ 処理中: {company} | {url}")

        # URLが無効な場合スキップ
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

        soup = get_html(url)
        if not soup:
            results.append({
                "企業名": company,
                "URL": url,
                "従業員数": "",
                "資本金": "",
                "売上高": "",
                "取得元": "エラー"
            })
            continue

        # 会社概要ページを探す
        overview_url = find_overview_url(soup, url)
        if overview_url:
            soup = get_html(overview_url)
            if not soup:
                results.append({
                    "企業名": company,
                    "URL": url,
                    "従業員数": "",
                    "資本金": "",
                    "売上高": "",
                    "取得元": "エラー"
                })
                continue

        # テキスト抽出
        text = soup.get_text(separator="\n")

        emp = patterns["従業員数"].search(text)
        cap = patterns["資本金"].search(text)
        rev = patterns["売上高"].search(text)

        results.append({
            "企業名": company,
            "URL": url,
            "従業員数": emp.group(2) + "人" if emp else "",
            "資本金": cap.group(2) if cap else "",
            "売上高": rev.group(2) if rev else "",
            "取得元": "HTML"
        })

    return pd.DataFrame(results)
    
