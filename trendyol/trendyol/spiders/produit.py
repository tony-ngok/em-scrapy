import asyncio
import json
import re
from datetime import datetime

import requests
import scrapy
from scrapy.http import HtmlResponse
from scrapy_playwright.page import PageMethod


# scrapy crawl trendyol_produit -O trendyol_produits.json # 复写整个数据
class TrendyolProduit(scrapy.Spider):
    name = 'trendyol_produit'
    allowed_domains = ['www.trendyol.com', 'apigw.trendyol.com']
    start_urls = [
        'https://www.trendyol.com/sihhat-pharma/sihhat-aqua-beyaz-vazelin-50-ml-p-51920806',
        'https://www.trendyol.com/the-fine-organics/avustralya-nanesi-aktif-karbon-dis-beyazlatma-tozu-50g-p-762586955',
        'https://www.trendyol.com/oxvin/walker-baggy-bol-paca-2-iplik-orta-kalinlikta-uzun-esofman-alti-orijinal-kalip-p-855410436'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "fr-FR,fr;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Priority": "u=0, i",
            "Referer": "https://www.google.com.tr/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }

        exch = requests.get('https://open.er-api.com/v6/latest/USD')
        try:
            if exch.status_code in range(200, 300):
                exch_data = exch.json()
                self.exch_rate = exch_data['rates']['TRY']
                print("Get USD/TRY")
            else:
                raise Exception("Get USD/TRY: error", exch.status_code)
        except Exception as e:
            print(str(e))
            self.exch_rate = 34.234075
        finally:
            print(f"USD/TRY: {self.exch_rate}".replace('.', ','))
        
    def start_requests(self):
        for i, url in enumerate(self.start_urls, start=1):
            print(url, f"({i:_}/{len(self.start_urls):_})".replace("_", "."))

            id_match = re.findall(r'p-(\d+)$', url)
            if id_match:
                product_id = id_match[0]
                yield scrapy.Request(f'https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/{product_id}/html-content?channelId=1',
                                     headers=self.headers,
                                     meta={
                                         "url": url,
                                         "product_id": product_id,
                                     },
                                     callback=self.pre_parse)

    def pre_parse(self, response: HtmlResponse):
        url = response.meta['url']
        product_id = response.meta['product_id']

        try:
            descr_page = response.json()['result']
            yield scrapy.Request(url, headers=self.headers,
                                 meta={
                                        "url": url,
                                        "product_id": product_id,
                                        "descr_page": descr_page,
                                        "playwright": True,
                                        "playwright_include_page": True,
                                        "playwright_page_methods": [
                                            PageMethod("wait_for_selector", "div.product-detail-wrapper")
                                        ]
                                     },
                                     callback=self.parse)
        except Exception as e:
            print("Preparse error:", url, f"({str(e)})")

    async def get_json(self, page):
        scr_appl = await page.query_selector_all('script[type="application/javascript"]')

        for scr in scr_appl:
            scr_txt = await scr.text_content()
            json_match = re.findall(r'__PRODUCT_DETAIL_APP_INITIAL_STATE__=(\{.*\});', scr_txt)
            if json_match:
                return json.loads(json_match[0])

    async def get_video(self, page):
        video = None

        video_sel = await page.query_selector('div.video-player')
        if video_sel:
            video_wait1 = await asyncio.gather(
                video_sel.click(),
                page.wait_for_selector('div.gallery-video-container')
            )

            video_wait2 = await asyncio.gather(
                video_wait1[1].click(),
                page.wait_for_selector('video.video-player > source[type="video/mp4"]', state='attached') # 不用等到要素出现在视窗中
            )

            video = await video_wait2[1].get_attribute('src')
        
        return video

    async def parse(self, response: HtmlResponse):
        url = response.meta['url']
        product_id = response.meta['product_id']
        descr_page = response.meta['descr_page']
        page = response.meta['playwright_page']

        try:
            # 首次进入页面时
            accept = await page.query_selector('button#onetrust-accept-btn-handler')
            if accept:
                await asyncio.gather(
                    accept.click(),
                    page.reload()
                )
            init_butt = await page.query_selector('button.onboarding-popover__default-renderer-primary-button')
            if init_butt:
                await init_butt.click()
                await asyncio.sleep(1)
            
            prod_json = await self.get_json(page)
            print(prod_json)

            video = await self.get_video(page)

            yield {
                "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "url": url,
                "product_id": product_id,
                "description": descr_page,
                "sku": product_id,
                "videos": video,
            }
        except Exception as e:
            print("Parse error:", url, f"({str(e)})")
        finally:
            await page.close()
