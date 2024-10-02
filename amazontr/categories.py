import json
import os
from asyncio import run, sleep
from random import uniform

from pyppeteer import launch
from pyppeteer.page import Page


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

    def __init__(self) -> None:
        self.cats_set = set()
        self.errs_set = set()

    async def start(self) -> None:
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)
    
    async def goto_cat(self, url: str) -> None:
        resp = await self.page.goto(url, { 'waitUntil': 'networkidle2' })
        actual_url = resp.url.split('&ref=')[0]

        if (resp.status >= 300):
            print("Error", resp.status)
            self.errs_set.add(actual_url)

            print("cat_links:", len(self.cats_set), "categorie(s)")
            print(len(self.errs_set), "error url(s)")
            return
    
        subcats = await self.page.querySelectorAll('li.apb-browse-refinements-indent-2 > span > a')
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
                await self.goto_cat(suburl)
        else:
            cat_href = await self.page.evaluate(self.GET_ATTR_JS, (await self.page.querySelector('a#apb-desktop-browse-search-see-all')), 'href')
            if cat_href:
                cat_url = 'https://www.amazon.com.tr'+cat_href.split('&ref=')[0]
                self.cats_set.add(cat_url)
            else:
                print("Error: no categorie link")
                self.errs_set.add(actual_url)

            print("cat_links:", len(self.cats_set), "categorie(s)")
            print(len(self.errs_set), "error url(s)")


async def main():
    ac = AmazontrCategories()
    await ac.start()

    await ac.goto_cat('https://www.amazon.com.tr/b?node=12466323031')
    await ac.goto_cat('https://www.amazon.com.tr/s?bbn=12466610031&rh=n%3A12466610031&dc&qid=1727809363&ref=lp_13525981031_ex_n_1')

    # await sleep(30)
    await ac.browser.close()
    
    cats_links = [{ 'cat_url': url } for url in ac.cats_set]
    with open('amazontr_categories.json', 'w') as f:
        json.dump(cats_links, f)
    
    errs_links = [{ 'cat_url': url } for url in ac.errs_set]
    with open('amazontr_categories_errs.json', 'w') as f:
        json.dump(errs_links, f)

if __name__ == '__main__':
    run(main())
