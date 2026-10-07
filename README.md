# Projeto 2 - Redes Neurais: Quantização de Cores

Implementação em Python + PyTorch de SOM, GNG e k-means, com execução reprodutível, métricas, gráficos e relatório.

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Coloque pelo menos cinco imagens em `data/raw/`.

## Execução
```bash
python scripts/run_single.py --image data/raw/exemplo.png --model som --capacity 16 --seed 13
python scripts/run_all.py --config config/experiments.yaml
python scripts/generate_report.py
pytest -q
```

## Evidências geradas
- imagens reconstruídas e checkpoints;
- erro de quantização e topológico;
- MAE, MSE, RMSE, PSNR e Delta E CIEDE2000;
- mapas Delta E, histogramas de diferenças e vitórias;
- neurônios ativos/inativos e entropia de uso;
- nuvem RGB com protótipos e grafo da GNG;
- tempos de treinamento e inferência;
- CSV por execução e resumo de média/desvio padrão;
- esqueleto de relatório Markdown.

A inferência e avaliação usam todos os pixels. A amostra de treinamento é mantida por imagem/semente para comparabilidade.
