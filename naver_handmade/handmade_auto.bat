@REM 在Windows中，可运行taskschd.msc，创建一个新计画任务、定时（例如每日执行一次）、调用此脚本，即可实现定时自动抓取。

@echo off
cd /d "%~dp0"
git pull

@REM 从大分类中抓取品牌子分类
:cat_brand
echo Start program cat_brand.py...
python cat_brand.py
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program cat_brand.py ends with errors. Rerun...
    goto cat_brand_review
)
echo Program cat_brand.py success
goto end

@REM 重试抓取品牌子分类
:cat_brand_review
python cat_brand.py --review
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program cat_brand.py --review ends with errors. Rerun...
    goto cat_brand_review
)
echo Program cat_brand.py success
goto end

@REM 抓取商品号
:prod_id
echo Start program prod_id.py...
python prod_id.py
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program prod_id.py ends with errors. Rerun...
    goto prod_id_review
)
echo Program prod_id.py success
goto end

@REM 重试抓取商品号
:prod_id_review
python prod_id.py --review
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program prod_id.py --review ends with errors. Rerun...
    goto prod_id_review
)
echo Program prod_id.py success
goto end

:end
echo END
