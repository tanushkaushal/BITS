$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) { py -3 -m venv .venv }
& '.venv\Scripts\python.exe' -m pip install --upgrade pip
& '.venv\Scripts\python.exe' -m pip install -r requirements.txt
$env:BITS_DB_HOST = 'localhost'
$env:BITS_DB_PORT = '3306'
$env:BITS_DB_NAME = 'bits_inventory'
$env:BITS_DB_USER = Read-Host 'MySQL username [root]'
if ([string]::IsNullOrWhiteSpace($env:BITS_DB_USER)) { $env:BITS_DB_USER = 'root' }
$secure = Read-Host 'MySQL password' -AsSecureString
$env:BITS_DB_PASSWORD = [System.Net.NetworkCredential]::new('', $secure).Password
if ([string]::IsNullOrWhiteSpace($env:BITS_SECRET_KEY)) { $env:BITS_SECRET_KEY = [guid]::NewGuid().ToString('N') }
& '.venv\Scripts\python.exe' app.py
