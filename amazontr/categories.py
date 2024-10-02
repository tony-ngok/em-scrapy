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
        self.cat_links = []
        self.err_links = []

    async def start(self) -> None:
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)
    
    async def goto_cat(self, url: str) -> None:
        resp = await self.page.goto(url)
        actual_url = resp.url
        clean_url = actual_url.split('fs=true')[0]+'fs=true'

        if (resp.status >= 300):
            print("Error", resp.status)
            self.err_links.append(clean_url)
            return
    
        subcats = await self.page.querySelectorAll('li.s-navigation-indent-2 > span > a')
        if subcats:
            subcat_links = []
            for subcat in subcats:
                cat_name = await self.page.evaluate(self.GET_TXT_JS, (await subcat.querySelector('span')))
                print(cat_name)
                if cat_name == 'Cinsel Sağlık ve Aile Planlaması':
                    continue

                href = await self.page.evaluate(self.GET_ATTR_JS, subcat, 'href')
                next_url = 'https://www.amazon.com.tr'+href
                subcat_links.append(next_url)

            print("subcat_links", subcat_links)
            for suburl in subcat_links:
                await self.goto_cat(suburl)
        else:
            self.cat_links.append({ 'cat_url': clean_url })
            print("cat_links", self.cat_links)


async def main():
    ac = AmazontrCategories()
    await ac.start()

    await ac.goto_cat('https://www.amazon.com.tr/s?i=hpc&fs=true')
    await ac.goto_cat('https://www.amazon.com.tr/s?i=beauty&fs=true')

    # await sleep(30)
    await ac.browser.close()
    
    with open('amazontr_categories1.json', 'w') as f:
        json.dump(ac.cat_links, f)

if __name__ == '__main__':
    run(main())
