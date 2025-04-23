# Wasabii Discord Notifier

這是一個爬蟲程式，用來抓取 UWO 公告並推送至 Discord 頻道。

## 安裝方式

```bash
git clone https://github.com/你的帳號/wasabii-discord-notifier.git
cd wasabii-discord-notifier
pip install -r requirements.txt
```

## 設定 Webhook

在專案根目錄建立 `.env` 檔案，內容如下：

```
DISCORD_WEBHOOK=https://discord.com/api/webhooks/你的webhook網址
```

## 執行方式

```bash
python crawler.py
```

你也可以用 cron 或排程工具定期執行此程式。
