# 🤖 Guia de Automação - Projeto 2

Este guia descreve as várias maneiras de automatizar a execução do projeto de quantização de cores com redes neurais.

## Opção 1: Menu Interativo (Recomendado para Iniciantes)

A forma mais simples de começar:

```bash
python scripts/automate.py
```

Ou simplesmente:

```bash
python scripts/automate.py interactive
```

Isso abre um menu com as seguintes opções:
- 1️⃣ Instalar dependências
- 2️⃣ Executar testes
- 3️⃣ Experimento único (demo)
- 4️⃣ Matriz completa
- 5️⃣ Teste rápido
- 6️⃣ Gerar relatório
- 7️⃣ Validar cores
- 8️⃣ Limpar outputs
- 9️⃣ Pipeline completo

---

## Opção 2: Linha de Comando

Execute comandos específicos diretamente:

```bash
# Instalação
python scripts/automate.py install

# Testes
python scripts/automate.py test

# Experimento único
python scripts/automate.py single

# Matriz completa
python scripts/automate.py full

# Teste rápido
python scripts/automate.py quick

# Gerar relatório
python scripts/automate.py report

# Validar cores
python scripts/automate.py validate

# Limpar outputs
python scripts/automate.py clean

# Pipeline completo (install → test → full → report)
python scripts/automate.py pipeline
```

---

## Opção 3: Make (Padrão do Projeto)

Se você tem `make` instalado (Linux/macOS ou Windows com Git Bash):

```bash
# Ver ajuda
make help

# Instalar
make install

# Testes
make test

# Experimento demo
make single-demo

# Teste rápido
make quick-test

# Matriz completa
make full-matrix

# Gerar relatório
make report

# Validar
make validate

# Limpar
make clean

# Pipeline completo
make pipeline

# Menu interativo
make interactive
```

---

## Opção 4: VS Code Tasks

Abra a paleta de comandos no VS Code (**Ctrl+Shift+P** / **Cmd+Shift+P**) e digite:

```
Tasks: Run Task
```

Selecione uma das tarefas disponíveis:
- ✅ **Setup: Install Dependencies** - Instala pacotes
- 🧪 **Test: Run Pytest** - Executa testes
- 🚀 **Experiment: Single Run (Quick Demo)** - Experimento de demonstração
- 🔄 **Experiment: Full Matrix (All Experiments)** - Matriz completa
- ⚡ **Experiment: Quick Test (Reduced Matrix)** - Teste rápido
- 📊 **Report: Generate Markdown Report** - Gera relatório
- ✔️ **Validation: Unique Colors Check** - Valida cores
- 🧹 **Clean: Remove Outputs** - Limpa arquivos
- 🔗 **Full Pipeline: Setup → Test → Run All → Report** - Pipeline completo

---

## Opção 5: GitHub Actions (CI/CD Automático)

O projeto inclui um workflow automático que:
- ✅ Roda testes em Python 3.10, 3.11, 3.12
- 🚀 Executa teste rápido em cada push
- 🔄 Executa matriz completa diariamente (2 AM UTC)
- 📊 Gera relatório e armazena resultados

**Ativar**: O workflow roda automaticamente quando você faz `push` ao repositório.

**Forçar execução manual**:
1. Vá para a aba **Actions** no GitHub
2. Selecione **Color Quantization Pipeline**
3. Clique em **Run workflow** e escolha o tipo de execução

---

## Fluxos de Trabalho Típicos

### 🏃 Desenvolvimento Rápido (5 min)
```bash
make test                    # Testa código
make single-demo            # Roda 1 experimento
```

### ⚡ Validação (30 min)
```bash
make install                # Atualiza dependências
make test                   # Testes completos
make quick-test            # Matriz reduzida
make report                # Gera relatório
```

### 🔬 Pesquisa Completa (3+ horas)
```bash
make pipeline              # Pipeline automático completo
# ou
python scripts/automate.py pipeline
```

### 🧹 Limpeza de Dados
```bash
make clean                 # Remove todos os outputs
make install              # Reinstala dependências
```

---

## Estrutura de Automação

```
scripts/automate.py          # Script Python de automação (CLI + Menu)
.vscode/tasks.json          # Tarefas do VS Code
.github/workflows/pipeline.yml  # Workflow do GitHub Actions
Makefile                    # Automação com Make
```

---

## Exemplos Avançados

### Rodar múltiplos experimentos em paralelo (Unix)
```bash
for model in som gng kmeans; do
  python scripts/automate.py single --model $model &
done
wait
```

### Criar relatório após experimento
```bash
python scripts/automate.py full
python scripts/automate.py report
```

### Backup de resultados
```bash
cp -r outputs/ outputs.backup.$(date +%Y%m%d)
```

---

## Troubleshooting

### Erro: "Module not found"
```bash
make install
# ou
python scripts/automate.py install
```

### Erro: "No images found"
Certifique-se de ter imagens em `data/raw/`:
```bash
ls -la data/raw/
```

### Limpar cache do Python
```bash
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
rm -rf .pytest_cache/
```

---

## Performance

| Fluxo | Tempo Esperado | CPU | GPU Suportada |
|-------|----------------|-----|--------------|
| Testes | 10-20s | ✅ | - |
| Single Demo | 30-60s | ✅ | ✅ |
| Teste Rápido | 5-10 min | ✅ | ✅ |
| Matriz Completa | 30-60 min | ✅ | ✅ (10x mais rápido) |
| Pipeline Completo | 45-75 min | ✅ | ✅ |

---

## Variáveis de Ambiente

```bash
# Forçar CPU (mesmo com CUDA disponível)
export PYTORCH_DISABLE_CUDA=1
python scripts/automate.py pipeline

# Definir número de threads do PyTorch
export OMP_NUM_THREADS=4
python scripts/automate.py full
```

---

## Próximos Passos

- 📖 Leia [README.md](../README.md) para visão geral do projeto
- 📚 Consulte [.github/copilot-instructions.md](copilot-instructions.md) para padrões de código
- 🔧 Configure seu `config/experiments.yaml` customizado
- 🤖 Use o menu interativo para familiarizar-se com o projeto
