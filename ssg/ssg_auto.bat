@REM 在Windows中，可运行taskschd.msc，创建一个新计画任务、定时（例如每日执行一次）、调用此脚本，即可实现定时自动抓取。

@echo off
cd /d "%~dp0"
pip install -U scrapy
pip install -U bs4
git pull

@REM 抓取商品分类
:categorie
echo Start program ssg_categorie...
scrapy crawl ssg_categorie
echo Errors: %ERRORLEVEL% 
if %ERRORLEVEL% neq 0 (
    echo Program ssg_categorie ends with errors. Rerun...
    goto categorie_review
)
echo Program ssg_categorie success
goto prod_id

@REM 重试抓取商品分类
:categorie_review
scrapy ssg_cats_errs_retry
echo Errors: %ERRORLEVEL% 
if %ERRORLEVEL% neq 0 (
    echo Program ssg_cats_errs_retry ends with errors. Rerun...
    goto categorie_review
)
echo Program ssg_categorie success
goto prod_id

@REM 抓取商品号
:prod_id
echo Start program ssg_prod_id...
scrapy crawl ssg_prod_id
echo Errors: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program ssg_prod_id ends with errors. Rerun...
    goto prod_id_review
)
echo Program ssg_prod_id success
goto product

@REM 重试抓取商品号
:prod_id_review
scrapy ssg_prods_ids_errs_retry
echo Errors: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program ssg_prods_ids_errs_retry ends with errors. Rerun...
    goto prod_id_review
)
echo Program ssg_prod_id success
goto product

@REM 抓取商品详细
:product
echo Start program ssg_prod...
scrapy crawl ssg_prod
echo Errors: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program ssg_prod ends with errors. Rerun...
    goto product_review
)
echo Program ssg_prod success
goto end

@REM 重试抓取商品详细
:product_review
scrapy ssg_prods_errs_retry
echo Errors: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program ssg_prods_errs_retry ends with errors. Rerun...
    goto product_review
)
echo Program ssg_prod success
goto end

:end
echo Pack up JSON...
python jsons_list.py
echo END
