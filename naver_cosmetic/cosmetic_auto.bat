@REM 在Windows中，可运行taskschd.msc，创建一个新计画任务、定时（例如每日执行一次）、调用此脚本，即可实现定时自动抓取。

@echo off
cd /d "%~dp0"
git pull

@REM 抓取密文
:graphql_ext
echo Start program 'graphql_ext.py cosmetic'...
python graphql_ext.py cosmetic
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program 'graphql_ext.py cosmetic' fail. Can't continue.
    goto end
)

@REM 反复运行抓取商品号，直到没有出错了为止
:prod_id
echo Start program 'prod_id.py cosmetic'...
python prod_id.py cosmetic
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program 'prod_id.py cosmetic' ends with errors. Rerun...
    goto prod_id_review
)
echo Program 'prod_id.py cosmetic' success
goto end

:prod_id_review
python prod_id.py cosmetic --review
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program 'prod_id.py cosmetic --review' ends with errors. Rerun...
    goto prod_id_review
)
echo Program 'prod_id.py cosmetic' success
goto end

:product
echo Start program 'product.py' cosmetic...
python product.py cosmetic
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program 'product.py cosmetic' ends with errors. Rerun...
    goto product_review
)
echo Program 'product.py cosmetic' success
goto end

:product_review
python product.py cosmetic --review
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program 'product.py cosmetic --review' ends with errors. Rerun...
    goto product_review
)
echo Program 'product.py cosmetic' success
goto end

:end
echo Pack up JSON...
python jsons_list.py cosmetic
echo END
