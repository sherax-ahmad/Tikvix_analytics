# scraper.py

import asyncio
import csv
import sys
from TikTokApi import TikTokApi
from TikTokApi.exceptions import NotFoundException, CaptchaException
from playwright.async_api import async_playwright

INPUT_FILE = "uploads/urls.txt"
OUTPUT_FILE = "report.csv"
MAX_RETRIES = 2

async def fetch_stats(api, url):
    for attempt in range(MAX_RETRIES):
        try:
            video = api.video(url=url)
            data = await video.info()
            stats = data.get("stats", {})
            return {
                "url": url,
                "views": stats.get("playCount", 0),
                "likes": stats.get("diggCount", 0),
                "comments": stats.get("commentCount", 0),
                "shares": stats.get("shareCount", 0),
                "error": ""
            }
        except (NotFoundException, CaptchaException) as e:
            return {"url": url, "error": str(e), "views": 0, "likes": 0, "comments": 0, "shares": 0}
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(5)
            else:
                return {"url": url, "error": str(e), "views": 0, "likes": 0, "comments": 0, "shares": 0}

async def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        async with TikTokApi() as api:
            await api.create_sessions(
                num_sessions=1,
                headless=False,
                sleep_after=2,
                starting_url="https://www.tiktok.com",
                browser="chromium",
                timeout=120_000,
                suppress_resource_load_types=["image", "media"]
            )

            results = []
            for url in urls:
                result = await fetch_stats(api, url)
                results.append(result)

            with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["url", "views", "likes", "comments", "shares", "error"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
