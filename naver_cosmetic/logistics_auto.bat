@REM 在Windows中，可运行taskschd.msc，创建一个新计画任务、定时（例如每日执行一次）、调用此脚本，即可实现定时自动抓取。

@echo off
cd /d "%~dp0"
git pull

@REM 抓取密文
:graphql_ext
echo Start program 'graphql_ext.py logistics'...
python graphql_ext.py logistics
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program 'graphql_ext.py logistics' fail. Can't continue.
    goto end
)

@REM 反复运行抓取商品号，直到没有出错了为止
:prod_id
echo Start program 'prod_id.py logistics'...
python prod_id.py logistics
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program 'prod_id.py logistics' ends with errors. Rerun...
    goto prod_id_review
)
echo Program 'prod_id.py logistics' success
goto end

:prod_id_review
python prod_id.py logistics --review
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program 'prod_id.py logistics --review' ends with errors. Rerun...
    goto prod_id_review
)
echo Program 'prod_id.py logistics' success
goto end

:product
echo Start program 'product.py' logistics...
python product.py logistics
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program 'product.py logistics' ends with errors. Rerun...
    goto product_review
)
echo Program 'product.py logistics' success
goto end

:product_review
python product.py logistics --review
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program 'product.py logistics --review' ends with errors. Rerun...
    goto product_review
)
echo Program 'product.py logistics' success
goto end

:end
echo Pack up JSON...
python jsons_list.py logistics
echo END
