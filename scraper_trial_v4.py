from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import os

# 入力ファイルパス（Excelがある場所と同じに）
input_path = os.path.join(os.path.dirname(__file__), "企業情報_cleaned.xlsx")

# 抽出用の正規表現
patterns = {
    "従業員数": re.compile(r"(従業員数|社員数)[^\d]{0,5}(\d{1,4}(?:[,，]?\d{3})*)\s*人?"),
    "資本金": re.compile(r"(資本金)[^\d]{0,5}([\d,，\.]+.*?円)"),
    "売上高": re.compile(r"(売上高)[^\d]{0,5}([\d,，\.]+.*?円)")
}

# 検索優先ページ名
priority_keywords = ["会社概要", "企業情報", "会社案内", "企業概要", "会社プロフィール"]

results = []

df = pd.read_excel(input_path)

for index, row in df.iterrows():
    company = row["企業名"]
    url = row["WebサイトURL"]
    print(f"▶️ 処理中: {company} | {url}")

    emp = cap = rev = None
    source = "エラー"

    try:
        if pd.isna(url) or not str(url).startswith("http"):
            raise ValueError("URLが無効")

        # 初期ページ取得
        res = requests.get(url, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "lxml")

        # 会社概要ページ探索
        overview_url = None
        for link in soup.find_all("a", href=True):
            link_text = str(link.get_text())
            href = link["href"]
            if any(k in link_text for k in priority_keywords):
                overview_url = requests.compat.urljoin(url, href)
                print(f"🔗 概要ページ発見: {overview_url}")
                break

        # 見つからなければトップページを使う
        if not overview_url:
            overview_url = url

        res = requests.get(overview_url, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "lxml")
        text = soup.get_text(separator="\n")

        emp_match = patterns["従業員数"].search(text)
        cap_match = patterns["資本金"].search(text)
        rev_match = patterns["売上高"].search(text)

        if emp_match or cap_match or rev_match:
            source = "HTML"
            print("✅ 情報抽出成功:", end=" ")
            if emp_match: print("従業員数", end=" ")
            if cap_match: print("資本金", end=" ")
            if rev_match: print("売上高", end=" ")
            print()
        else:
            print("⚠️ 該当情報が見つかりません")

        results.append({
            "企業名": company,
            "URL": url,
            "従業員数": emp_match.group(2) + "人" if emp_match else "",
            "資本金": cap_match.group(2) if cap_match else "",
            "売上高": rev_match.group(2) if rev_match else "",
            "取得元": source
        })

    except Exception as e:
        print(f"⚠️ エラー発生: {e}")
        results.append({
            "企業名": company,
            "URL": url,
            "従業員数": "",
            "資本金": "",
            "売上高": "",
            "取得元": "エラー"
        })

# 保存
output_path = os.path.join(os.path.dirname(__file__), "企業情報_抽出結果_v4.xlsx")
df_out = pd.DataFrame(results)
df_out.to_excel(output_path, index=False)
print(f"✅ 完了！保存先: {output_path}")