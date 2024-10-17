import asyncio
import re
import sys

from pyppeteer import launch


class NaverHandmadeCatBrand:
    '''
    获得所有品牌（将大分类拆分成多个较小分类，以减少单个分类的请求数据量）
    '''

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7",
        "dnt": "1",
        "priority": "u=0, i",
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
        self.cats_brands = {}
        self.todos = []

        if review:
            try:
                with open('naver_handmade_cats_brands.txt', 'r', encoding='utf-8') as f_brands:
                    for line in f_brands:
                        self.cats_brands[line.strip()] = True
            except:
                print("No prev cat(s) brand(s)")
                for todo in todos:
                    self.todos.append(todo)

            try:
                with open('naver_handmade_cats_brands_errs.txt', 'r', encoding='utf-8') as f_brands_errs:
                    for line in f_brands_errs:
                        self.todos.append(line.strip())
            except:
                print("No prev err(s)")
        else:
            print("Start anew")
            for todo in todos:
                self.todos.append(todo)

        print(f"{len(self.cats_brands):_} existent cat(s) brand(s)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) to do".replace('_', '.'))

        self.dones = len(self.cats_brands)
        self.errs = 0

    def count(self):
        print(f"{self.dones:_} existent cat(s) brand(s)".replace('_', '.'))
        print(f"{self.errs:_} error(s)".replace('_', '.'))

    def get_cat_brand(self, url: str):
        cb_match = re.findall(r'BRAND-(\d+)&menu=(\d+)', url)
        if cb_match:
            br, cat = cb_match[0]
            return f'{br}_{cat}'
        else:
            raise Exception(f'No category brand match: {url}')

    async def start(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(300000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self):
        for i, todo in enumerate(self.todos, start=1):
            print(f'\n{i}/{len(self.todos)}', todo)
            await self.get_brands(todo)

    async def get_brands(self, url: str):
        try:
            resp = await self.page.goto(url)
            if resp.status >= 300:
                raise Exception(f"Status {resp.status}")

            cats_n = len(await self.page.querySelectorAll('ul[data-keyword-group-id="BRAND"] a'))
            for j in range(1, cats_n):
                cat_sel = (await self.page.querySelectorAll('ul[data-keyword-group-id="BRAND"] a'))[j]

                await asyncio.gather(
                    cat_sel.click(),
                    self.page.waitForNavigation()
                )

                cat_brand = self.get_cat_brand(self.page.url)
                if cat_brand not in self.cats_brands:
                    print("Get cat brand:", cat_brand)
                    self.cats_brands[cat_brand] = True
                    self.dones += 1
                    self.count()
        except Exception as e:
            print("ERROR:", str(e))
            self.cats_brands[url] = False
            self.errs += 1
            self.count()

    async def fin(self):
        await self.browser.close()

        with open('naver_handmade_cats_brands.txt', 'w', encoding='utf-8') as f_brands, open('naver_handmade_cats_brands_errs.txt', 'w', encoding='utf-8') as f_brands_errs:
            for k, v in self.cats_brands.items():
                if v:
                    f_brands.write(k+'\n')
                else:
                    f_brands_errs.write(k+'\n')

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
        for c in [64, 65, 66, 68, 70, 71]:
            todos.append(f"https://shopping.naver.com/living/handmade/category?menu=100048{c}")

    nh_brands = NaverHandmadeCatBrand(review, todos)
    await nh_brands.start()
    await nh_brands.scrape()
    await nh_brands.fin()


if __name__ == '__main__':
    asyncio.run(main())
