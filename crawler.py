import requests
import json
import time
import datetime
import os
from urllib.parse import unquote
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
cid = '7650'
pages = "1"
sent_log_file = 'sent_links.json'
rs = requests.session()

def load_sent_links():
    if os.path.exists(sent_log_file):
        with open(sent_log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_sent_links(links):
    with open(sent_log_file, 'w', encoding='utf-8') as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

def send_to_discord(title, link, content):
    message = f"📢 **{title}**\n🔗 {link}\n```{content[:500]}...```"
    data = {"content": message}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print("❌ 發送失敗：", response.status_code, response.text)
    else:
        print("✅ 已發送：", title)

def request_get(uri):
    header = {'User-Agent': 'Mozilla/5.0'}
    res = rs.get(uri, headers=header)
    return res.text

def parse_notice(uri, sent_links):
    new_sent_links = sent_links[:]
    html_data = request_get(uri)
    soup = bs(html_data, 'html.parser')

    for ul in soup.findAll('ul', class_="news-content__list"):
        for li in ul.findAll('li'):
            a_tag = li.find('a')
            time_tag = li.find('span', class_='news--time')
            
            if not a_tag or not time_tag:
                continue

            title = a_tag.getText().strip()

            # 🚫 排除包含「客服」的公告
            if "客服" in title:
                print(f"🚫 略過含客服公告：{title}")
                continue

            link = "https://gvl.wasabii.com.tw/notice/" + a_tag.get('href')

            if link in sent_links:
                continue

            detail_html = request_get(link)
            soup2 = bs(detail_html, 'html.parser')
            content_div = soup2.find("div", class_="news-detail__content")
            content = content_div.getText().strip() if content_div else ""
            send_to_discord(title, link, content)
            new_sent_links.append(link)

    return new_sent_links

def start_requests():
    urls = [f'https://gvl.wasabii.com.tw/notice/NoticeList.aspx?PageNo={i}&T=0' for i in range(1, int(pages) + 1)]
    sent_links = load_sent_links()
    for url in urls:
        sent_links = parse_notice(url, sent_links)
        time.sleep(0.5)
    save_sent_links(sent_links)

if __name__ == '__main__':
    start_requests()
