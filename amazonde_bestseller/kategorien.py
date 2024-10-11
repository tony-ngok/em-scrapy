import asyncio
from sys import argv

from pyppeteer import launch


class AmazondeBSKategorien:
    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'
    GET_TXT_JS = '(elem) => elem.textContent'

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.amazon.de/",
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

    def __init__(self, review: bool = False, todos: list = []) -> None:
        if review:
            try:
                with open('amazonde_bestsellers_kategorien.txt', 'r', encoding='utf-8') as f_cats:
                    # 抓取记录
                    self.cats = {}
                    for line in f_cats:
                        kat, stat = line.strip().split() 
                        self.cats[kat] = int(stat) # 0：未完成；1：已完成
            except:
                print("Keine Kategorien: Neustarten")
                self.cats = {self.get_katnr(todo): 0 for todo in todos}
        else:
            print("Neustarten")
            self.cats = {self.get_katnr(todo): 0 for todo in todos}

        self.init_count()
        self.errs = 0
            
    def init_count(self) -> None:
        '''
        数已完成（True）与未完成（False出错或None未遍历）的分类
        '''

        self.dones = 0
        self.todos = 0
        
        for _, v in self.cats.items():
            if v:
                self.dones += 1
            else:
                self.todos += 1
        
        print(f"{self.dones:_} bestehende Kategorie(n)".replace('_', '.'))
        print(f"{self.todos:_} URL(s) zu erledigen".replace('_', '.'))

    def count(self):
        print(f"{self.dones:_} bestehende Kategorie(n)".replace('_', '.'))
        print(f"{self.errs:_} Fehler".replace('_', '.'))

    def get_katnr(self, url: str):
        return url.split('/', 5)[-1]

    async def init(self) -> None:
        self.browser = await launch()
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(180000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self) -> None:
        i = 1
        for k, v in self.cats.items():
            if not v:
                k_url = 'https://www.amazon.de/gp/bestsellers/'+k
                print(f"{i:_}/{self.todos:_}".replace("_", "."), k_url)
                await self.besuchen(k_url)
                i += 1

    async def besuchen(self, k_url: str, level: int = 0):
        print('\n' + " "*level + k_url)
        kat_nr = self.get_katnr(k_url)

        try:
            if self.cats.get(kat_nr):
                print(" "*level + "Duplikat")
                self.count()
                return

            resp = await self.page.goto(k_url)
            if resp.status >= 400:
                print(" "*level + "Fehler", resp.status, "beim URL:", k_url)
                self.cats[k_url] = -1
                self.errs += 1
                self.count()
                return
            
            treeitems = await self.page.querySelectorAll('div[role="group"] > div')
            sublinks = await self.page.querySelectorAll('div[role="group"] a')
            if len(treeitems) == len(sublinks): # 子分类页面会缺少一个子分类要素
                for sublink in sublinks:
                    href = await self.page.evaluate(self.GET_ATTR_JS, sublink, 'href')
                    if '/ref' in href:
                        href = href.split('/href')[0]
                    
                    subk_url = 'https://www.amazon.de/gp/bestsellers/'+href
                    await self.besuchen(subk_url, level+1)
            else:
                print(" "*level + "Unterkategorie:", kat_nr)
                self.cats[kat_nr] = 1
                self.dones += 1
                self.count()
        except Exception as e:
            print(" "*level + "Fehler beim URL:", k_url, f"({str(e)})")
            self.cats[k_url] = -1
            self.errs += 1
            self.count()

    async def fin(self):
        await self.browser.close()

        with open('amazonde_bestsellers_kategorien.txt', 'w', encoding='utf-8') as f_cats:
            for k, v in self.cats.items():
                if v == 1:
                    f_cats.write(f"{k} 1\n")
                else:
                    f_cats.write(f"{k} 0\n")


async def main():
    review = False
    if (len(argv) >= 2) and (argv[1] == '--review'):
        review = True

    todos = [
        'https://www.amazon.de/gp/bestsellers/sports',
        'https://www.amazon.de/gp/bestsellers/toys',
        'https://www.amazon.de/gp/bestsellers/books'
    ]

    bs = AmazondeBSKategorien(review, todos)
    await bs.init()
    await bs.scrape()
    await bs.fin()


if __name__ == '__main__':
    asyncio.run(main())
