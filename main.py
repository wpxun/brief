import os
import json
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random

import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from google import genai
from google.genai import types

FEEDS_FILE = "feeds.json"
RECIPIENT_EMAIL = "269668815@qq.com"

def strip_html(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())[:500]  # limit to 500 chars to save tokens

def fetch_recent_news():
    with open(FEEDS_FILE, 'r') as f:
        feeds = json.load(f)
    
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    
    recent_items = []
    
    for feed in feeds:
        try:
            parsed = feedparser.parse(feed['url'])
            for entry in parsed.entries:
                # Get published date
                pub_date_str = entry.get('published') or entry.get('updated')
                if not pub_date_str:
                    continue
                
                try:
                    pub_date = date_parser.parse(pub_date_str)
                    if pub_date.tzinfo is None:
                        pub_date = pub_date.replace(tzinfo=timezone.utc)
                except Exception:
                    continue
                
                if pub_date > cutoff:
                    summary = entry.get('summary') or entry.get('description', '')
                    clean_summary = strip_html(summary)
                    item = {
                        "category": feed["category"],
                        "source_type": feed["source_type"],
                        "source_name": feed["name"],
                        "title": entry.get('title', ''),
                        "url": entry.get('link', ''),
                        "content_snippet": clean_summary
                    }
                    recent_items.append(item)
        except Exception as e:
            print(f"Error fetching {feed['url']}: {e}")
            
    return recent_items

def process_with_llm(items):
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        print("Error: LLM_API_KEY environment variable not set.")
        return []
    
    client = genai.Client(api_key=api_key)
    
    # We might have too many items, limit to 150 to fit context reasonably.
    if len(items) > 150:
        items = random.sample(items, 150)
        
    prompt = """
    You are an expert tech and science news editor.
    I will provide a JSON list of recent news items collected from various RSS feeds.
    Your task is to:
    1. Select the top 20 most important and impactful news items.
    2. Rank them by importance (1 being the most important).
    3. When ranking, apply this source weighting preference: News > Forum > Video > Blog > Paper. Do NOT let academic papers dominate the list.
    4. For each selected item, translate the title into Chinese, and provide a concise, high-quality summary in Chinese.
    
    Return the result strictly as a JSON array of objects with the following keys:
    "category", "title_zh", "title_en", "summary_zh", "url", "source_name"
    
    Here is the raw news data:
    """ + json.dumps(items, ensure_ascii=False)
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        # Parse JSON
        result = json.loads(response.text)
        return result
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return []

def send_email(news_data):
    sender_email = os.environ.get("GMAIL_USER")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Email credentials not set.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"全球科技与科学日报 (Daily Tech & Science News) - {datetime.now().strftime('%Y-%m-%d')}"
    msg["From"] = sender_email
    msg["To"] = RECIPIENT_EMAIL

    # Generate HTML content
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;}
            h1 { color: #2c3e50; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 15px;}
            .subtitle { text-align: center; color: #7f8c8d; font-size: 14px; margin-bottom: 30px; }
            .news-item { margin-bottom: 30px; padding: 20px; background: #ffffff; border: 1px solid #e1e8ed; border-left: 4px solid #3498db; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
            .meta-tags { margin-bottom: 10px; }
            .category { display: inline-block; background: #e8f4f8; color: #2980b9; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;}
            .source { display: inline-block; background: #f2f2f2; color: #7f8c8d; padding: 4px 10px; border-radius: 12px; font-size: 12px; margin-left: 6px;}
            .title-zh { font-size: 18px; font-weight: bold; margin: 0 0 6px 0; color: #1a1a1a; line-height: 1.4;}
            .title-en { font-size: 14px; color: #7f8c8d; margin: 0 0 12px 0; font-style: italic;}
            .summary { font-size: 15px; margin: 0 0 15px 0; color: #444; line-height: 1.7;}
            .link { font-size: 14px; font-weight: 600; color: #3498db; text-decoration: none;}
            .link:hover { text-decoration: underline; color: #2980b9; }
            .footer { text-align: center; margin-top: 40px; font-size: 12px; color: #aaa; border-top: 1px solid #eee; padding-top: 20px;}
        </style>
    </head>
    <body>
        <h1>🌐 全球科技与科学日报</h1>
        <p class="subtitle">为您精选过去 24 小时最重要的科技新闻</p>
    """
    
    if not news_data:
        html_content += "<p style='text-align: center;'>今日没有获取到足够的新闻数据。</p>"
    else:
        for item in news_data:
            cat = item.get('category', '未知')
            src = item.get('source_name', '未知来源')
            tzh = item.get('title_zh', '')
            ten = item.get('title_en', '')
            sum_zh = item.get('summary_zh', '')
            url = item.get('url', '#')
            
            html_content += f"""
            <div class="news-item">
                <div class="meta-tags">
                    <span class="category">{cat}</span>
                    <span class="source">{src}</span>
                </div>
                <h2 class="title-zh">{tzh}</h2>
                <p class="title-en">{ten}</p>
                <p class="summary">{sum_zh}</p>
                <a href="{url}" class="link" target="_blank">阅读原文 &rarr;</a>
            </div>
            """
            
    html_content += """
        <div class="footer">
            <p>本邮件由 AI 自动聚合生成 | 运行于 GitHub Actions</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, RECIPIENT_EMAIL, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    print("Fetching recent news...")
    items = fetch_recent_news()
    print(f"Fetched {len(items)} items from the last 24 hours.")
    
    if not items:
        print("No new items found. Exiting.")
        return

    print("Processing with LLM...")
    top_news = process_with_llm(items)
    print(f"LLM returned {len(top_news)} formatted items.")
    
    if top_news:
        print("Sending email...")
        send_email(top_news)
    else:
        print("Failed to process news. Email not sent.")

if __name__ == "__main__":
    main()
