@REM 在Windows中，可运行taskschd.msc，创建一个新计画任务、定时（例如每日执行一次）、调用此脚本，即可实现定时自动抓取。

@echo off
cd /d "%~dp0"
git pull

:cats
echo Start program cats.py...
python cats.py
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program cats.py ends with errors. Rerun...
    goto cats_review
)
echo Program cats.py success
goto end

:cats_review
python cats.py --review
echo Exit code: %ERRORLEVEL%
if %ERRORLEVEL% neq 0 (
    echo Program cats.py --review ends with errors. Rerun...
    goto cats_review
)
echo Program cats.py success
goto end

:end
echo END
