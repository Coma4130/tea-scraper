import feedparser
import pandas as pd
import datetime
import urllib.parse

def get_tea_topics():
    # 検索キーワードを「茶 研究」に設定
    keyword = "茶 研究"
    # キーワードをURL用に安全な文字列（エンコード）に変換
    encoded_keyword = urllib.parse.quote(keyword)
    
    # GoogleニュースのRSS URL（スペース問題を回避した形式）
    url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ja&gl=JP&ceid=JP:ja"
    
    # ニュースを取得
    feed = feedparser.parse(url)
    
    topics = []
    for entry in feed.entries:
        topics.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })
    
    # データフレームに変換
    df = pd.DataFrame(topics)
    
    # 現在の日付を取得してファイル名に含める、または上書き保存
    if not df.empty:
        df.to_csv("tea_topics.csv", index=False, encoding="utf-8-sig")
        print("CSVファイルを作成しました。")
    else:
        print("新しいトピックは見つかりませんでした。")

if __name__ == "__main__":
    get_tea_topics()
