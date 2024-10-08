import asyncio
import json
import re
from math import ceil
from random import randint
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
                    self.prods_set = set([url for url in self.prods_list]) # 不好直接用url hash（太长了，容易误查重）
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

            print(len(self.prods_set), "produit(s) url(s)")
            print(len(self.todo_list), "url(s) to do")
        else:
            print("Start anew")
            self.prods_list = []
            self.prods_set = set()
            self.todo_list = todo
        
        self.errs_list = []
        self.errs_set = set()
    
    async def start(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(300000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self):
        for url in self.todo_list:
            resp = await self.page.goto(url)
            await self.visite(url, resp)
    
    async def visite(self, url: str, resp: Response, page_no: int = 1, max_pages = None) -> None:
        print('\n'+url)
        try:
            if resp.status >= 300:
                raise Exception(f"Error {resp.status}")
            
            # 取得最大可以翻的页数
            if (max_pages is None):
                total_sel = await self.page.querySelector('p.SearchResultsDisplayOptions_SearchResultsDisplayOptions__count__iOx2s')
                total_txt = (await self.page.evaluate(self.GET_TXT_JS, total_sel)).strip().replace(',', '').replace('件', '')
                max_pages = min(ceil(int(total_txt)/30), 50)
                print("Max", max_pages, "page(s)")
            
            await self.page.waitForSelector(f'li#searchResults{page_no}')

            i = page_no
            while i <= max_pages:
                li = await self.page.querySelector(f'li#searchResults{i}')
                raw_results = await li.querySelectorAll(':scope div.SearchResult_SearchResult__imageContainerMain__nP_A2')
                results = [(await rr.querySelector(':scope a')) for rr in raw_results if not (await rr.querySelector('p.SearchResult_SearchResult__itemMatch__iOdUC'))]
                
                print('\n'+url)
                print(len(results), "result(s) on page", i)

                for r in results:
                    href = await self.page.evaluate(self.GET_ATTR_JS, r, 'href')
                    href = href.split('?')[0]

                    prod_id = href.split('/')[-1]
                    if (prod_id.endswith('.html')):
                        prod_id = prod_id[:-5]
                    
                    if prod_id not in self.prods_set:
                        self.prods_set.add(prod_id)
                        self.prods_list.append(href)
                
                print(len(self.prods_set), "categorie(s)")
                print(len(self.errs_set), "error url(s)")

                await asyncio.sleep(randint(3000, 7000)/1000.0)

                if (i >= max_pages):
                    break

                i += 1
                if ((i == 22) or (i == 43)):
                    await asyncio.gather(
                        self.page.evaluate(self.SCROLL_JS),
                        self.page.waitForSelector('button.Pager_Pager__link__xLzFo')
                    )

                    next_btn = await self.page.querySelectorAll('button.Pager_Pager__link__xLzFo')[1]
                    nav = await asyncio.gather(
                        next_btn.click(),
                        self.page.waitForNavigation()
                    )
                    await self.visite(url, nav[1], i, max_pages)
                else:
                    await asyncio.gather(
                        self.page.evaluate(self.SCROLL_JS),
                        self.page.waitForSelector(f'li#searchResults{page_no}')
                    )
        except Exception as e:
            print("Error:", str(e))
            if prod_id not in self.errs_set:
                self.errs_list.append(url)
                self.errs_set.add(prod_id)
            print(len(self.prods_set), "produit(s) url(s)")
            print(len(self.errs_set), "error url(s)")
            return


async def main():
    review = False
    if (len(argv) >= 2) and argv[1] == '--review':
        review = True

    todo_list = []
    if not review: # 从头开始
        todo_list.append('https://shopping.yahoo.co.jp/category/1840/list')

    ac = YahoojpProdUrls(review, todo_list)
    await ac.start()
    await ac.scrape()
    await ac.browser.close()

    with open('yahoojp_prods_urls.json', 'w') as f:
        f.write('[\n')
        f.write(',\n'.join(ac.prods_list))
        f.write('\n]')
    
    with open('yahoojp_prods_urls_errs.json', 'w') as f:
        f.write('[\n')
        f.write(',\n'.join(ac.errs_list))
        f.write('\n]')


if __name__ == '__main__':
    asyncio.run(main())