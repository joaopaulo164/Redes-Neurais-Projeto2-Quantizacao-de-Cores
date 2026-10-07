# Arquivo de perfil do PowerShell - Atalhos rápidos para automação
# Copie este arquivo para: C:\Users\{seu_usuario}\Documents\PowerShell\profile.ps1

# ou adicione o conteúdo ao seu profile.ps1 existente

$ProjectRoot = "c:\Projetos\projeto_2_redes_neurais"

# Função para mostrar ajuda dos atalhos
function Show-AutomationHelp {
    Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║       🤖 Atalhos de Automação - Quantização de Cores        ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
    
    Write-Host "📦 INSTALAÇÃO" -ForegroundColor Green
    Write-Host "  · install-deps         Instalar dependências"
    Write-Host "  · update-deps          Atualizar dependências`n"
    
    Write-Host "🧪 TESTES" -ForegroundColor Green
    Write-Host "  · run-tests            Executar testes unitários"
    Write-Host "  · run-tests-verbose    Testes com saída detalhada`n"
    
    Write-Host "🚀 EXPERIMENTOS" -ForegroundColor Green
    Write-Host "  · run-demo             Experimento único (demo)"
    Write-Host "  · run-quick            Teste rápido (matriz reduzida)"
    Write-Host "  · run-full             Matriz completa"
    Write-Host "  · run-pipeline         Pipeline completo (install→test→full→report)`n"
    
    Write-Host "📊 RELATÓRIOS" -ForegroundColor Green
    Write-Host "  · gen-report           Gerar relatório Markdown"
    Write-Host "  · validate-colors      Validar cores únicas`n"
    
    Write-Host "🧹 LIMPEZA" -ForegroundColor Green
    Write-Host "  · clean-outputs        Remover arquivos de saída"
    Write-Host "  · clean-cache          Remover cache Python"
    Write-Host "  · clean-all            Limpar tudo e reinstalar`n"
    
    Write-Host "🎯 MENU" -ForegroundColor Green
    Write-Host "  · auto-menu            Menu interativo de automação`n"
}

# ========== INSTALAÇÃO ==========
function install-deps {
    Set-Location $ProjectRoot
    Write-Host "`n📦 Instalando dependências..." -ForegroundColor Green
    python -m pip install -r requirements.txt
    Write-Host "✅ Dependências instaladas!`n" -ForegroundColor Green
}

function update-deps {
    Set-Location $ProjectRoot
    Write-Host "`n📦 Atualizando dependências..." -ForegroundColor Green
    python -m pip install --upgrade -r requirements.txt
    Write-Host "✅ Dependências atualizadas!`n" -ForegroundColor Green
}

# ========== TESTES ==========
function run-tests {
    Set-Location $ProjectRoot
    Write-Host "`n🧪 Executando testes..." -ForegroundColor Blue
    python -m pytest -q
    Write-Host "`n✅ Testes concluídos!`n" -ForegroundColor Green
}

function run-tests-verbose {
    Set-Location $ProjectRoot
    Write-Host "`n🧪 Executando testes (verbose)..." -ForegroundColor Blue
    python -m pytest -v
    Write-Host "`n✅ Testes concluídos!`n" -ForegroundColor Green
}

# ========== EXPERIMENTOS ==========
function run-demo {
    Set-Location $ProjectRoot
    Write-Host "`n🚀 Executando experimento demo (SOM 16 cores)..." -ForegroundColor Cyan
    python scripts/run_single.py --image data/raw/00_controle_16_cores.png --model som --capacity 16 --seed 13
    Write-Host "`n✅ Experimento demo concluído!`n" -ForegroundColor Green
}

function run-quick {
    Set-Location $ProjectRoot
    Write-Host "`n⚡ Executando teste rápido (matriz reduzida)..." -ForegroundColor Cyan
    python scripts/run_all.py --config "config/experiments - teste rapido.yaml"
    Write-Host "`n✅ Teste rápido concluído!`n" -ForegroundColor Green
}

function run-full {
    Set-Location $ProjectRoot
    Write-Host "`n🔄 Executando matriz completa..." -ForegroundColor Cyan
    Write-Host "⏱️  Tempo esperado: 30-60 minutos`n" -ForegroundColor Yellow
    python scripts/run_all.py --config config/experiments.yaml
    Write-Host "`n✅ Matriz completa concluída!`n" -ForegroundColor Green
}

function run-pipeline {
    Set-Location $ProjectRoot
    Write-Host "`n🔗 Iniciando pipeline completo..." -ForegroundColor Cyan
    Write-Host "⏱️  Tempo esperado: 45-75 minutos`n" -ForegroundColor Yellow
    python scripts/automate.py pipeline
    Write-Host "`n✅ Pipeline completo finalizado!`n" -ForegroundColor Green
}

# ========== RELATÓRIOS ==========
function gen-report {
    Set-Location $ProjectRoot
    Write-Host "`n📊 Gerando relatório..." -ForegroundColor Yellow
    python scripts/generate_report.py
    Write-Host "`n✅ Relatório gerado!`n" -ForegroundColor Green
}

function validate-colors {
    Set-Location $ProjectRoot
    Write-Host "`n✔️  Validando cores únicas..." -ForegroundColor Yellow
    python scripts/validate_unique_colors.py
    Write-Host "`n✅ Validação concluída!`n" -ForegroundColor Green
}

# ========== LIMPEZA ==========
function clean-outputs {
    Set-Location $ProjectRoot
    Write-Host "`n🧹 Limpando arquivos de saída..." -ForegroundColor Magenta
    Remove-Item outputs/checkpoints/* -Force -ErrorAction SilentlyContinue
    Remove-Item outputs/reconstructed/* -Force -ErrorAction SilentlyContinue
    Remove-Item outputs/figures/* -Force -ErrorAction SilentlyContinue
    Remove-Item outputs/metrics/runs.csv -Force -ErrorAction SilentlyContinue
    Remove-Item outputs/tables/summary.csv -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Limpeza concluída!`n" -ForegroundColor Green
}

function clean-cache {
    Set-Location $ProjectRoot
    Write-Host "`n🧹 Limpando cache Python..." -ForegroundColor Magenta
    Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Force -Recurse
    Remove-Item .pytest_cache -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "✅ Cache limpo!`n" -ForegroundColor Green
}

function clean-all {
    Set-Location $ProjectRoot
    Write-Host "`n🧹 Limpeza completa..." -ForegroundColor Magenta
    clean-outputs
    clean-cache
    install-deps
    Write-Host "✅ Limpeza completa finalizada!`n" -ForegroundColor Green
}

# ========== MENU ==========
function auto-menu {
    Set-Location $ProjectRoot
    Write-Host "`n🤖 Menu Interativo de Automação`n" -ForegroundColor Cyan
    python scripts/automate.py interactive
}

# ========== ALIAS RÁPIDOS ==========
New-Alias -Name proj -Value { Set-Location $ProjectRoot } -ErrorAction SilentlyContinue
New-Alias -Name help-auto -Value Show-AutomationHelp -ErrorAction SilentlyContinue

# Mostrar atalhos ao iniciar o PowerShell
Write-Host "`n✨ Atalhos de automação carregados! Use 'help-auto' para ver todos os comandos`n" -ForegroundColor Green
