import feedparser
import pandas as pd
from datetime import datetime
import os

def get_tea_topics():
    # 「茶 研究」のGoogleニュースRSS（スクレイピングより安定かつ規約に安全）
    query = "茶 研究"
    url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
    
    feed = feedparser.parse(url)
    entries = []

    for entry in feed.entries:
        entries.append({
            "published": entry.published,
            "title": entry.title,
            "link": entry.link,
            "source": entry.source.title
        })

    df_new = pd.DataFrame(entries)

    # データの保存（重複を除去して蓄積）
    file_name = "tea_topics.csv"
    if os.path.exists(file_name):
        df_old = pd.read_csv(file_name)
        df_final = pd.concat([df_old, df_new]).drop_duplicates(subset=['link'], keep='first')
    else:
        df_final = df_new

    df_final.to_csv(file_name, index=False, encoding="utf-8-sig")
    print(f"{datetime.now()}: {len(df_new)}件取得しました。")

if __name__ == "__main__":
    get_tea_topics()