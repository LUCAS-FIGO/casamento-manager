# Criar diretórios necessários
$directories = @(
    ".\src",
    ".\tests",
    ".\.streamlit"
)

Write-Host "Criando diretórios..." -ForegroundColor Yellow

foreach ($dir in $directories) {
    if (-not (Test-Path -Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Diretório criado: $dir" -ForegroundColor Green
    }
}

# Definir arquivos para mover
$filesToMove = @{
    "CAZAR.py" = ".\src\CAZAR.py"
    "database.py" = ".\src\database.py"
    "casamento_manager.py" = ".\src\casamento_manager.py"
    "secrets.toml" = ".\.streamlit\secrets.toml"
}

Write-Host "Movendo arquivos..." -ForegroundColor Yellow

foreach ($file in $filesToMove.Keys) {
    if (Test-Path -Path $file) {
        Move-Item -Path $file -Destination $filesToMove[$file] -Force
        Write-Host "Arquivo movido: $file -> $($filesToMove[$file])" -ForegroundColor Green
    }
}

# Criar arquivo de teste
$testContent = @'
import pytest
from src.database import Database

def test_database_connection():
    db = Database()
    assert db is not None
'@

$testPath = ".\tests\test_database.py"
if (-not (Test-Path -Path $testPath)) {
    Set-Content -Path $testPath -Value $testContent
    Write-Host "Arquivo de teste criado: $testPath" -ForegroundColor Green
}

# Atualizar .gitignore
$gitignoreContent = @'
# Ambiente Python
__pycache__/
*.py[cod]
*$py.class
.env
venv/

# VS Code
.vscode/

# Streamlit
.streamlit/secrets.toml

# Logs
*.log

# Sistema
.DS_Store
Thumbs.db
'@

Set-Content -Path ".gitignore" -Value $gitignoreContent
Write-Host "Arquivo .gitignore atualizado" -ForegroundColor Green

Write-Host "`nOrganização do projeto concluída!" -ForegroundColor Green

# Exibir estrutura final
Write-Host "`nEstrutura do projeto:" -ForegroundColor Yellow
Get-ChildItem -Recurse | Where-Object { !$_.PSIsContainer } | Select-Object FullName