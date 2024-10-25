import os

from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


# scrapy ssg_prods_ids_errs_retry
class SsgProdsIdsErrsRetryCmd(ScrapyCommand):
    def run(self, args, opts):
        err_file = 'ssg_prods_ids_errs.txt'
        if not os.path.exists(err_file):
            print("Error file not found:", err_file)
            return

        with open(err_file, "r", encoding='utf-8') as f_err:
            todos = [line.strip() for line in f_err if line.strip()]

        open(err_file, 'w').close() # 清空错误记录
        print(f"{len(todos):_}".replace("_", "."), "todos")

        # 设置抓取的爬虫并传递失败的URL列表
        process = CrawlerProcess(get_project_settings())
        process.crawl('ssg_prod_id', start_urls=todos, retry=True)
        process.start()
