# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import re
import sys

from scrapy import signals, Request
from scrapy.http import Response

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class SsgSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class SsgDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class SsgCatsErrsMiddleware:
    def __init__(self, max_tries):
        self.errs_file = "ssg_categories_errs.txt"
        self.errs = 0
        self.max_tries = max_tries

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        max_tries = crawler.settings.getint("CAT_MAX_TRIES", 10)
        s = cls(max_tries)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_exception(self, request: Request, exception: Exception, spider):
        """
        出现异常时，就写入错误
        """

        with open(self.errs_file, 'a', encoding='utf-8') as f_err:
            f_err.write(f"{request.url.split('ctgId=')[1]}\n")

        spider.logger.error(f'Request fail: {request.url} - Exception: {exception}')

        self.errs += 1
        spider.logger.info(f"Errors: {self.errs:_}".replace("_", "."))

    def process_response(self, request: Request, response: Response, spider):
        """
        如果返回错误状态，就写入错误
        """

        if response.status == 404:
            spider.logger.info(f'Categorie not found (ignored): {request.url} (Status 404)')
            return
        elif (response.status >= 400):
            try_times = request.meta.get('try_times', 1)
            spider.logger.error(f'Request fail: {request.url} (Status {response.status}) ({try_times:_}/{self.max_tries:_})'.replace("_", "."))
            spider.logger.info(response.text[:2000])

            if try_times < self.max_tries: # 允许返回非正常状态码时重试
                re_request = request.copy()
                re_request.meta['try_times'] = try_times+1
                re_request.dont_filter = True
                return re_request
            else: # 尝试超过次数限制了，记录错误，放弃
                with open(self.errs_file, 'a', encoding='utf-8') as f_err:
                    if request.url == 'https://www.ssg.com/monm/main.ssg':
                        f_err.write("monm") # 整个全分类失败
                    else:
                        f_err.write(f"{request.url.split('ctgId=')[1]}\n")

                self.errs += 1
                spider.logger.info(f"Errors: {self.errs:_}".replace("_", "."))
                return

        return response

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def spider_closed(self, spider):
        sys.exit(self.errs)


class SsgProdsIdsErrsMiddleware:
    def __init__(self, max_tries):
        self.output_file = "ssg_prods_ids.txt"
        self.errs_file = "ssg_prods_ids_errs.txt"
        self.errs = 0
        self.max_tries = max_tries

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        max_tries = crawler.settings.getint("PROD_URL_MAX_TRIES", 50)
        s = cls(max_tries)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def get_cat_no(self, url: str):
        cat_match = re.findall(r'tgId=(\d+)', url)
        if cat_match:
            return cat_match[0]

    def process_exception(self, request: Request, exception: Exception, spider):
        """
        出现异常时，就写入错误
        """

        with open(self.errs_file, 'a', encoding='utf-8') as f_err:
            f_err.write(f"{self.get_cat_no(request.url)}\n")

        spider.logger.error(f'Request fail: {request.url} - Exception: {exception}')

        self.errs += 1
        spider.logger.info(f"Errors: {self.errs:_}".replace("_", "."))

    def process_response(self, request: Request, response: Response, spider):
        """
        如果返回错误状态，就写入错误
        """

        if response.status == 404:
            spider.logger.info(f'Page not found (ignored): {request.url} (Status 404)')
            return
        elif (response.status >= 400):
            try_times = request.meta.get('try_times', 1)
            spider.logger.error(f'Request fail: {request.url} (Status {response.status}) ({try_times:_}/{self.max_tries:_})'.replace("_", "."))
            spider.logger.info(response.text[:3000])

            if try_times < self.max_tries: # 允许返回非正常状态码时重试
                re_request = request.copy()
                re_request.meta['try_times'] = try_times+1
                re_request.dont_filter = True
                return re_request
            else: # 尝试超过次数限制了，记录错误，放弃
                with open(self.errs_file, 'a', encoding='utf-8') as f_err:
                    f_err.write(f"{self.get_cat_no(request.url)}\n")

                self.errs += 1
                spider.logger.info(f"Errors: {self.errs:_}".replace("_", "."))
                return

        return response

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def spider_closed(self, spider):
        if spider.prods_ids:
            with open(self.output_file, 'a', encoding='utf-8') as f_output:
                for pid in spider.prods_ids:
                    f_output.write(pid+'\n')

        sys.exit(self.errs)


class SsgProdsErrsMiddleware:
    def __init__(self, max_tries):
        self.errs_file = "ssg_products_errs.txt"
        self.errs = 0
        self.max_tries = max_tries

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        max_tries = crawler.settings.getint("PROD_MAX_TRIES", 100)
        s = cls(max_tries)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def get_prod_no(self, url: str):
        cat_match = re.findall(r'temId=(\d+)', url)
        if cat_match:
            return cat_match[0]

    def process_exception(self, request: Request, exception: Exception, spider):
        """
        出现异常时，就写入错误
        """

        with open(self.errs_file, 'a', encoding='utf-8') as f_err:
            f_err.write(f"{self.get_prod_no(request.url)}\n")

        spider.logger.error(f'Request fail: {request.url} - Exception: {exception}')

        self.errs += 1
        spider.logger.info(f"Errors: {self.errs:_}".replace("_", "."))

    def process_response(self, request: Request, response: Response, spider) -> Response:
        """
        如果返回错误状态，就写入错误
        """

        if (response.status == 404):
            if ('iframePItemDtlDesc.ssg' not in request.url):
                spider.logger.info(f'Product not found (ignored): {request.url} (Status 404)')
                return
            else: # 如果描述页面返回404，则说明没有描述
                return response
        elif (response.status >= 400):
            try_times = request.meta.get('try_times', 1)
            spider.logger.error(f'Request fail: {request.url} (Status {response.status}) ({try_times:_}/{self.max_tries:_})'.replace("_", "."))
            spider.logger.info(response.text[:3000])

            if try_times < self.max_tries: # 允许返回非正常状态码时重试
                re_request = request.copy()
                re_request.meta['try_times'] = try_times+1
                re_request.dont_filter = True
                return re_request
            else: # 尝试超过次数限制了，记录错误，放弃
                with open(self.errs_file, 'a', encoding='utf-8') as f_err:
                    f_err.write(f"{self.get_prod_no(request.url)}\n")

                self.errs += 1
                spider.logger.info(f"Errors: {self.errs:_}".replace("_", "."))
                return

        return response

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def spider_closed(self, spider):
        sys.exit(self.errs)
