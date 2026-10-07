.PHONY: help install test single-demo quick-test full-matrix report validate clean pipeline interactive

help:
	@echo "==================================================================="
	@echo "🤖 Automação - Quantização de Cores com Redes Neurais"
	@echo "==================================================================="
	@echo ""
	@echo "Comandos disponíveis:"
	@echo ""
	@echo "  make install          Instalar dependências (pip install -r requirements.txt)"
	@echo "  make test             Executar testes unitários (pytest)"
	@echo "  make single-demo      Experimento único (SOM 16 cores, seed 13)"
	@echo "  make quick-test       Teste rápido (matriz reduzida)"
	@echo "  make full-matrix      Matriz completa de experimentos"
	@echo "  make report           Gerar relatório Markdown"
	@echo "  make validate         Validar cores únicas nos experimentos"
	@echo "  make clean            Limpar arquivos de saída"
	@echo "  make pipeline         Pipeline completo (install → test → full-matrix → report)"
	@echo "  make interactive      Menu interativo (padrão com 'python scripts/automate.py')"
	@echo "  make help             Exibir esta mensagem"
	@echo ""
	@echo "==================================================================="

install:
	@echo "📦 Instalando dependências..."
	python -m pip install -r requirements.txt
	@echo "✅ Dependências instaladas!"

test:
	@echo "🧪 Executando testes unitários..."
	python -m pytest -q
	@echo "✅ Testes concluídos!"

single-demo:
	@echo "🚀 Executando experimento único (demo)..."
	python scripts/run_single.py --image data/raw/00_controle_16_cores.png --model som --capacity 16 --seed 13
	@echo "✅ Experimento concluído!"

quick-test:
	@echo "⚡ Executando teste rápido (matriz reduzida)..."
	python scripts/run_all.py --config "config/experiments - teste rapido.yaml"
	@echo "✅ Teste rápido concluído!"

full-matrix:
	@echo "🔄 Executando matriz completa..."
	python scripts/run_all.py --config config/experiments.yaml
	@echo "✅ Matriz completa concluída!"

report:
	@echo "📊 Gerando relatório..."
	python scripts/generate_report.py
	@echo "✅ Relatório gerado!"

validate:
	@echo "✔️  Validando cores únicas..."
	python scripts/validate_unique_colors.py
	@echo "✅ Validação concluída!"

clean:
	@echo "🧹 Limpando arquivos de saída..."
	rm -rf outputs/checkpoints/*
	rm -rf outputs/reconstructed/*
	rm -rf outputs/figures/*
	rm -rf outputs/metrics/runs.csv
	rm -rf outputs/tables/summary.csv
	@echo "✅ Limpeza concluída!"

pipeline: install test full-matrix report validate
	@echo ""
	@echo "==================================================================="
	@echo "✅ Pipeline completo finalizado!"
	@echo "==================================================================="

interactive:
	@echo "🤖 Iniciando menu interativo..."
	python scripts/automate.py interactive

.DEFAULT_GOAL := help
