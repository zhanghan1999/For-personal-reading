# ============================================================
# 拉取《毛泽东文集》1-8 卷 PDF → .tools\sources\mao\  （gitignore，不入库）
# 用法：
#   默认源 mzdbl.cn：
#     powershell -ExecutionPolicy Bypass -File .tools\fetch_mao_wenji.ps1
#   指定其他镜像/直链（换 -BaseUrl）：
#     powershell -ExecutionPolicy Bypass -File .tools\fetch_mao_wenji.ps1 -BaseUrl 'https://某镜像/maoxuan'
# 说明：
#   - 该站对本机 IP 限速（约 2KB/s），请在能正常访问 mzdbl.cn/.org 的网络下运行；
#   - 断点续传（curl -C -）+ 自动重试；产物放 .tools\sources\mao\（站点红线：PDF 不入库）。
# ============================================================
param(
  [string]$BaseUrl = 'http://www.mzdbl.cn/maoxuan',
  [string]$OutDir = "$PSScriptRoot\sources\mao"
)
$ProgressPreference = 'SilentlyContinue'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# 文件名（UTF-8 交由 curl 处理；如源站需 GBK 文件名请自行调整）
$files = 1..8 | ForEach-Object { "毛泽东文集$_.pdf" }

foreach ($name in $files) {
  $enc = [uri]::EscapeDataString($name)
  $url = "$BaseUrl/$enc"
  $out = Join-Path $OutDir $name
  Write-Host "==> $name" -ForegroundColor Cyan
  $ok = $false
  for ($try = 1; $try -le 5 -and -not $ok; $try++) {
    curl.exe -sS -L -C - --retry 3 --retry-delay 5 --max-time 1200 -o $out $url
    if ($LASTEXITCODE -eq 0 -and (Test-Path $out)) {
      $sz = (Get-Item $out).Length
      # 校验 PDF 魔数
      $b = [System.IO.File]::ReadAllBytes($out)[0..4]
      $magic = -join ($b | ForEach-Object { [char]$_ })
      if ($magic -eq '%PDF-') { $ok = $true; Write-Host ("    OK  {0:N2} MB" -f ($sz/1MB)) -ForegroundColor Green }
      else { Write-Host ("    非 PDF（跳转/错误页 {0}B），重试 {1}/5" -f $sz, $try) -ForegroundColor Yellow; Remove-Item $out -ErrorAction SilentlyContinue }
    } else {
      Write-Host ("    curl 失败(exit={0})，重试 {1}/5" -f $LASTEXITCODE, $try) -ForegroundColor Yellow
      Start-Sleep -Seconds 8
    }
  }
  if (-not $ok) { Write-Host ("    放弃：$name（网络/限速，可稍后再跑续传）") -ForegroundColor Red }
}

Write-Host "完成。文件在：$OutDir"
Get-ChildItem $OutDir -Filter *.pdf | ForEach-Object { "{0}  {1:N2} MB" -f $_.Name, ($_.Length/1MB) }
