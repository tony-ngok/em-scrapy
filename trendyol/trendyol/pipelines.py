# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import json
import os
import time

from itemadapter import ItemAdapter
import pymongo
from pymongo.errors import ConnectionFailure, NetworkTimeout
import scrapy
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.http import HtmlResponse

from utils.mongodb.mongo_utils import bulk_write, exists_ids, get_uos, update_sold_out


class TrendyolPipeline:
    def process_item(self, item, spider):
        return item


class MongoPipeLine3:
    """
    创建商品时，需发送商品URL本身请求以及另外2个请求，才可获得完整商品资料\n
    更新商品时，仅需发送商品URL本身请求即可
    """

    # 临时存取抓到的批量数据
    file_root = "products{}.txt"
    exists_root = "exists{}.txt"
    news_root = "news{}.txt"

    def __init__(self, uri: str, db_name: str, coll_name: str, batch_size: int, max_tries: int, days_bef: int,
                 has_vars: bool, has_recensions: bool, has_ship_fee: bool, has_ship_date: bool, headers: dict):
        self.uri = uri
        self.db_name = db_name
        self.coll_name = coll_name
        self.batch_size = batch_size
        self.max_tries = max_tries
        self.days_bef = days_bef # 数据每隔数日更新一次
        self.has_vars = has_vars
        self.has_recensions = has_recensions
        self.has_ship_fee = has_ship_fee
        self.has_ship_date = has_ship_date
        self.headers = headers

        self.records = 0 # 抓取到的数据量
        self.readys = 0 # 已经处理好准备上传的数据
        self.batch_no = 0
        self.switch = False # 开始批量处理前关闭，写入数据库后打开

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(
            uri=crawler.settings.get("MONGO_URI"),
            db_name=crawler.settings.get("MONGO_DB_NAME"),
            coll_name=crawler.settings.get("MONGO_COLL_NAME", "products"),
            batch_size=crawler.settings.getint("MONGO_BATCH_SIZE", 1000),
            max_tries=crawler.settings.getint("MONGO_MAX_TRIES", 10),
            days_bef=crawler.settings.getint("DAYS_BEF", 7),
            has_vars=crawler.settings.getbool("HAS_VARS", False),
            has_recensions=crawler.settings.getbool("HAS_RECENSIONS", False),
            has_ship_fee=crawler.settings.getbool("HAS_SHIP_FEE", False),
            has_ship_date=crawler.settings.getbool("HAS_SHIP_DATE", False), # 是否有送达日期（意味着配送日数会变）
            headers=crawler.settings.getdict("HEADERS", {})
        )

    def open_spider(self, spider: Spider):
        for i in range(1, self.max_tries+1):
            try:
                self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=60000)
                self.coll = self.client[self.db_name][self.coll_name]
                print(f"Database connexion: {self.db_name}.{self.coll_name}" )
                return
            except (ConnectionFailure, NetworkTimeout) as c_err:
                spider.logger.error(f"{repr(c_err)} ({i}/{self.max_tries})")
                time.sleep(2)

        print("MongoDB connexion fail")
        spider.crawler.engine.close_spider("MongoDB connexion fail")

    def process_batch(self, spider: Spider):
        """
        每批次中，将已存在（要更新）与不存在（要创建）的商品分开处理
        """

        print("Stage", self.batch_no+1)

        # 将批次文件读入内存
        batchfile = self.file_root.format(self.batch_no)
        items_buffer = []
        with open(batchfile, 'r', encoding='utf-8') as fb:
            for line in fb:
                if line.strip():
                    items_buffer.append(json.loads(line.strip()))
        os.remove(batchfile)

        # 该批次中已存在数据库中的商品号
        ids = [item['item']["product_id"] for item in items_buffer]
        ids_in_db = exists_ids(self.coll, ids)

        # 区分已存在及待创建的商品
        exists_file = self.exists_root.format(self.batch_no)
        news_items = []
        with open(exists_file, 'a', encoding='utf-8') as fe:
            for item in items_buffer: # 已存在的商品写入另一个文件
                if item['item']["product_id"] in ids_in_db:
                    self.readys += 1
                    json.dump(item['item'], fe, ensure_ascii=False)
                    fe.write('\n')
                else:
                    news_items.append(item)
        del items_buffer

        # 先更新已经存在的商品
        uos = get_uos(exists_file)
        if bulk_write(uos, self.coll, self.max_tries):
            spider.logger.info(f"Batch {self.batch_no+1} bulk_write (update) done")
            print(f"Stage {self.batch_no+1}: bulk_write (update) done")
            os.remove(exists_file)
        else:
            print("bulk_write (update) fail")

        # 分情况处理下一步请求（要新建的商品）
        if news_items:
            for ni in news_items:
                has_more_descr = ni["has_more_descr"]
                video_id = ni["video_id"]
                pid = ni["item"]["product_id"]
                descr_info = ni["item"]["description"]

                if has_more_descr:
                    headers = { **self.headers, "Referer": item['item']["url"] }
                    req_url2 = f"https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/{pid}/html-content?channelId=1"
                    req2 = scrapy.Request(req_url2, headers=headers,
                                          meta={ "cookiejar": item["i"] },
                                          callback=self.parse_descr_page,
                                          cb_kwargs={ "batch": self.batch_no, "item": ni["item"], "video_id": video_id, "spider": spider })
                    spider.crawler.engine.crawl(req2)
                elif video_id:
                    ni["item"]['description'] = descr_info if descr_info else None
                    headers = { **self.headers, "Referer": item['item']["url"] }
                    req_url3 = f'https://apigw.trendyol.com/discovery-web-websfxmediacenter-santral/video-content-by-id/{video_id}?channelId=1'
                    req3 = scrapy.Request(req_url3, headers=headers,
                                          meta={ "cookiejar": item["i"] },
                                          callback=self.parse_video,
                                          cb_kwargs={ "batch": self.batch_no, "item": ni["item"], "spider": spider })
                    spider.crawler.engine.crawl(req3)
                else:
                    ni["item"]['description'] = descr_info if descr_info else None
                    self.write_new(self.batch_no, ni["item"], spider)
        else:
            self.batch_no += 1

    def parse_descr_page(self, response: HtmlResponse, batch: int, item: dict, video_id: str, spider: Spider):
        i = response.meta['cookiejar']
        descr_info = item['description']

        descr_page = response.json()['result']
        descr_page = '' if not descr_page else " ".join(descr_page.replace('id="rich-content-wrapper"', 'class="trendyol-descr"').strip().split())

        description = descr_info+descr_page
        item['description'] = description if description else None

        if video_id:
            req_url3 = f'https://apigw.trendyol.com/discovery-web-websfxmediacenter-santral/video-content-by-id/{video_id}?channelId=1'
            headers = { **self.headers, 'Referer': item["url"] }
            req3 = scrapy.Request(req_url3, headers=headers,
                                  meta={ "cookiejar": i },
                                  callback=self.parse_video,
                                  cb_kwargs={ "batch": self.batch_no, "item": item, "spider": spider })
            spider.crawler.engine.crawl(req3)
        else:
            self.write_new(batch, item, spider)

    def parse_video(self, response: HtmlResponse, batch: int, item: dict, spider: Spider):
        item['videos'] = response.json().get('result', {}).get('url')
        self.write_new(batch, item, spider)

    def write_new(self, batch: int, dat: dict, spider: Spider):
        news_file = self.news_root.format(batch)
        with open(news_file, 'a', encoding='utf-8') as fn:
            self.readys += 1
            json.dump(dat, fn, ensure_ascii=False)
            fn.write('\n')

        if self.readys % self.batch_size == 0:
            self.batch_no += 1
            n_uos = get_uos(news_file)
            if bulk_write(n_uos, self.coll, self.max_tries):
                spider.logger.info(f"Batch {self.batch_no} create done")
                print(f"Stage {self.batch_no}: create done")
                os.remove(news_file)
            else:
                print("bulk_write (create) fail")

    def process_item(self, item, spider: Spider):
        if self.switch:
            self.switch = False

        dat = ItemAdapter(item).asdict()
        self.records += 1

        # 连续写1000条记录到文件
        batchfile = self.file_root.format(self.batch_no)
        with open(batchfile, 'a', encoding='utf-8') as f:
            json.dump(dat, f, ensure_ascii=False)
            f.write("\n")

        if self.records % self.batch_size == 0:
            self.process_batch(spider)
            self.switch = True

        return item

    def close_spider(self, spider: Spider):
        if not self.switch:
            self.process_batch(spider)

        if not update_sold_out(self.coll, self.max_tries, self.days_bef):
            print("Update sold out fail")

        self.client.close()
