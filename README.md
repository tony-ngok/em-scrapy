# em-scrapy
EveryMarket业务：Scrapy抓取商品

## 抓取注意事项
1. 抓取前，先下载网页（仅HTML），看看里面有没有目标内容
    * 若有，说明该网页可直接用纯Scrapy抓取
    * 若无，说明该网页为JavaScript生成，则考虑用Pyppeteer或Scrapy+Playwright抓取
2. 没有图的商品卖不出去，只能扔掉
3. 配送资料统一以国内邮寄为准（不考虑国际邮寄）
