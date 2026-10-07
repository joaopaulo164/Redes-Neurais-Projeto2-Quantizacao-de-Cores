# Projeto 2 - Redes Neurais: Quantização de Cores

Implementação em Python + PyTorch para quantização de cores com SOM, GNG e k-means, incluindo execução reprodutível, métricas, gráficos, validação e geração de relatório.

## Navegação Rápida

Se você chegou aqui primeiro, siga este caminho:

1. Leia `COMECE_AQUI.md` para começar em 60 segundos.
2. Use `AUTOMACAO.md` para entender os fluxos de automação.
3. Use `AUTOMATE_QUICK_START.md` para atalhos rápidos de comando.
4. Use `PIPELINE_COMPLETO.md` para detalhes do pipeline com backup.
5. Consulte `AUTOMACAO_RESUMO.md` para um panorama executivo.

## Visão Geral

Este projeto executa um pipeline completo de quantização:

- leitura das imagens em `data/raw/`
- amostragem controlada por semente
- treinamento dos modelos (SOM, GNG, k-means)
- quantização dos pixels da imagem inteira
- avaliação por métricas de erro e qualidade visual
- geração de imagens, gráficos e relatório final

## Requisitos

```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

Se estiver usando Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução Rápida

```bash
# Experimento único
python scripts/run_single.py --image data/raw/exemplo.png --model som --capacity 16 --seed 13

# Matriz completa
python scripts/run_all.py --config config/experiments.yaml

# Relatório
python scripts/generate_report.py

# Testes
pytest -q
```

## Automação do Projeto

Os fluxos automatizados estão centralizados nos seguintes arquivos:

```bash
# Menu interativo
python scripts/automate.py

# Pipeline completo com backup
python scripts/execute_and_report.py --quick
python scripts/execute_and_report.py --full
```

## Documentação do Projeto

### Para começar
- `COMECE_AQUI.md` — guia inicial em 60 segundos
- `AUTOMATE_QUICK_START.md` — referência rápida de comandos

### Para automação e execução
- `AUTOMACAO.md` — guia completo de automação
- `PIPELINE_COMPLETO.md` — visão detalhada do pipeline com backup e relatórios
- `AUTOMACAO_RESUMO.md` — resumo executivo do que foi implementado

### Para requisitos e suporte
- `README_AUTOMACAO.md` — visão geral da automação
- `README_GITIGNORE.md` — regras de ignore do Git
- `Guia_detalhado_de_execucao_Projeto_2.md` — manual detalhado do projeto
- `Guia_detalhado_de_execucao_Projeto_2_Atualizado.md` — versão atualizada do guia

## Estrutura de Saída

```text
outputs/
├── checkpoints/
├── reconstructed/
├── figures/
├── metrics/
├── tables/

report/
└── relatorio_final.md

validation/
└── validation_unique_colors.csv
```

## Resultado Esperado

O projeto gera:

- imagens reconstruídas e checkpoints;
- erro de quantização e topológico;
- MAE, MSE, RMSE, PSNR e Delta E CIEDE2000;
- mapas Delta E, histogramas, gráficos de protótipos e grafo GNG;
- CSV por execução e resumo agregado;
- relatório Markdown final em `report/`.

## Fluxo Recomendado

Para trabalhar no projeto de forma organizada:

1. Comece com `COMECE_AQUI.md`.
2. Entenda a automação em `AUTOMACAO.md`.
3. Use `python scripts/execute_and_report.py --quick` para testar.
4. Quando estiver estável, execute `--full` para a matriz completa.
5. Consulte o relatório em `report/relatorio_final.md`.

## Observações

A inferência e avaliação usam todos os pixels. A amostra de treinamento é mantida por imagem/semente para garantir comparabilidade e reprodutibilidade.

---

Para mais detalhes, comece por `COMECE_AQUI.md` e siga a trilha de documentos indicada acima.

## Índice por perfil de usuário

### Se você é iniciante
- [COMECE_AQUI.md](COMECE_AQUI.md) — guia rápido em 60 segundos
- [AUTOMACAO.md](AUTOMACAO.md) — visão geral da automação
- [AUTOMATE_QUICK_START.md](AUTOMATE_QUICK_START.md) — comandos prontos para usar

### Se você quer automatizar o projeto
- [AUTOMACAO.md](AUTOMACAO.md) — fluxo completo de execução e automação
- [PIPELINE_COMPLETO.md](PIPELINE_COMPLETO.md) — backup, limpeza, validação e relatório
- [AUTOMACAO_RESUMO.md](AUTOMACAO_RESUMO.md) — resumo executivo do sistema

### Se você quer executar passo a passo
- [Guia_detalhado_de_execucao_Projeto_2.md](Guia_detalhado_de_execucao_Projeto_2.md) — guia original detalhado
- [Guia_detalhado_de_execucao_Projeto_2_Atualizado.md](Guia_detalhado_de_execucao_Projeto_2_Atualizado.md) — versão atualizada para Windows e prática operacional
- [README_GITIGNORE.md](README_GITIGNORE.md) — regras de Git, ambientes e arquivos ignorados

### Se você quer mais contexto técnico
- [README_AUTOMACAO.md](README_AUTOMACAO.md) — visão geral da automação implementada
- [Project_2.pdf](Project_2.pdf) — material complementar do projeto

---

## Documento principal recomendado

Para a maioria dos usuários, o melhor ponto de partida é:

1. [COMECE_AQUI.md](COMECE_AQUI.md)
2. [AUTOMACAO.md](AUTOMACAO.md)
3. [AUTOMATE_QUICK_START.md](AUTOMATE_QUICK_START.md)

A partir daí, você pode seguir para o guia detalhado ou para a execução automatizada.

---
