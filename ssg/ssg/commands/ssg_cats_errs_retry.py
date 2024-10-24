import os

from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


# scrapy ssg_cats_errs_retry
class SsgCatsErrsRetryCmd(ScrapyCommand):
    def run(self, args, opts):
        err_file = f'ssg_categories_errs.txt'
        if not os.path.exists(err_file):
            print("Error file not found:", err_file)
            return
        
        with open(err_file, "r", encoding='utf-8') as f_err:
            todos = []
            for line in f_err:
                todo = line.strip()
                if todo:
                    if todo == 'monm':
                        todos.append('https://www.ssg.com/monm/main.ssg')
                    else:
                        todos.append('https://www.ssg.com/disp/category.ssg?ctgId='+todo)

        open(err_file, 'w').close() # 清空错误记录

        # 设置抓取的爬虫并传递失败的URL列表
        process = CrawlerProcess(get_project_settings())
        process.crawl('ssg_categorie', start_urls=todos, retry=True)
        process.start()
