$ErrorActionPreference = "Stop"

$exePath = Join-Path $PSScriptRoot "SubtitleSeparator.exe"
if (-not (Test-Path $exePath)) {
    throw "SubtitleSeparator.exe was not found next to this script. Please extract the whole ZIP first."
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "双语字幕工具.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exePath
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.IconLocation = "$exePath,0"
$shortcut.Description = "双语字幕分离、合并与格式转换工具"
$shortcut.Save()

Write-Host "桌面快捷方式已创建：$shortcutPath" -ForegroundColor Green
