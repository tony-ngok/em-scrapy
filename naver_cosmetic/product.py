# https://blog.naver.com/spson0153/223390335136

import asyncio
import re
import sys

from pyppeteer import launch
from pyppeteer_stealth import stealth


class NaverCosmeticProduct:
    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7",
        "dnt": "1",
        "priority": "u=0, i",
        "referer": "https://shopping.naver.com/",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
    }

    def __init__(self, review: bool = False, todos: list = []):
        self.prods_ids = {}
        self.todos = []

        if review:
            try:
                with open('naver_cosmetic_prods.json', 'r', encoding='utf-8') as f_prods_ids:
                    for line in f_prods_ids:
                        self.prods_ids[line.strip()] = True
            except:
                print("No existents product(s)")
                for todo in todos:
                    self.todos.append(todo)

            try:
                with open('naver_cosmetic_prods_errs.txt', 'r', encoding='utf-8') as f_errs:
                    for line in f_errs:
                        self.todos.append(line.strip())
            except:
                print("No prev(s) err(s)")
        else:
            print("Start anew")
            for todo in todos:
                self.todos.append(todo)

        print(f"{len(self.prods_ids):_} existent product(s)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) todo".replace('_', '.'))

        self.dones = len(self.prods_ids)
        self.errs = 0

    def count(self):
        print(f"{self.dones:_} existent product(s)".replace('_', '.'))
        print(f"{self.errs:_} URL(s) todo".replace('_', '.'))

    async def start(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(300000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self):
        for i, todo in enumerate(self.todos, start=1):
            url = 'https://shopping.naver.com/luxury/cosmetic/products/'+todo
            print(f'\n{i:_}/{len(self.todos):_}'.replace("_", "."), url)
            await self.get_prod_data(url)

    async def get_prod_data(self, url: str):
        pass

    def fin(self):
        with open('naver_cosmetic_prods.json', 'w', encoding='utf-8') as f_prods_ids, open('naver_cosmetic_prods_errs.txt', 'w', encoding='utf-8') as f_errs:
            for k, v in self.prods_ids.items():
                if v:
                    f_prods_ids.write(k+'\n')
                else:
                    f_errs.write(k+'\n')

        if self.errs:
            sys.exit(1)
        else:
            sys.exit(0)


async def main():
    review = False
    if (len(sys.argv) >= 2) and (sys.argv[1] == '--review'):
        review = True

    todos = []
    if not review:
        with open('naver_cosmetic_prods_ids.txt', 'r', encoding='utf-8') as prods_ids:
            for line in prods_ids:
                todos.append(line.strip())

    nc_recs = NaverCosmeticProduct(review, todos)
    await nc_recs.start()
    await nc_recs.scrape()
    await nc_recs.fin()


if __name__ == '__main__':
    asyncio.run(main())
