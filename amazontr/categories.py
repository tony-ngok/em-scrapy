import asyncio
import json
import re
from sys import argv

from pyppeteer import launch


class AmazontrCategories:
    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'
    GET_TXT_JS = '(elem) => elem.textContent'

    HEADERS = {
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

    def __init__(self, review: bool, todo: list = []) -> None:
        if review:
            try:
                with open('amazontr_categories.json', 'r', encoding='utf-8') as f_cats: 
                    self.cats_list = [cat['cat_url'] for cat in json.load(f_cats)] # 已经获得的分类页面
                    self.cats_set = set([self.get_catno(url) for url in self.cats_list]) # 不好直接用url hash（太长了，容易误查重）
            except:
                print("No cats file")
                self.cats_list = []
                self.cats_set = set()
        
            try:
                with open('amazontr_categories_errs.json', 'r', encoding='utf-8') as f_errs: # 前面的出错
                    self.todo_list = [cat['cat_url'] for cat in json.load(f_errs)]
            except:
                print("No prev errs")
                self.todo_list = []

            print(len(self.cats_list), "categorie(s)")
            print(len(self.todo_list), "url(s) to do")
        else:
            print("Start anew")
            self.cats_list = []
            self.cats_set = set()
            self.todo_list = todo

        self.errs_list = []
        self.errs_set = set()

    def get_catno(url):
        catno_match = re.findall(r'n%3A(\d+)', url)
        if catno_match:
            return catno_match[-1]

    async def start(self) -> None:
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)
    
    async def scrape(self):
        for url in self.todo_list:
            await self.visite(url)

    async def visite(self, url: str) -> None:
        resp = await self.page.goto(url, { 'waitUntil': 'networkidle2' })

        accept = await self.page.querySelector('input[id="sp-cc-accept"]')
        if accept:
            await self.page.click('input[id="sp-cc-accept"]')
            await asyncio.sleep(1)

        actual_url = self.page.url
        if '&dc' in actual_url:
            actual_url = actual_url.split('&dc')[0]
        print('\n'+actual_url)

        actual_catno = self.get_catno(actual_url)
        print(actual_catno)
        if (actual_catno in self.cats_set) or (actual_catno in self.errs_set):
            print("Duplicate")
            return

        if (resp.status >= 300):
            print("Error", resp.status)
            self.errs_list.append(actual_url)
            self.errs_set.add(actual_catno)
            print(len(self.cats_list), "categorie(s)")
            print(len(self.errs_list), "error url(s)")
            return
    
        try:
            subcats = await self.page.querySelectorAll('li.apb-browse-refinements-indent-2 > span > a, li.s-navigation-indent-2 > span > a')
            if subcats:
                subcat_links = []
                for subcat in subcats:
                    cat_name = await self.page.evaluate(self.GET_TXT_JS, (await subcat.querySelector('span')))
                    if cat_name == 'Cinsel Sağlık ve Aile Planlaması':
                        continue

                    href = await self.page.evaluate(self.GET_ATTR_JS, subcat, 'href')
                    next_url = 'https://www.amazon.com.tr'+href
                    subcat_links.append(next_url)

                print("subcat_links", subcat_links)
                for suburl in subcat_links:
                    await self.visite(suburl)
            else: # 翻到底了
                cat_url = f'https://www.amazon.com.tr/s?rh=n%3A{actual_catno}&fs=true'
                print("Add cat_url:", cat_url)
                self.cats_list.append(cat_url)

                print(len(self.cats_list), "categorie(s)")
                print(len(self.errs_list), "error url(s)")
        except Exception as e:
            print("Error:", str(e))
            self.errs_list.append(actual_url)
            self.errs_set.add(actual_catno)
            print(len(self.cats_list), "categorie(s)")
            print(len(self.errs_set), "error url(s)")


async def main():
    review = False
    if (len(argv) >= 2) and argv[1] == '--review':
        review = True

    todo_list = []
    if not review: # 从头开始
        todo_list.append('https://www.amazon.com.tr/s?rh=n%3A12466323031')
        todo_list.append('https://www.amazon.com.tr/s?rh=n%3A12466610031')

    ac = AmazontrCategories(review, todo_list)
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
