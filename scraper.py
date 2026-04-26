import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import urllib.parse

def get_last_week_range():
    """過去7日間の開始日と終了日を計算"""
    today = datetime.now()
    one_week_ago = today - timedelta(days=7)
    return one_week_ago.date(), today.date()

def is_within_last_week(date_str):
    """日付文字列を判定し、過去7日以内ならTrueを返す"""
    try:
        pub_date = pd.to_datetime(date_str).date()
        start, _ = get_last_week_range()
        return pub_date >= start
    except:
        return False

def scrape_jstage():
    """J-STAGEから『茶』の新着論文を収集"""
    print("Scraping J-STAGE...")
    # 新着順で検索
    url = "https://www.jstage.jst.go.jp/result/-char/ja?globalSearchKey=茶&sortOrder=pubyear_desc"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        
        for item in soup.select(".searchlist-contents"):
            title_tag = item.select_one(".searchlist-title a")
            date_tag = item.select_one(".searchlist-additional-info")
            
            if title_tag and date_tag:
                date_text = date_tag.get_text(strip=True)
                if is_within_last_week(date_text):
                    results.append({
                        "date": date_text,
                        "title": title_tag.get_text(strip=True),
                        "url": title_tag["href"],
                        "source": "J-STAGE"
                    })
        return results
    except Exception as e:
        print(f"J-STAGE Error: {e}")
        return []

def fetch_pubmed():
    """PubMed APIを使用して過去7日間の論文を収集"""
    print("Fetching PubMed via API...")
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    try:
        # 1. 検索実行
        search_params = {
            "db": "pubmed", "term": "tea", "reldate": 7,
            "datetype": "pdat", "retmode": "json", "retmax": 10
        }
        search_res = requests.get(f"{base_url}esearch.fcgi", params=search_params).json()
        id_list = search_res.get("esearchresult", {}).get("idlist", [])
        
        if not id_list: return []

        # 2. 詳細取得
        summary_params = {"db": "pubmed", "id": ",".join(id_list), "retmode": "json"}
        summary_res = requests.get(f"{base_url}esummary.fcgi", params=summary_params).json()
        
        results = []
        for pmid in id_list:
            data = summary_res.get("result", {}).get(pmid)
            if data:
                results.append({
                    "date": data.get("pubdate"),
                    "title": data.get("title"),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "source": "PubMed"
                })
        return results
    except Exception as e:
        print(f"PubMed Error: {e}")
        return []

def scrape_google_news():
    """Google Newsから『お茶』の新着ニュースを収集"""
    print("Scraping Google News...")
    # q=茶, when:7d (過去7日間)
    query = urllib.parse.quote("お茶 when:7d")
    url = f"https://news.google.com/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        
        # Google Newsの構造に基づきタイトルとリンクを抽出
        for article in soup.select("article")[:10]: # 上位10件
            title_tag = article.select_one("h3 a")
            date_tag = article.select_one("time")
            
            if title_tag:
                link = "https://news.google.com" + title_tag["href"][1:]
                results.append({
                    "date": date_tag["datetime"] if date_tag else "Unknown",
                    "title": title_tag.get_text(strip=True),
                    "url": link,
                    "source": "Google News"
                })
        return results
    except Exception as e:
        print(f"Google News Error: {e}")
        return []

def save_to_csv(data):
    """CSVへ保存（文字化け防止のため utf-8-sig）"""
    if not data:
        print("新規データは見つかりませんでした。")
        return
    
    df = pd.DataFrame(data)
    file_name = "tea_topics.csv"
    
    if os.path.exists(file_name):
        df.to_csv(file_name, mode='a', header=False, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(file_name, index=False, encoding="utf-8-sig")
    print(f"完了: {len(data)}件のデータを '{file_name}' に追加しました。")

if __name__ == "__main__":
    all_results = []
    
    # 各サイトから収集
    all_results.extend(scrape_jstage())
    time.sleep(1) # サーバー負荷軽減
    all_results.extend(fetch_pubmed())
    time.sleep(1)
    all_results.extend(scrape_google_news())
    
    # 保存
    save_to_csv(all_results)