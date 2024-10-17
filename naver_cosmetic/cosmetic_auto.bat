@REM 在Windows中，可运行taskschd.msc，创建一个新计画任务、定时（例如每日执行一次）、调用此脚本，即可实现定时自动抓取。

@echo off
cd /d "%~dp0"
git pull

@REM 抓取密文
:graphql_ext
echo Start program graphql_ext.py...
python graphql_ext.py
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program graphql_ext.py fail. Can't continue.
    goto end
)

@REM 反复运行抓取商品号，直到没有出错了为止
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
