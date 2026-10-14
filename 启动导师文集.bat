@echo off
title 导师文集 - 本地服务器
cd /d "%~dp0"
echo.
echo  ==============================================
echo    导师文集 - 本地服务器（正在启动...）
echo    启动成功后会自动打开首页
echo    关闭本窗口即停止服务
echo  ==============================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0.tools\server.ps1"
echo.
echo  服务器已退出（如需使用批注自动保存，请保持此窗口开启）。
pause
