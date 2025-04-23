import os
import json
import time
import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
sent_log_file = 'sent_links_uwo.json'

def load_sent_links():
    if os.path.exists(sent_log_file):
        with open(sent_log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_sent_links(links):
    with open(sent_log_file, 'w', encoding='utf-8') as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

def send_to_discord(title, link, content):
    max_length = 1900
    content = re.sub(r'\n{2,}', '\n', content)
    if len(content) > max_length:
        content = content[:max_length] + "\n...（內文過長已截斷）"

    embed = {
        "title": f"📢 {title}",
        "description": content,
        "url": link,
        "color": 0x00b0f4
    }

    data = {"embeds": [embed]}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print("❌ 發送失敗：", response.status_code, response.text)
    else:
        print("✅ 已發送：", title)

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

def parse_uwo_notice():
    sent_links = load_sent_links()
    new_sent_links = sent_links[:]
    driver = get_driver()
    driver.get("https://uwo.floor.line.games/kr/bbs/notice/notice_kr/1")
    time.sleep(3)  # 等待 JS 載入

    soup = BeautifulSoup(driver.page_source, "html.parser")
    notices = soup.select(".c-bbs__item")

    for notice in notices:
        a_tag = notice.find("a", href=True)
        title_tag = notice.find("p", class_="c-bbs__title")
        if not a_tag or not title_tag:
            continue

        link = "https://uwo.floor.line.games" + a_tag["href"]
        title = title_tag.text.strip()

        if link in sent_links:
            continue

        # 前往公告詳細頁
        driver.get(link)
        time.sleep(2)
        detail_soup = BeautifulSoup(driver.page_source, "html.parser")
        content_div = detail_soup.select_one(".fr-view")
        content = content_div.get_text(separator="\n").strip() if content_div else ""

        send_to_discord(title, link, content)
        new_sent_links.append(link)

        driver.back()
        time.sleep(1)

    driver.quit()
    save_sent_links(new_sent_links)

if __name__ == "__main__":
    parse_uwo_notice()
