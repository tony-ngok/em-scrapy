@REM 在Windows中，可运行taskschd.msc，创建一个新计画任务、定时（例如每日执行一次）、调用此脚本，即可实现定时自动抓取。

@echo off
cd /d "%~dp0"
pip install -U scrapy
pip install -U bs4
pip install -U pymongo
git pull

del monotaro.log
scrapy crawl monotaro_category
scrapy crawl monotaro_prod_url
scrapy crawl monotaro_product
