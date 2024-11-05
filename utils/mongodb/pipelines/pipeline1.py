import json
import os
import time

from itemadapter import ItemAdapter
import pymongo
from pymongo.errors import ConnectionFailure, NetworkTimeout
from scrapy import Spider
from scrapy.crawler import Crawler

from utils.mongodb.mongo_utils import bulk_write, get_uos, update_sold_out


class MongoPipeLine1:
    """
    Mongo管道中最简单的一种：只需发送商品URL本身请求，即可获得完整商品资料
    """

    file_root = "products{}.txt" # 临时存取抓到的批量数据

    def __init__(self, uri: str, db_name: str, coll_name: str, batch_size: int, max_tries: int, days_bef: int, has_vars: bool, has_recensions: bool, has_ship_fee: bool):
        self.uri = uri
        self.db_name = db_name
        self.coll_name = coll_name
        self.batch_size = batch_size
        self.max_tries = max_tries
        self.days_bef = days_bef # 数据每隔数日更新一次
        self.has_vars = has_vars
        self.has_recensions = has_recensions
        self.has_ship_fee = has_ship_fee

        self.records = 0 # 抓取到的数据量
        self.batch_no = 0
        self.switch = False # 开始批量处理前关闭，写入数据库后打开

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        spider = cls(
            uri=crawler.settings.get("MONGO_URI"),
            db_name=crawler.settings.get("MONGO_DB_NAME"),
            coll_name=crawler.settings.get("MONGO_COLL_NAME", "products"),
            batch_size=crawler.settings.getint("MONGO_BATCH_SIZE", 1000),
            max_tries=crawler.settings.getint("MONGO_MAX_TRIES", 10),
            days_bef=crawler.settings.getint("DAYS_BEF", 7),
            has_vars=crawler.settings.getbool("HAS_VARS", False),
            has_recensions=crawler.settings.getbool("HAS_RECENSIONS", False),
            has_ship_fee=crawler.settings.getbool("HAS_SHIP_FEE", False)
        )

        return spider

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
            self.batch_no += 1
            print("Stage", self.batch_no)

            uos = get_uos(batchfile)
            if bulk_write(uos, self.coll, self.max_tries):
                spider.logger.info(f"Batch {self.batch_no} done")
                print("Stage", self.batch_no, "done")
                os.remove(batchfile)
            else:
                print("bulk_write fail")
            self.switch = True

        return item

    def close_spider(self, spider: Spider):
        if not self.switch:
            batchfile = self.file_root.format(self.batch_no)
            self.batch_no += 1
            print("Stage", self.batch_no)

            uos = get_uos(batchfile)
            if bulk_write(uos, self.coll, self.max_tries):
                spider.logger.info(f"Batch {self.batch_no} done")
                print("Stage", self.batch_no, "done")
                os.remove(batchfile)
            else:
                spider.logger.error(f"Batch {self.batch_no} fail")
                print("Bulk write fail")

        if not update_sold_out(self.coll, self.max_tries, self.days_bef):
            print("Update sold out fail")

        self.client.close()
