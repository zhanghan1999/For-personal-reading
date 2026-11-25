# server.ps1 — 导师文集本地服务器（纯 PowerShell，任何 Windows 电脑免装 Python）
# 功能：静态托管全站 + POST /anno 保存私人批注 + POST /page-write 写回补充注释到文章
# 用法：双击「启动导师文集.bat」；本脚本由 bat 调用。
$ErrorActionPreference = 'Stop'
$ROOT = Split-Path -Parent $PSScriptRoot
$PORT = 8790
$ANNO = Join-Path $ROOT '批注\annotations.js'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$MIME = @{
  '.html' = 'text/html; charset=utf-8'; '.htm' = 'text/html; charset=utf-8'
  '.css' = 'text/css; charset=utf-8'; '.js' = 'application/javascript; charset=utf-8'
  '.json' = 'application/json; charset=utf-8'; '.png' = 'image/png'; '.jpg' = 'image/jpeg'
  '.jpeg' = 'image/jpeg'; '.gif' = 'image/gif'; '.svg' = 'image/svg+xml'; '.ico' = 'image/x-icon'
  '.txt' = 'text/plain; charset=utf-8'; '.pdf' = 'application/pdf'
  '.woff2' = 'font/woff2'; '.woff' = 'font/woff'; '.ttf' = 'font/ttf'
  '.mp3' = 'audio/mpeg'; '.mp4' = 'video/mp4'
}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://127.0.0.1:$PORT/")
try {
  $listener.Start()
} catch {
  Write-Host "端口 $PORT 被占用：$($_.Exception.Message)"
  Read-Host '按回车键退出'
  exit 1
}

function Send-Text($resp, $code, $contentType, $text) {
  $resp.StatusCode = $code
  $resp.ContentType = $contentType
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
  $resp.ContentLength64 = $bytes.Length
  $resp.OutputStream.Write($bytes, 0, $bytes.Length)
}

function Send-Json($resp, $code, $obj) {
  Send-Text $resp $code 'application/json; charset=utf-8' ($obj | ConvertTo-Json -Compress)
}

$handler = {
  param($ctx)
  $req = $ctx.Request
  $resp = $ctx.Response
  $resp.KeepAlive = $false   # 每个请求独立连接，串行处理不互相阻塞
  try {
    $raw = [System.Uri]::UnescapeDataString($req.Url.AbsolutePath)
    $path = $raw.Replace('/', '\').TrimStart('\')
    if ($req.HttpMethod -eq 'POST') {
      $reader = New-Object System.IO.StreamReader($req.InputStream, [System.Text.Encoding]::UTF8)
      $body = $reader.ReadToEnd()
      if ($path -eq 'anno') {
        $dir = Split-Path $ANNO -Parent
        if (!(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        [System.IO.File]::WriteAllText($ANNO, $body, [System.Text.Encoding]::UTF8)
        Send-Json $resp 200 @{ ok = $true }
        Write-Host "批注已自动保存 -> $ANNO"
      } elseif ($path -eq 'page-write') {
        $data = $body | ConvertFrom-Json
        $rel = (($data.path -replace '\\', '/').TrimStart('/'))
        if ($rel -notmatch '\.html$' -or $rel -match '\.\.') {
          Send-Text $resp 400 'text/plain; charset=utf-8' 'bad path'
          return
        }
        $fp = [System.IO.Path]::GetFullPath((Join-Path $ROOT $rel))
        $rootFull = [System.IO.Path]::GetFullPath($ROOT)
        if (-not $fp.StartsWith($rootFull + '\', [System.StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path $fp -PathType Leaf)) {
          Send-Text $resp 403 'text/plain; charset=utf-8' 'forbidden'
          return
        }
        $html = [System.IO.File]::ReadAllText($fp, [System.Text.Encoding]::UTF8)
        # 用 Match 的索引拼接，避开 .NET 替换串里 $1/$& 的转义（正文里出现 $ 也不会被吃掉）
        $m = [regex]::Match($html, '<main\b[^>]*>.*?</main>', 'Singleline')
        if (-not $m.Success) {
          Send-Text $resp 500 'text/plain; charset=utf-8' 'main not found'
          return
        }
        $repl = '<main id="main">' + $data.mainHtml + '</main>'
        $new = $html.Substring(0, $m.Index) + $repl + $html.Substring($m.Index + $m.Length)
        if ($new -ne $html) {
          [System.IO.File]::WriteAllText($fp, $new, [System.Text.Encoding]::UTF8)
          Write-Host "文章已写回 -> $fp"
        } else {
          # 内容没变（例如“保存空内容=删除新条目”）不是错误，照常返回成功
          Write-Host "文章无变化，跳过写入 -> $fp"
        }
        Send-Json $resp 200 @{ ok = $true }
      } else {
        Send-Text $resp 404 'text/plain; charset=utf-8' 'not found'
      }
    } else {
      if ($path -eq '') { $path = 'index.html' }
      $full = [System.IO.Path]::GetFullPath((Join-Path $ROOT $path))
      $rootFull = [System.IO.Path]::GetFullPath($ROOT)
      if ($full.StartsWith($rootFull + '\', [System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path $full -PathType Leaf)) {
        $ext = [System.IO.Path]::GetExtension($full).ToLower()
        if ($MIME.ContainsKey($ext)) { $resp.ContentType = $MIME[$ext] } else { $resp.ContentType = 'application/octet-stream' }
        $resp.Headers['Cache-Control'] = 'no-cache'
        $bytes = [System.IO.File]::ReadAllBytes($full)
        $resp.ContentLength64 = $bytes.Length
        $resp.OutputStream.Write($bytes, 0, $bytes.Length)
      } else {
        Send-Text $resp 404 'text/plain; charset=utf-8' 'not found'
      }
    }
  } catch {
    try { Send-Text $resp 500 'text/plain; charset=utf-8' $_.Exception.Message } catch { }
  } finally {
    try { $resp.Close() } catch { }
  }
}

Write-Host '===================================================='
Write-Host '  导师文集 · 本地服务器已启动'
Write-Host "  首页地址：http://127.0.0.1:$PORT/"
Write-Host "  批注自动保存：$ANNO"
Write-Host '  关闭本窗口即停止服务'
Write-Host '===================================================='
Start-Process "http://127.0.0.1:$PORT/"

while ($listener.IsListening) {
  $ctx = $listener.GetContext()
  try {
    & $handler $ctx          # 同 runspace 同步处理（变量可见；Connection:close 保证不互相阻塞）
  } catch {
    try { Send-Text $ctx.Response 500 'text/plain; charset=utf-8' $_.Exception.Message } catch { }
  }
}
