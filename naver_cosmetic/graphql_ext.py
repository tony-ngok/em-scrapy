import asyncio
from urllib.parse import unquote

from pyppeteer import launch
from pyppeteer.network_manager import Response


class NaverCosmeticGraphqlExt:
    """
    获得抓取化妆品API所需的GraphQL扩张参数（密文）
    """

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

    def __init__(self):
        self.graphql_ext = None

    async def start(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(300000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def getGraphqlHash(self):
        def handle_response(response: Response): # 监听页面发出请求，以获得密文
            if 'graphql?operationName=FetchPagedLuxuryListItems' in response.url:
                self.graphql_ext = unquote(response.url.split("&extensions=")[1])
                print("Get GraphQL extension:", self.graphql_ext)
        self.page.on('response', handle_response)

        try:
            resp = await self.page.goto('https://shopping.naver.com/luxury/cosmetic/category?optionFilters=CH_101180106')
            if resp.status >= 300:
                raise Exception(f"Status {resp.status}")
        except Exception as e:
            print("ERROR:", str(e))

    async def fin(self):
        await self.browser.close()

        if self.graphql_ext:
            with open('graphql_ext.txt', 'w', encoding='utf-8') as f:
                f.write(self.graphql_ext)
            exit(0)
        else:
            print("No GraphQL hash")
            exit(1)


async def main():
    nc_ext = NaverCosmeticGraphqlExt()
    await nc_ext.start()
    await nc_ext.getGraphqlHash()
    await nc_ext.fin()


if __name__ == '__main__':
    asyncio.run(main())
