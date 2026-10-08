# ⚡ Quick Start - Automação

## Navegação rápida

- [README principal](README.md)
- [Comece aqui](COMECE_AQUI.md)
- [Guia de automação](AUTOMACAO.md)
- [Pipeline completo](PIPELINE_COMPLETO.md)
- [Resumo executivo](AUTOMACAO_RESUMO.md)

## 🎯 Comece em 30 segundos

### Opção A: Menu Interativo (Mais Fácil)
```powershell
cd c:\Projetos\projeto_2_redes_neurais
python scripts/automate.py
```
Escolha a opção no menu.

### Opção B: Linha de Comando
```powershell
# Instalar e rodar teste
python scripts/automate.py install
python scripts/automate.py test

# Rodar 1 experimento (2 min)
python scripts/automate.py single

# Rodar todos os experimentos (30-60 min)
python scripts/automate.py full
```

### Opção C: Make (Se tiver Git Bash/Linux)
```bash
make help           # Ver todos os comandos
make install        # Instalar
make test           # Testes
make single-demo    # 1 experimento
make full-matrix    # Todos os experimentos
make pipeline       # Tudo automaticamente
```

### Opção D: VS Code Tasks
1. Pressione **Ctrl+Shift+P**
2. Digite `Tasks: Run Task`
3. Escolha a tarefa

---

## 🚀 Fluxos Comuns

### 5 minutos
```powershell
python scripts/automate.py install
python scripts/automate.py test
```

### 30 minutos
```powershell
python scripts/automate.py quick    # Teste rápido
python scripts/automate.py report   # Gera relatório
```

### 1 hora
```powershell
python scripts/automate.py pipeline # Tudo automaticamente!
```

---

## 📋 Todas as Opções

| Comando | Tempo | Descrição |
|---------|-------|-----------|
| `python scripts/automate.py install` | 1 min | Instala dependências |
| `python scripts/automate.py test` | 1 min | Roda testes |
| `python scripts/automate.py single` | 2 min | 1 experimento demo |
| `python scripts/automate.py quick` | 10 min | Matriz reduzida |
| `python scripts/automate.py full` | 45 min | Matriz completa |
| `python scripts/automate.py report` | 1 min | Gera relatório |
| `python scripts/automate.py validate` | 2 min | Valida cores |
| `python scripts/automate.py clean` | 1 min | Faz backup e limpa `outputs/` e `validation/` |
| `python scripts/automate.py pipeline` | 60 min | Tudo em sequência |
| `python scripts/automate.py interactive` | ✨ | Menu interativo |

`make clean`, a tarefa VS Code `Clean: Remove Outputs` e o atalho PowerShell
`clean-outputs` limpam apenas `outputs/`, sem backup. `make pipeline` e
`python scripts/automate.py pipeline` também não executam backup/limpeza.
O modo
`python scripts/execute_and_report.py --clean-only` limpa `outputs/` e
`validation/`, também sem backup. Para a limpeza protegida, use
`python scripts/automate.py clean` ou a opção 8 do menu.

---

## 🆘 Troubleshooting

### "ModuleNotFoundError"
```powershell
python scripts/automate.py install
```

### "No images found"
Copie imagens para `data/raw/`:
```powershell
ls data/raw
```

### PowerShell Alias Rápido
Adicione ao seu `profile.ps1`:
```powershell
function auto { python scripts/automate.py }
function test { python -m pytest -q }
function demo { python scripts/automate.py single }
```

---

## 📖 Documentação Completa

- [AUTOMACAO.md](AUTOMACAO.md) - Guia detalhado
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Padrões de código
- [README.md](README.md) - Visão geral do projeto

---

## 🤖 GitHub Actions

O projeto roda automaticamente no GitHub:
- ✅ Testes em cada `push`
- 🔄 Matriz completa todo dia às 2 AM UTC
- 📊 Relatórios automáticos

Veja em: **Actions** → **Color Quantization Pipeline**
