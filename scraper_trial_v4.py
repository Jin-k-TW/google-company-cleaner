import sys
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 引数でファイルパスを受け取る
if len(sys.argv) > 1:
    input_path = sys.argv[1]
else:
    input_path = "企業情報_cleaned.xlsx"  # ローカルテスト用

output_path = input_path.replace(".xlsx", "_抽出結果_v4.xlsx")

# 検索キーワード
keywords = ["会社概要", "企業情報", "会社案内", "企業概要", "会社紹介"]

# 正規表現パターン
patterns = {
    "従業員数": re.compile(r"(従業員数|社員数)[\s:：]*([\d,]+)[\s]*人?"),
    "資本金": re.compile(r"(資本金)[\s:：]*([0-9,億万円]+)"),
    "売上高": re.compile(r"(売上高)[\s:：]*([0-9,億兆万円]+)")
}

# HTML取得
def get_html(url):
    try:
        res = requests.get(url, timeout=10, verify=False)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "lxml")
        return soup
    except Exception as e:
        print(f"⚠️ HTML取得失敗: {e}")
        return None

# 概要ページ探索
def find_overview_url(soup, base_url):
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"]
        text = link.get_text(strip=True)
        if any(kw in text for kw in keywords):
            if href.startswith("http"):
                return href
            elif href.startswith("/"):
                return base_url.rstrip("/") + href
            else:
                return base_url.rstrip("/") + "/" + href
    return None

# Excel読み込み
df = pd.read_excel(input_path)
results = []

# 各URLごとに処理
for index, row in df.iterrows():
    company = row["企業名"]
    url = row["URL"]
    print(f"\n▶️ 処理中: {company} | {url}")

    if not isinstance(url, str) or not url.startswith("http"):
        print("⚠️ URL形式エラー")
        results.append({
            "企業名": company, "URL": url,
            "従業員数": "", "資本金": "", "売上高": "",
            "取得元": "エラー"
        })
        continue

    soup = get_html(url)
    if not soup:
        results.append({
            "企業名": company, "URL": url,
            "従業員数": "", "資本金": "", "売上高": "",
            "取得元": "エラー"
        })
        continue

    overview_url = find_overview_url(soup, url)
    if overview_url and overview_url != url:
        print(f"🔄 概要ページ遷移: {overview_url}")
        soup = get_html(overview_url)
        if not soup:
            results.append({
                "企業名": company, "URL": url,
                "従業員数": "", "資本金": "", "売上高": "",
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

# 出力
df_out = pd.DataFrame(results)
df_out.to_excel(output_path, index=False)
print(f"\n✅ 完了！保存先: {output_path}")
