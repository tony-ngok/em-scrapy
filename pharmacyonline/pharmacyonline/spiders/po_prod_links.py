import json
from asyncio import run, sleep
import os
from random import uniform

from pyppeteer import launch
from pyppeteer.network_manager import Response


class PoProdLinks:
    """
    分类内商品链接为JavaScript生成，故考虑用pyppeteer或Scrapy+Playwright抓取
    """

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
        "Referer": "https://www.pharmacyonline.com.au/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    def __init__(self) -> None:
        self.prod_link = ""
        self.contents = None
        self.max_page = 1

    async def start(self) -> None:
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        await self.page.setViewport({ 'width': 1366, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)
    
    async def goto_cat(self, cat: str) -> None:
        self.cat = cat
        def handle_response(response: Response):
            if '/cs/v2/search' in response.url and response.headers.get('content-type') and 'json' in response.headers['content-type']:
                self.contents = response
        self.page.on('response', handle_response)

        return await self.page.goto(cat, { 'waitUntil': 'networkidle2' })

    async def scrape_cats(self):
        cont_json = await self.contents.json()
        meta = cont_json['queryResults'][0]['meta']
        self.max_page = -(meta['totalResultsFound'] // -12)

        if self.max_page > 1:
            await self.goto_cat(self.cat+f'?Page={self.max_page}')
            cont_json = await self.contents.json()
            meta = cont_json['queryResults'][0]['meta']

        recs = cont_json['queryResults'][0]['records']
        for i, rec in enumerate(recs, start=1):
            yield rec['url']

async def main():
    grandparent_directory = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
    file_path_in = os.path.join(grandparent_directory, 'po_cats.json')
    file_path_out = os.path.join(grandparent_directory, 'po_prod_links.json')

    ppl = PoProdLinks()
    await ppl.start()
    with open(file_path_in, 'r') as f_in, open(file_path_out, 'w') as f_out:
        for i, l in enumerate(f_in):
            print(i, l)
            try:
                cat_url = json.loads(l.strip()[:-1])['cat_link']
                await ppl.goto_cat(cat_url)
                async for l in ppl.scrape_cats():
                    f_out.write(f'{{"prod_url": "{l}"}},\n')
            except:
                continue
            
            await sleep(uniform(0.5, 1.5))
    
    await ppl.browser.close()

if __name__ == '__main__':
    run(main())
