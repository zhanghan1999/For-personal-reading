@echo off
chcp 65001 >nul
title 导师文集 · 本地服务器
cd /d "%~dp0"
set "SCRIPT=%~dp0.tools\server.py"
echo.
echo  ==============================================
echo    导师文集 · 本地服务器（正在启动…）
echo    启动成功后会自动打开首页
echo    关闭本窗口即停止服务
echo  ==============================================
echo.
where py >nul 2>nul
if %errorlevel%==0 (
  py "%SCRIPT%"
  goto end
)
where python >nul 2>nul
if %errorlevel%==0 (
  python "%SCRIPT%"
  goto end
)
"C:\Users\zh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" "%SCRIPT%"
:end
echo.
echo  服务器已退出（如需使用批注自动保存，请保持此窗口开启）。
pause
