@REM 在Windows中，可运行taskschd.msc，创建一个新计画任务、定时（例如每日执行一次）、调用此脚本，即可实现定时自动抓取。

@echo off
cd /d "%~dp0"
git pull

python graphql_ext.py @REM 抓取密文

@REM 反复运行抓取商品号，直到没有出错了为止
:loop
python prod_id.py
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Last run ends with errors. Rerun...
    goto loop
)
