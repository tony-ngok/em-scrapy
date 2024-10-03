import asyncio
import json
import re
from random import randint
from sys import argv

from pyppeteer import launch
from pyppeteer.network_manager import Response


class YahoojpProdUrls:
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

            print(len(self.prods_set), "produit(s)")
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

