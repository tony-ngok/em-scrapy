# https://shopping.yahoo.co.jp/category/2501/recommend?sc_i=shp_pc_top_cate_menu_cosm_and_frag:2501:rcmd

import asyncio
import json
import re
from random import randint
from sys import argv

from pyppeteer import launch
from pyppeteer.network_manager import Response


class YahoojpCategories:
    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7",
        "dnt": "1",
        "priority": "u=0, i",
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

    def __init__(self, resume: bool, todo: list = []) -> None:
        if resume: # 断点续传模式（主要为调试查错用）
            try:
                with open('yahoojp_categories.json', 'r', encoding='utf-8') as f_errs: 
                    self.cats_list = [url for url in json.load(f_errs)] # 已经获得的分类页面
                    self.cats_set = set([self.get_catno(url) for url in self.cats_list]) # 不好直接用url hash（太长了，容易误查重）
            except:
                print("No cats file")
                self.cats_list = []
                self.cats_set = set()
            
            try:
                with open('yahoojp_categories_errs.json', 'r', encoding='utf-8') as f_errs: 
                    self.todo_list = [url for url in json.load(f_errs)] # 积累之前出错的URL
            except:
                print("No prev errors")
                self.todo_list = []

            print(len(self.cats_set), "categorie(s)")
            print(len(self.todo_list), "url(s) to do")
        else:
            print("Start anew")
            self.cats_list = []
            self.cats_set = set()
            self.todo_list = todo
        
        self.errs_list = []
        self.errs_set = set()
    
    def get_catno(self, url: str):
        catno_match = re.findall(r'/(\d+)', url)
        if catno_match:
            return catno_match[-1]

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

    async def visite(self, url: str, resp: Response) -> None: # 由地址栏访问站点
        print('\n'+url)
        catno = self.get_catno(url)
        print(catno)
        if (catno in self.cats_set) or (catno in self.errs_set):
            print("Duplicate")
            return

        try:
            if resp.status >= 300:
                raise Exception(f"Error {resp.status}")

            subcats = (await self.page.querySelectorAll('li.style_SubCategoryList__subCategoryItem__MdKvA > a'))[1:]
            if not subcats:
                if catno not in self.cats_list: # 翻到叶分类了
                    cat_url = f'https://shopping.yahoo.co.jp/category/{catno}/list'
                    if catno not in self.cats_list:
                        self.cats_list.append(cat_url)
                        self.cats_set.add(catno)
                    print(len(self.cats_set), "categorie(s)")
                    print(len(self.errs_set), "error url(s)")
                    return
                else:
                    hrefs = [await self.page.evaluate(self.GET_ATTR_JS, sc, 'href') for sc in subcats]
                    print(hrefs)
                    for subcat, href in zip(subcats, hrefs):
                        await asyncio.sleep(randint(1000, 5000)/1000.0)
                        nav = await asyncio.gather(
                            subcat.click(),
                            self.page.waitForNavigation()
                        )
                        await self.visite(href, nav[1])
                        await self.page.goBack()

        except Exception as e:
            print("Error:", str(e))
            if catno not in self.errs_set:
                self.errs_list.append(url)
                self.errs_set.add(catno)
            print(len(self.cats_set), "categorie(s)")
            print(len(self.errs_set), "error url(s)")
            return


async def main():
    review = False
    if (len(argv) >= 2) and argv[1] == '--review':
        review = True

    todo_list = []
    if not review: # 从头开始
        todo_list.append('https://shopping.yahoo.co.jp/category/2501/recommend?sc_i=shp_pc_top_cate_menu_cosm_and_frag:2501:rcmd')

    ac = YahoojpCategories(review, todo_list)
    await ac.start()
    await ac.scrape()
    await ac.browser.close()
    
    cats_links = [{ 'cat_url': url } for url in ac.cats_list]
    with open('amazontr_categories.json', 'w') as f:
        json.dump(cats_links, f)
    
    errs_links = [{ 'cat_url': url } for url in ac.errs_list]
    with open('amazontr_categories_errs.json', 'w') as f:
        json.dump(errs_links, f)


if __name__ == '__main__':
    asyncio.run(main())
