import os

from scrapy.commands import ScrapyCommand
from scrapy.http import HtmlResponse
from scrapy.utils.project import get_project_settings


# scrapy ssg_categorie_err_retry
class SsgCategorieErrRetryCmd(ScrapyCommand):
    def run(self, args: list[str], opts)
