import asyncio
import json
import re
from math import ceil
from random import randint, shuffle
from sys import argv

from pyppeteer import launch
from pyppeteer.network_manager import Response


class YahoojpProdUrls:
    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'
    GET_TXT_JS = '(elem) => elem.textContent'
    SCROLL_JS = 'window.scrollBy(0, document.body.scrollHeight)'

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7",
        "dnt": "1",
        "priority": "u=0, i",
        "referer": "https://shopping.yahoo.co.jp/category/2501/recommend?sc_i=shp_pc_top_cate_menu_cosm_and_frag:2501:rcmd",
        "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-arch": '"x86"',
        "sec-ch-ua-full-version-list": '"Microsoft Edge";v="129.0.2792.65", "Not=A?Brand";v="8.0.0.0", "Chromium";v="129.0.6668.71"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-platform-version": '"10.0.0"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
    }

    def __init__(self, resume: bool = False, todo: list = []) -> None:
        if resume: # 断点续传模式（主要为调试查错用）
            try:
                with open('yahoojp_prods_urls.json', 'r', encoding='utf-8') as f_errs: 
                    self.prods_list = [url for url in json.load(f_errs)] # 已经获得的分类页面
                    self.prods_set = set([self.get_prod_id(url) for url in self.prods_list])
            except:
                print("No cats file")
                self.prods_list = []
                self.prods_set = set()
            
            try:
                with open('yahoojp_prods_urls_errs.json', 'r', encoding='utf-8') as f_errs: 
                    self.todo_list = [(err[0], err[1]) for err in json.load(f_errs)] # 积累之前出错的URL
            except:
                print("No prev errors")
                self.todo_list = []

            print(f"{len(self.prods_set):_} produit(s) url(s)".replace("_", "."))
            print(f"{len(self.todo_list):_} url(s) to do".replace("_", "."))
        else:
            print("Start anew")
            self.prods_list = []
            self.prods_set = set()
            self.todo_list = todo
        
        self.errs_list = []
        self.errs_set = set()
    
    def get_cat_id(self, url: str):
        return url.split('/')[-2]

    def get_prod_id(self, url: str):
        prod_id = url.split('/')[-1]
        if (prod_id.endswith('.html')):
            prod_id = prod_id[:-5]
        return prod_id

    async def start(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(300000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self):
        for url in self.todo_list:
            try:
                resp = await self.page.goto(url)
                await self.visite(url, resp)
            except Exception as e:
                print("Error:", str(e))

                cat_id = self.get_cat_id(url)
                if cat_id not in self.errs_set:
                    self.errs_list.append(url)
                    self.errs_set.add(cat_id)

                print(f"{len(self.prods_set):_} produit(s) url(s)".replace("_", "."))
                print(f"{len(self.errs_set):_} error url(s)".replace("_", "."))

    async def visite(self, url: str, resp: Response, pages: list = [], i: int = -1) -> None:
        print()
        url_b = url
        if (pages and (i >= 0)):
            print(pages, f"i={i}")
            url_b += f'?b={pages[i]}'
        print(url_b)
        
        try:
            if resp.status >= 300:
                raise Exception(f"Error {resp.status}")
            
            # 取得最大可以翻的页
            if not (pages and (i >= 0)):
                total_sel = await self.page.querySelector('p.SearchResultsDisplayOptions_SearchResultsDisplayOptions__count__iOx2s')
                total_txt = (await self.page.evaluate(self.GET_TXT_JS, total_sel)).strip().replace(',', '').replace('件', '')
                max_items = min(int(total_txt), 1500)
                print(f"Max {max_items:_} item(s)".replace('_', '.'))

                if max_items > 30:
                    pages = list(range(31, max_items, 30))
                    shuffle(pages)
                    print(pages)

            raw_results = await self.page.querySelectorAll('div.SearchResult_SearchResult__imageContainerMain__nP_A2')
            results = [(await rr.querySelector(':scope a')) for rr in raw_results if not (await rr.querySelector('p.SearchResult_SearchResult__itemMatch__iOdUC'))]
            print(len(results), "result(s) on page")

            for r in results:
                href = await self.page.evaluate(self.GET_ATTR_JS, r, 'href')

                href = href.split('?')[0]
                if href.endswith('/'):
                    href = href[:-1]

                prod_id = self.get_prod_id(href)
                if prod_id not in self.prods_set:
                    self.prods_set.add(prod_id)
                    self.prods_list.append(href)
            
            print(f"{len(self.prods_set):_} produit(s) url(s)".replace("_", "."))
            print(f"{len(self.errs_set):_} error url(s)".replace("_", "."))
            await asyncio.sleep(randint(3000, 5000)/1000.0)

            i += 1
            if i < len(pages):
                resp = await self.page.goto(url+f'?b={pages[i]}')
                await self.visite(url, resp, pages, i)
        except Exception as e:
            print("Error:", str(e))

            cat_id = self.get_cat_id(url_b)
            if cat_id not in self.errs_set:
                self.errs_list.append(url_b)
                self.errs_set.add(cat_id)

            print(f"{len(self.prods_set):_} produit(s) url(s)".replace("_", "."))
            print(f"{len(self.errs_set):_} error url(s)".replace("_", "."))
            return


async def main():
    review = False
    if (len(argv) >= 2) and argv[1] == '--review':
        review = True

    todo_list = []
    if not review: # 从头开始
        with open('yahoojp_categories.json', 'r', encoding='utf-8') as f_cats:
            todo_list = [cat for cat in json.load(f_cats)]

    ac = YahoojpProdUrls(review, todo_list)
    await ac.start()
    await ac.scrape()
    await ac.browser.close()

    with open('yahoojp_prods_urls.json', 'w') as f:
        f.write('[\n')
        f.write(',\n'.join([f'"{url}"' for url in ac.prods_list]))
        f.write('\n]')
    
    with open('yahoojp_prods_urls_errs.json', 'w') as f:
        f.write('[\n')
        f.write(',\n'.join([f'"{url}"' for url in ac.errs_list]))
        f.write('\n]')


if __name__ == '__main__':
    asyncio.run(main())
