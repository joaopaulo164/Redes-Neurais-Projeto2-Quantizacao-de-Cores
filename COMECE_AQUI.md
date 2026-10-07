# 🎯 Comece Aqui em 60 Segundos

## O que foi criado para você?

Uma **automação completa** que faz:
1. ✅ Backup automático de resultados anteriores
2. ✅ Limpeza segura de outputs
3. ✅ Execução de experimentos
4. ✅ Geração de validações
5. ✅ Criação de relatório estruturado (9 seções completas!)

---

## 🚀 Começe AGORA em 3 passos

### Passo 1: Instalar (5 min)
```bash
python scripts/automate.py install
python -m pytest -q
```

### Passo 2: Teste Rápido (10 min)
```bash
python scripts/execute_and_report.py --quick
```

Agora você tem:
- `outputs/` com imagens quantizadas
- `report/relatorio_final.md` - seu relatório!
- `EXECUCAO_RESUMO.txt` - resumo da execução

### Passo 3: Matriz Completa (45 min)
```bash
python scripts/execute_and_report.py --full
```

Você terá:
- 225+ experimentos executados
- Todas as imagens, figuras, métricas
- Relatório acadêmico completo

---

## 📋 Menu Interativo (Mais Fácil!)

```bash
python scripts/automate.py
```

Escolha a opção:
- **1**: Instalar
- **2**: Testes
- **3**: Demo (1 experimento)
- **4**: Matriz completa
- **5**: Teste rápido
- **6**: Gerar relatório
- **7**: Validar
- **8**: Limpar outputs
- **9**: Pipeline simples
- **10**: Pipeline com backup ⭐
- **0**: Sair

---

## 📊 O que cada passo produz

### Backup (automático)
```
outputs_execucao_20261007_143022/  ← Seus resultados antigos guardados!
```

### Resultados (em `outputs/`)
```
checkpoints/     ← 225+ modelos treinados
reconstructed/   ← 225+ imagens quantizadas
figures/         ← 225+ gráficos de análise
metrics/runs.csv ← Todos os dados (5+ MB)
tables/summary.csv ← Resumo agregado
```

### Relatório (em `report/`)
```
relatorio_final.md ← Seu trabalho acadêmico completo!
```

---

## 📖 Estrutura do Relatório Gerado

O arquivo `report/relatorio_final.md` inclui:

1. **Introdução** - Contexto, problema, motivação
2. **Fundamentação** - SOM, GNG, k-means, métricas
3. **Metodologia** - Hardware, protocolo, hiperparâmetros
4. **Validação** - Prova que tudo funciona
5. **Resultados Quantitativos** - Tabelas e números
6. **Resultados Qualitativos** - Imagens e gráficos
7. **Discussão** - Responde as 4 questões propostas
8. **Limitações** - Reconhece restrições
9. **Conclusão** - Síntese final
10. **Apêndices** - Instruções completas

**Todos os espaços já existem! Basta preencher com análises!**

---

## ⏱️ Tempos Esperados

| O que? | Tempo |
|--------|-------|
| Instalar | 5 min |
| Teste rápido | 10-15 min |
| Matriz completa (CPU) | 45-75 min |
| Matriz completa (GPU) | 10-15 min |

---

## 💾 Estrutura de Diretórios

Após execução:
```
projeto_2_redes_neurais/
├── outputs/                        ← Resultados NOVOS
├── outputs_execucao_20261007_143022/  ← Backup ANTIGO
├── report/
│   └── relatorio_final.md         ← SEU RELATÓRIO!
├── validation/
│   └── validation_unique_colors.csv
├── EXECUCAO_RESUMO.txt
├── AUTOMACAO_RESUMO.md
├── PIPELINE_COMPLETO.md
└── AUTOMATE_QUICK_START.md
```

---

## 🎯 Cenários Comuns

### "Quero testar rápido se tudo funciona"
```bash
python scripts/execute_and_report.py --quick
# Tempo: 10-15 min
# Resultado: Relatório completo em report/relatorio_final.md
```

### "Quero executar tudo completamente"
```bash
python scripts/execute_and_report.py --full
# Tempo: 45-75 min (CPU) ou 10-15 min (GPU)
# Resultado: Matriz completa + Relatório acadêmico
```

### "Quero menu amigável"
```bash
python scripts/automate.py
# Escolha opção 10 para pipeline com backup
```

### "Quero só limpeza + novo backup"
```bash
python scripts/execute_and_report.py --backup-only
python scripts/execute_and_report.py --clean-only
```

---

## ✨ Features Principais

### 🔄 Automação Inteligente
- Backup automático com timestamp
- Limpeza segura de outputs
- Execução orquestrada
- Geração de relatório

### 📁 Backup com Timestamp
```
outputs_execucao_20261007_143022/  ← Backup #1
outputs_execucao_20261007_102015/  ← Backup #2
outputs_execucao_20261007_081530/  ← Backup #3
```
Compare múltiplas execuções facilmente!

### 📊 Relatório Estruturado
Pronto para apresentação ou publicação, com:
- Todas as 9 seções de trabalho acadêmico
- Tabelas automáticas de métricas
- Referências às figuras geradas
- Espaços para análise manual
- Respostas às 4 questões propostas

### 🤖 Múltiplas Interfaces
- Menu interativo
- CLI com subcomandos
- Tarefas VS Code
- Makefile
- GitHub Actions
- PowerShell shortcuts

---

## 🎓 Próximos Passos

1. **Execute**: `python scripts/execute_and_report.py --quick`
2. **Aguarde**: 10-15 minutos
3. **Abra**: `report/relatorio_final.md`
4. **Análise**: Preencha as discussões com sua interpretação
5. **Completo**: Seu trabalho acadêmico está pronto!

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- **AUTOMACAO.md** - Guia completo e detalhado
- **AUTOMATE_QUICK_START.md** - Referência rápida
- **PIPELINE_COMPLETO.md** - Pipeline novo com backup
- **AUTOMACAO_RESUMO.md** - O que foi criado

---

## 🆘 Problemas Comuns

### "ModuleNotFoundError"
```bash
python scripts/automate.py install
```

### "Nenhuma imagem encontrada"
Copie pelo menos 1 imagem para `data/raw/`:
```bash
ls data/raw/
```

### "Quer rodar em GPU?"
GPU é automático se disponível. Controle com:
```python
# Em config/experiments.yaml
device: cuda  # ou cpu
```

---

**🎉 Tudo pronto! Basta executar e aguardar!**

```bash
python scripts/execute_and_report.py --quick
```

Seu relatório estará em `report/relatorio_final.md` 📄
