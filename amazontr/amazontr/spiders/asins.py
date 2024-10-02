import asyncio
import json
import re

import scrapy
from scrapy.http import HtmlResponse
from scrapy_playwright.page import PageMethod


# scrapy crawl amazontr_asins -O amazontr_asins.json
class AmazontrAsins(scrapy.Spider):
    name = "amazontr_asins"
    allowed_domains = ["www.amazon.com.tr"]
    start_urls = []
    asins = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            with open('amazontr_categories.json', 'r', encoding='utf-8') as f_cats:
                self.start_urls = [cat['cat_url'] for cat in json.load(f_cats)]
        except:
            pass
        print("Total", len(self.start_urls), "categorie(s)")

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.amazon.com.tr/",
            "Sec-CH-UA": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }

    def start_requests(self):
        for n, url in enumerate(self.start_urls, start=1):
            yield scrapy.Request(url, headers=self.headers,
                                 meta={
                                        'cat_no': n,
                                        'cat_url': url,
                                        # 'actual_page': 1,
                                        "playwright": True,
                                        "playwright_include_page": True,
                                        "playwright_page_methods": [
                                            PageMethod("wait_for_selector", 'div[data-cy="title-recipe"]')
                                        ]
                                     },
                                callback=self.parse)

    def get_asin(self, url):
        asin_match = re.findall(r'/dp/(\w+)', url)
        if asin_match:
            return asin_match[0]

    async def parse(self, response: HtmlResponse):
        cat_no = response.meta['cat_no']
        page = response.meta['playwright_page']
        cat_url = response.meta['cat_url']

        i = 1
        asins = 0
        while True:
            print(cat_no, cat_url, f"page={i}")
            if (await page.query_selector('input[id="sp-cc-accept"]')):
                await page.click('input[id="sp-cc-accept"]')
                await asyncio.sleep(1)

            prod_cards = await page.query_selector_all('div[data-cy="title-recipe"]')
            for pc in prod_cards:
                if await pc.query_selector(':scope a.puis-sponsored-label-text'):
                    continue

                pc_a = await pc.query_selector(':scope h2 > a')
                href = await pc_a.get_attribute('href')
                asin = self.get_asin(href)
                if asin not in self.asins:
                    asins += 1
                    yield { 'asin': asin }
            
            if await page.query_selector('a.s-pagination-next'):
                i += 1
                await page.goto(cat_url+f'&page={i}')
            else:
                break
        
        await page.close()
        print(cat_no, cat_url, f"done: asins={asins}")
