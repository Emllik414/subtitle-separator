@echo off
chcp 65001 >nul
title 创建双语字幕工具桌面快捷方式
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0CreateDesktopShortcut.ps1"
if errorlevel 1 (
  echo.
  echo 创建失败。请确认已经先解压整个 ZIP，然后再运行本文件。
) else (
  echo.
  echo 完成。现在可以从桌面打开“双语字幕工具”。
)
echo.
pause
