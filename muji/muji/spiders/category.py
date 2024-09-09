from asyncio import sleep

import scrapy
from scrapy.http import HtmlResponse
from scrapy_playwright.page import PageMethod


# scrapy crawl muji_category -O muji_categories.json
class MujiCategory(scrapy.Spider):
    name = "muji_category"
    allowed_domains = ["www.muji.com"]
    start_urls = ["https://www.muji.com/jp/ja/store/cmdty/section/D00045?web_store=hmenu_D00056"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.headers,
                             meta={
                                 "playwright": True,
                                 "playwright_include_page": True,
                                 "playwright_page_methods": [
                                     PageMethod("click", "button.FilterHeading_buttonFindByCategory__8iVl6"),
                                     PageMethod("wait_for_selector", ".CategorySelectionModalInner_categoryRow__IOEhH")
                                 ]
                             },
                             callback=self.parse)

    async def parse(self, response: HtmlResponse):
        page = response.meta['playwright_page']

        cat_ax = (await page.query_selector_all('a.CategorySelectionModalInner_categoryRow__IOEhH'))[1:]
        for a in cat_ax:
            yield {
                "prod_url": 'https://www.muji.com'+(await a.get_attribute('href'))
            }

        buttons = await page.query_selector_all('button.CategorySelectionModalInner_categoryRow__IOEhH')
        for button in buttons:
            await button.click()
            await sleep(0.5)

            cat_ax = (await page.query_selector_all('a.CategorySelectionModalInner_categoryRow__IOEhH'))[1:]
            for a in cat_ax:
                yield {
                    "cat_url": 'https://www.muji.com'+(await a.get_attribute('href'))
                }
