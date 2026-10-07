# 📊 Automação Completa + Relatório Estruturado

## 🎯 Novo Fluxo de Execução

Você agora pode executar o projeto com **backup automático**, **limpeza**, **experimentos** e **relatório estruturado** em um único comando:

```bash
# Opção 1: Menu interativo (mais fácil)
python scripts/automate.py interactive
# Escolha opção 10

# Opção 2: Linha de comando completa
python scripts/execute_and_report.py --full

# Opção 3: Teste rápido + relatório
python scripts/execute_and_report.py --quick

# Opção 4: Make
make pipeline
```

---

## 📋 O que o novo fluxo faz

1. **Backup com Timestamp** 
   - Cria pasta `outputs_execucao_{YYYYMMDD_HHMMSS}/`
   - Preserva resultados anteriores para comparação

2. **Limpeza Segura**
   - Remove arquivos antigos de `outputs/`
   - Mantém estrutura de diretórios e `.gitkeep`

3. **Execução Completa**
   - Roda matriz de experimentos (matriz completa ou rápida)
   - Salva imagens, checkpoints, métricas, figuras

4. **Validação**
   - Verifica se quantização respeita limite de cores
   - Gera `validation/validation_unique_colors.csv`

5. **Relatório Estruturado**
   - Gera `report/relatorio_final.md` com:
     - **Introdução**: contexto, problema, objetivos
     - **Fundamentação**: SOM, GNG, k-means, métricas
     - **Metodologia**: hardware, protocolo, hiperparâmetros
     - **Validação**: evidências de funcionamento
     - **Resultados Quantitativos**: tabelas e métricas
     - **Resultados Qualitativos**: imagens e figuras
     - **Discussão**: responde às 4 questões
     - **Limitações**: reconhece restrições
     - **Conclusão**: síntese e trabalhos futuros
     - **Apêndices**: completos com todas as informações

6. **Resumo Executivo**
   - Gera `EXECUCAO_RESUMO.txt` com:
     - Estatísticas dos arquivos gerados
     - Links para resultados principais
     - Timestamp e rastreabilidade

---

## 📁 Estrutura de Backups

```
projeto_2_redes_neurais/
├── outputs/                          ← Resultados ATUAIS
│   ├── checkpoints/
│   ├── reconstructed/
│   ├── figures/
│   ├── metrics/runs.csv
│   └── tables/summary.csv
│
├── outputs_execucao_20261007_143022/ ← Backup anterior
│   ├── checkpoints/
│   ├── reconstructed/
│   └── ...
│
├── outputs_execucao_20261007_102015/ ← Backup anterior
│   └── ...
│
└── EXECUCAO_RESUMO.txt               ← Resumo da última execução
```

Isso permite **comparar e analisar múltiplas execuções** facilmente!

---

## ⏱️ Tempo Estimado

| Opção | Tempo | Imagens | Modelos | Capacidades | Seeds |
|-------|-------|---------|---------|-------------|-------|
| Quick Test | 10-15 min | 1-2 | 2 | 1 | 1-2 |
| Full Matrix (CPU) | 45-75 min | 5 | 3 | 3 | 5 |
| Full Matrix (GPU) | 10-15 min | 5 | 3 | 3 | 5 |

---

## 🎓 Estrutura do Relatório

O relatório gerado segue a estrutura de um trabalho acadêmico completo:

### Frente
- ✅ Introdução (contexto, problema, motivação, objetivos)
- ✅ Fundamentação Teórica (SOM, GNG, k-means, métricas)

### Corpo
- ✅ Metodologia (hardware, dados, protocolo, hiperparâmetros)
- ✅ Validação (convergência, crescimento, reprodutibilidade)
- ✅ Resultados Quantitativos (tabelas de métricas agregadas)
- ✅ Resultados Qualitativos (imagens, figuras, gráficos)

### Análise
- ✅ Discussão (responde às 4 questões propostas)
- ✅ Limitações (reconhece restrições e vieses)
- ✅ Conclusão (síntese, modelo apropriado por cenário)

### Suporte
- ✅ Apêndices (hiperparâmetros, instruções, referências)

**Todas as seções incluem:**
- Espaços para preencher análises manualmente
- Referências automáticas às figuras em `outputs/figures/`
- Tabelas agregadas de `outputs/tables/summary.csv`
- Instruções de reprodução

---

## 🔄 Exemplo de Fluxo Típico

```bash
# 1. Setup inicial (uma única vez)
python scripts/automate.py install

# 2. Teste rápido (validação)
python scripts/automate.py quick

# 3. Execução completa com backup e relatório
python scripts/execute_and_report.py --full

# 4. Abrir relatório
report/relatorio_final.md

# 5. Próxima execução (novo backup automático)
python scripts/execute_and_report.py --full
```

---

## 🛠️ Opções Avançadas

### Apenas Backup
```bash
python scripts/execute_and_report.py --backup-only
```

### Apenas Limpeza
```bash
python scripts/execute_and_report.py --clean-only
```

### Usar config customizado
```bash
python scripts/execute_and_report.py --full --config config/experiments-dev.yaml
```

### Teste rápido + Relatório
```bash
python scripts/execute_and_report.py --quick
```

---

## 📊 Arquivos Gerados

Após execução completa, você terá:

```
outputs/
├── checkpoints/           ← 225+ modelos treinados
├── reconstructed/         ← 225+ imagens quantizadas
├── figures/               ← 225+ gráficos de análise
├── metrics/
│   └── runs.csv          ← Todas as métricas (5+ MB)
└── tables/
    └── summary.csv       ← Resumo agregado (média/std)

report/
└── relatorio_final.md    ← Relatório COMPLETO e estruturado

validation/
└── validation_unique_colors.csv ← Validação de cores

EXECUCAO_RESUMO.txt       ← Resumo da execução
```

---

## 🚀 Comandos Rápidos

```bash
# Menu interativo
python scripts/automate.py

# Execução completa
python scripts/execute_and_report.py --full

# Teste rápido
python scripts/execute_and_report.py --quick

# Com Make
make pipeline

# Limpar e reexecutar
python scripts/execute_and_report.py --clean-only && python scripts/execute_and_report.py --full
```

---

## 💡 Dicas

1. **Primeira Execução**: Use `--quick` para validar o setup (~10 min)
2. **Dados Importantes**: Backups são criados automaticamente com timestamp
3. **Reprodução**: Mesma seed + mesma imagem = mesmo resultado (garantido!)
4. **Relatório**: Editável em Markdown, pode ser convertido para PDF
5. **Comparação**: Compare `outputs_execucao_X` com `outputs_execucao_Y`

---

## 📖 Mais Informação

- [AUTOMACAO.md](AUTOMACAO.md) - Guia completo de automação
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Padrões de código
- [report/relatorio_final.md](report/relatorio_final.md) - Relatório gerado (após execução)

---

**Criado para facilitar a execução reprodutível e documentação completa do Projeto 2! 🎉**
