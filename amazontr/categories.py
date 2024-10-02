import asyncio
import json
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

    def __init__(self, review: bool, todo: set = set()) -> None:
        if review:
            try:
                with open('amazontr_categories.json', 'r', encoding='utf-8') as f_cats: 
                    self.cats_set = set([cat['cat_url'] for cat in json.load(f_cats)])
            except:
                print("No cats file")
                self.cats_set = set(todo)
        
            try:
                with open('amazontr_categories_errs.json', 'r', encoding='utf-8') as f_errs: # 前面的出错
                    self.todo_set = set([cat['cat_url'] for cat in json.load(f_errs)])
            except:
                print("No prev errs")
                self.todo_set = set()

            print(len(self.cats_set), "categorie(s)")
            print(len(self.todo_set), "url(s) to do")
        else:
            print("Start anew")
            self.cats_set = set()
            self.todo_set = todo

        self.errs_set = set()

    async def start(self) -> None:
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)
    
    async def scrape(self):
        while len(self.todo_set):
            url = self.todo_set.pop()
            await self.visite(url)

    async def visite(self, url: str) -> None:
        resp = await self.page.goto(url, { 'waitUntil': 'networkidle2' })

        accept = self.page.querySelector('input[id="sp-cc-accept"]')
        if accept:
            await self.page.click('input[id="sp-cc-accept"]')
            await asyncio.sleep(1)

        actual_url = self.page.url
        if '&dc' in actual_url:
            actual_url = actual_url.split('&dc')[0]
        print('\n'+actual_url)
        if (actual_url in self.cats_set) or (actual_url in self.errs_set):
            print("Duplicate")
            return

        if (resp.status >= 300):
            print("Error", resp.status)
            self.errs_set.add(actual_url)
            print(len(self.cats_set), "categorie(s)")
            print(len(self.errs_set), "error url(s)")
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
            else:
                see_all = await self.page.querySelector('a#apb-desktop-browse-search-see-all')
                if see_all:
                    cat_href = await self.page.evaluate(self.GET_ATTR_JS, see_all, 'href')
                    if cat_href:
                        cat_url = 'https://www.amazon.com.tr'+cat_href.split('&ref=')[0]
                        self.cats_set.add(cat_url)
                    else:
                        print("Error: no categorie link")
                        self.errs_set.add(actual_url)
                else:
                    self.cats_set.add(actual_url) # 有的直接就是叶分类页面

                print(len(self.cats_set), "categorie(s)")
                print(len(self.errs_set), "error url(s)")
        except Exception as e:
            print("Error:", str(e))
            self.errs_set.add(actual_url)
            print(len(self.cats_set), "categorie(s)")
            print(len(self.errs_set), "error url(s)")


async def main():
    review = False
    if (len(argv) >= 2) and argv[1] == '--review':
        review = True

    todo = set()
    if not review: # 从头开始
        todo.add('https://www.amazon.com.tr/b?node=12466323031')
        todo.add('https://www.amazon.com.tr/s?bbn=12466610031&rh=n%3A12466610031&dc&qid=1727809363&ref=lp_13525981031_ex_n_1')

    ac = AmazontrCategories(review, todo)
    await ac.start()
    await ac.scrape()
    await ac.browser.close()
    
    cats_links = [{ 'cat_url': url } for url in ac.cats_set]
    with open('amazontr_categories.json', 'w') as f:
        json.dump(cats_links, f)
    
    errs_links = [{ 'cat_url': url } for url in ac.errs_set]
    with open('amazontr_categories_errs.json', 'w') as f:
        json.dump(errs_links, f)


if __name__ == '__main__':
    asyncio.run(main())
