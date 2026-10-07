# Guia detalhado de execução
## Projeto 2: Quantização de cores com SOM, GNG e k-means

Este guia apresenta o processo completo para preparar o ambiente local, validar a implementação, organizar as imagens, executar os experimentos e gerar as evidências do relatório.

> **Atualização para Windows CMD:** os comandos para o Prompt de Comando do Windows foram incluídos. Para executar os testes, utilize preferencialmente `python -m pytest -q`, pois esse comando garante o uso do pytest associado ao interpretador Python da `.venv`.

---

# 1. Visão geral do fluxo

```text
1. Extrair o projeto
2. Abrir o terminal na raiz
3. Verificar o Python
4. Criar e ativar a .venv
5. Instalar as dependências
6. Preparar as imagens
7. Verificar os imports
8. Executar os testes com python -m pytest -q
9. Realizar uma execução reduzida
10. Inspecionar as evidências
11. Configurar os experimentos oficiais
12. Executar a matriz completa
13. Gerar tabelas e relatório
```

---

# 2. Requisitos

## 2.1 Software

- Python 3.10, 3.11 ou 3.12;
- `pip`;
- Prompt de Comando do Windows, PowerShell ou terminal Linux/macOS;
- editor ou IDE, preferencialmente Visual Studio Code ou PyCharm;
- Git, caso o projeto seja versionado.

## 2.2 Hardware

A implementação funciona em CPU. Uma GPU compatível com CUDA pode acelerar operações matriciais da SOM e do k-means, embora a GNG contenha etapas sequenciais.

Com cinco imagens principais, três modelos, três capacidades e cinco sementes, o protocolo produz:

```text
5 × 3 × 3 × 5 = 225 execuções
```

A imagem `00_controle_16_cores.png` pode ser usada separadamente na validação. Caso também seja incluída na matriz completa, o total passa para 270 execuções.

---

# 3. Estrutura esperada

```text
projeto_2_redes_neurais/
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt
├── config/
│   └── experiments.yaml
├── data/
│   ├── README.md
│   └── raw/
├── outputs/
│   ├── checkpoints/
│   ├── figures/
│   ├── metrics/
│   ├── reconstructed/
│   └── tables/
├── report/
├── scripts/
├── src/
└── tests/
```

Todos os comandos devem ser executados a partir da raiz do projeto.

---

# 4. Abrir o terminal na raiz

## 4.1 Windows: Prompt de Comando (CMD)

```cmd
cd /d C:\Projetos\projeto_2_redes_neurais
```

O parâmetro `/d` também altera a unidade de disco, quando necessário.

Confira o diretório e os arquivos:

```cmd
cd
dir
```

Devem aparecer, entre outros:

```text
src
tests
scripts
config
data
requirements.txt
```

## 4.2 Windows PowerShell

```powershell
cd C:\Projetos\projeto_2_redes_neurais
```

## 4.3 Linux ou macOS

```bash
cd ~/projetos/projeto_2_redes_neurais
```

---

# 5. Verificar o Python

## CMD, PowerShell, Linux ou macOS

```bash
python --version
```

No Windows, se necessário:

```cmd
py --version
```

É recomendável usar Python 3.10, 3.11 ou 3.12.

---

# 6. Criar o ambiente virtual

## Windows: CMD ou PowerShell

```cmd
python -m venv .venv
```

Alternativamente:

```cmd
py -m venv .venv
```

## Linux ou macOS

```bash
python3 -m venv .venv
```

---

# 7. Ativar o ambiente virtual

## 7.1 Windows: Prompt de Comando (CMD)

```cmd
.venv\Scripts\activate.bat
```

O terminal deverá passar a exibir algo semelhante a:

```text
(.venv) C:\Projetos\projeto_2_redes_neurais>
```

Confirme o interpretador:

```cmd
where python
python -c "import sys; print(sys.executable)"
```

O primeiro caminho e o valor de `sys.executable` devem apontar para:

```text
C:\Projetos\projeto_2_redes_neurais\.venv\Scripts\python.exe
```

É normal que `where python` também liste instalações globais depois do caminho da `.venv`. O Windows utiliza o primeiro caminho.

> No CMD não use `Set-ExecutionPolicy`. Esse comando é exclusivo do PowerShell.

## 7.2 Windows PowerShell

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## 7.3 Linux ou macOS

```bash
source .venv/bin/activate
```

## 7.4 Desativar o ambiente

```bash
deactivate
```

---

# 8. Atualizar o pip e instalar dependências

Com a `.venv` ativa:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Verifique o PyTorch:

```bash
python -c "import torch; print(torch.__version__)"
```

Verifique as demais bibliotecas:

```bash
python -c "import numpy, pandas, PIL, matplotlib, skimage, yaml; print('Dependencias OK')"
```

---

# 9. Verificar CPU e GPU

```bash
python -c "import torch; print('CUDA disponivel:', torch.cuda.is_available()); print('Dispositivo:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

Em CPU, mantenha:

```yaml
device: cpu
```

Se CUDA estiver corretamente disponível:

```yaml
device: cuda
```

Antes da rodada oficial, valide uma configuração isolada no dispositivo escolhido.

---

# 10. Preparar as imagens

Coloque os arquivos em:

```text
data/raw/
```

Conjunto recomendado:

```text
data/raw/
├── 00_controle_16_cores.png
├── 01_poucas_cores.png
├── 02_gradiente_suave.png
├── 03_alta_saturacao.png
├── 04_cor_rara.png
└── 05_cena_complexa.png
```

As imagens devem permanecer em PNG, RGB e 512 × 512 pixels. Não converta para JPEG, pois a compressão com perdas pode introduzir novas cores e artefatos.

A imagem `00_controle_16_cores.png` deve ser usada prioritariamente para validação. As imagens numeradas de `01` a `05` formam o conjunto experimental principal.

---

# 11. Configurar o pytest

Crie o arquivo `pytest.ini` na raiz:

```ini
[pytest]
pythonpath = .
testpaths = tests
addopts = -ra
```

Esse arquivo informa ao pytest que a raiz do projeto deve participar do caminho de importação e que os testes estão na pasta `tests`.

Verifique também a existência de:

```text
src/__init__.py
src/models/__init__.py
src/models/quantizers.py
```

No CMD:

```cmd
if exist src\__init__.py (echo src init OK) else (echo src init AUSENTE)
if exist src\models\__init__.py (echo models init OK) else (echo models init AUSENTE)
if exist src\models\quantizers.py (echo quantizers OK) else (echo quantizers AUSENTE)
```

---

# 12. Verificar os imports

Antes dos testes, execute:

```bash
python -c "import src; print(src.__file__)"
python -c "from src.models import SOM, GNG, TorchKMeans; print('Importacao OK')"
```

No Windows, o primeiro comando deverá apontar para algo semelhante a:

```text
C:\Projetos\projeto_2_redes_neurais\src\__init__.py
```

O segundo deverá imprimir:

```text
Importacao OK
```

---

# 13. Executar os testes

## Comando recomendado

```bash
python -m pytest -q
```

Prefira essa forma a apenas `pytest -q`. O comando `python -m pytest -q` garante que o pytest seja executado pelo mesmo interpretador associado ao comando `python`, isto é, o Python da `.venv` ativa.

## Sequência no Prompt de Comando

```cmd
cd /d C:\Projetos\projeto_2_redes_neurais
.venv\Scripts\activate.bat
where python
python -c "import sys; print(sys.executable)"
python -c "from src.models import SOM, GNG, TorchKMeans; print('Importacao OK')"
python -m pytest -q
```

Resultado esperado:

```text
...                                                                      [100%]
3 passed in X.XXs
```

## Por que `pytest -q` pode falhar?

No Windows pode existir um `pytest.exe` associado ao Python global, enquanto o projeto usa o Python da `.venv`. Nesse cenário, o executável global pode não incluir a raiz do projeto no caminho de importação, resultando em:

```text
ModuleNotFoundError: No module named 'src'
```

O diagnóstico pode ser feito com:

```cmd
where python
where pytest
```

Mesmo quando `where pytest` exibir um executável global, `python -m pytest -q` utiliza o interpretador da `.venv`, desde que ela esteja ativa.

---

# 14. Primeira execução de validação

Não inicie diretamente as 225 execuções. Teste uma imagem, uma capacidade e uma semente.

## CMD

```cmd
python scripts\run_single.py --image data\raw\01_poucas_cores.png --model som --capacity 16 --seed 13
```

## PowerShell, Linux ou macOS

```bash
python scripts/run_single.py --image data/raw/01_poucas_cores.png --model som --capacity 16 --seed 13
```

Argumentos:

- `--image`: arquivo de entrada;
- `--model`: `som`, `gng` ou `kmeans`;
- `--capacity`: `16`, `64` ou `256`;
- `--seed`: semente da execução.

Na SOM:

```text
16  → 4 × 4
64  → 8 × 8
256 → 16 × 16
```

---

# 15. Validar os três modelos

## CMD

```cmd
python scripts\run_single.py --image data\raw\01_poucas_cores.png --model som --capacity 16 --seed 13
python scripts\run_single.py --image data\raw\01_poucas_cores.png --model gng --capacity 16 --seed 13
python scripts\run_single.py --image data\raw\01_poucas_cores.png --model kmeans --capacity 16 --seed 13
```

Confirme a criação de arquivos em:

```text
outputs/checkpoints/
outputs/figures/
outputs/metrics/
outputs/reconstructed/
```

---

# 16. Evidências produzidas

Para cada execução, o projeto deve gerar:

- imagem reconstruída;
- comparação lado a lado;
- mapa de Delta E;
- histograma das diferenças RGB;
- histograma de vitórias;
- projeção RGB com protótipos;
- checkpoint;
- linha em `outputs/metrics/runs.csv`.

Principais métricas:

- erro de quantização;
- erro topológico para SOM e GNG;
- MAE, MSE e RMSE;
- PSNR;
- Delta E médio, desvio padrão e máximo;
- neurônios ativos e inativos;
- entropia de uso;
- tempo de treinamento e inferência.

---

# 17. Configuração dos experimentos

Arquivo:

```text
config/experiments.yaml
```

Configuração oficial sugerida:

```yaml
data_dir: data/raw
output_dir: outputs
device: cpu
seeds: [13, 37, 73, 101, 137]
capacities: [16, 64, 256]
models: [som, gng, kmeans]
max_train_pixels: 100000
inference_batch_size: 65536

som:
  epochs: 15
  batch_size: 512
  lr0: 0.5
  lrf: 0.05
  sigma_final: 0.5

gng:
  steps: 100000
  eps_b: 0.05
  eps_n: 0.0006
  insertion_interval: 100
  max_edge_age: 90
  alpha: 0.5
  beta: 0.005

kmeans:
  max_iter: 100
  tolerance: 0.0001
```

---

# 18. Configuração rápida de validação

Use temporariamente:

```yaml
seeds: [13]
capacities: [16]
models: [som, gng, kmeans]
max_train_pixels: 10000
inference_batch_size: 8192

som:
  epochs: 2
  batch_size: 256
  lr0: 0.5
  lrf: 0.05
  sigma_final: 0.5

gng:
  steps: 1000
  eps_b: 0.05
  eps_n: 0.0006
  insertion_interval: 100
  max_edge_age: 90
  alpha: 0.5
  beta: 0.005

kmeans:
  max_iter: 10
  tolerance: 0.0001
```

Não use esses valores reduzidos como resultados finais.

---

# 19. Limpar resultados preliminares

## CMD

```cmd
if exist outputs\metrics\runs.csv del outputs\metrics\runs.csv
if exist outputs\tables\summary.csv del outputs\tables\summary.csv
del /q outputs\reconstructed\* 2>nul
del /q outputs\figures\* 2>nul
del /q outputs\checkpoints\* 2>nul
```

Antes de apagar, considere renomear a pasta `outputs` para preservar a validação.

## PowerShell

```powershell
Remove-Item outputs\metrics\runs.csv -ErrorAction SilentlyContinue
Remove-Item outputs\tables\summary.csv -ErrorAction SilentlyContinue
Remove-Item outputs\reconstructed\* -Force -ErrorAction SilentlyContinue
Remove-Item outputs\figures\* -Force -ErrorAction SilentlyContinue
Remove-Item outputs\checkpoints\* -Force -ErrorAction SilentlyContinue
```

## Linux ou macOS

```bash
rm -f outputs/metrics/runs.csv
rm -f outputs/tables/summary.csv
rm -f outputs/reconstructed/*
rm -f outputs/figures/*
rm -f outputs/checkpoints/*
```

---

# 20. Executar o protocolo completo

Restaure a configuração oficial e execute:

## CMD

```cmd
python scripts\run_all.py --config config\experiments.yaml
```

## PowerShell, Linux ou macOS

```bash
python scripts/run_all.py --config config/experiments.yaml
```

Para as cinco imagens principais, são esperadas 225 execuções.

---

# 21. Monitorar a execução

## CMD

```cmd
find /c /v "" outputs\metrics\runs.csv
```

Com 225 resultados e um cabeçalho, o arquivo deve possuir 226 linhas.

## PowerShell

```powershell
(Get-Content outputs\metrics\runs.csv).Count
```

## Linux ou macOS

```bash
wc -l outputs/metrics/runs.csv
```

---

# 22. Evitar resultados duplicados

O script acrescenta linhas a `runs.csv`. Executar a mesma configuração novamente pode produzir duplicidade. Antes de reiniciar uma rodada:

1. faça backup de `runs.csv`;
2. identifique as execuções concluídas;
3. arquive ou limpe resultados preliminares;
4. registre a justificativa da nova rodada.

---

# 23. Gerar tabela e relatório

Ao fim da execução completa, o resumo deverá estar em:

```text
outputs/tables/summary.csv
```

Gere o relatório preliminar:

## CMD

```cmd
python scripts\generate_report.py
```

## Outros terminais

```bash
python scripts/generate_report.py
```

Saída esperada:

```text
report/relatorio_gerado.md
```

---

# 24. Interpretação básica

## Erro de quantização

Quanto menor, menor a distância média entre os pixels e seus protótipos.

## Erro topológico

- SOM: verifica se as duas BMUs são adjacentes na grade;
- GNG: verifica se há aresta entre os dois protótipos mais próximos;
- k-means: não se aplica.

## Delta E

Quanto menor, menor a diferença perceptual de cor no espaço CIELAB.

## PSNR

Em geral, quanto maior, mais próxima está a reconstrução da imagem original.

## Neurônios inativos

Muitos protótipos sem vitórias podem indicar treinamento insuficiente, redundância ou inadequação dos hiperparâmetros.

---

# 25. Evidências específicas por imagem

- `00_controle_16_cores.png`: verificar cobertura das regiões e uso dos protótipos;
- `01_poucas_cores.png`: observar bordas, janelas, caminho e pequenas cores;
- `02_gradiente_suave.png`: procurar faixas artificiais de cor;
- `03_alta_saturacao.png`: verificar a preservação dos matizes das pétalas;
- `04_cor_rara.png`: ampliar a região vermelha e comparar com métricas globais;
- `05_cena_complexa.png`: analisar barco, flores, montanhas, água e reflexos.

---

# 26. Solução de problemas

## `ModuleNotFoundError: No module named 'src'`

No CMD:

```cmd
cd /d C:\Projetos\projeto_2_redes_neurais
.venv\Scripts\activate.bat
python -c "import src; print(src.__file__)"
python -c "from src.models import SOM, GNG, TorchKMeans; print('Importacao OK')"
python -m pytest -q
```

Se os imports funcionarem e apenas `pytest -q` falhar, use `python -m pytest -q`.

## `No module named torch`

```cmd
python -m pip install -r requirements.txt
python -c "import torch; print(torch.__version__)"
```

## Imagem não encontrada

```cmd
dir data\raw
```

Confira o nome exato usado em `--image`.

## Falta de memória

Reduza no YAML:

```yaml
max_train_pixels: 25000
inference_batch_size: 8192
```

## Execução muito demorada

Use primeiro a configuração reduzida da seção 18. Depois, restaure os valores oficiais.

## GPU não reconhecida

```cmd
python -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```

Se o resultado for `False` e `None`, use `device: cpu` ou instale uma distribuição do PyTorch compatível com CUDA e com o hardware local.

---

# 27. Checklist de execução oficial

## Ambiente

- [ ] raiz do projeto correta;
- [ ] `.venv` criada e ativa;
- [ ] `sys.executable` aponta para `.venv`;
- [ ] dependências instaladas;
- [ ] imports de `src.models` funcionando;
- [ ] `python -m pytest -q` aprovado.

## Dados

- [ ] seis imagens em `data/raw/`;
- [ ] cinco imagens principais identificadas;
- [ ] imagem de controle separada;
- [ ] arquivos em PNG, RGB e 512 × 512;
- [ ] nomes preservados.

## Experimentos

- [ ] três modelos;
- [ ] capacidades 16, 64 e 256;
- [ ] cinco sementes;
- [ ] dispositivo registrado;
- [ ] resultados preliminares arquivados;
- [ ] 225 execuções principais concluídas.

## Relatório

- [ ] métricas consolidadas;
- [ ] média e desvio padrão;
- [ ] reconstruções selecionadas;
- [ ] mapas de Delta E;
- [ ] histogramas de vitórias;
- [ ] regiões de interesse ampliadas;
- [ ] limitações discutidas;
- [ ] conclusão fundamentada.

---

# 28. Sequência resumida para Windows CMD

```cmd
cd /d C:\Projetos\projeto_2_redes_neurais

python -m venv .venv

.venv\Scripts\activate.bat

where python

python -c "import sys; print(sys.executable)"

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

python -c "import src; print(src.__file__)"

python -c "from src.models import SOM, GNG, TorchKMeans; print('Importacao OK')"

python -m pytest -q

python scripts\run_single.py --image data\raw\01_poucas_cores.png --model som --capacity 16 --seed 13

python scripts\run_single.py --image data\raw\01_poucas_cores.png --model gng --capacity 16 --seed 13

python scripts\run_single.py --image data\raw\01_poucas_cores.png --model kmeans --capacity 16 --seed 13

python scripts\run_all.py --config config\experiments.yaml

python scripts\generate_report.py
```

---

# 29. Sequência resumida para PowerShell

```powershell
cd C:\Projetos\projeto_2_redes_neurais
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/run_all.py --config config/experiments.yaml
python scripts/generate_report.py
```

---

# 30. Sequência resumida para Linux ou macOS

```bash
cd ~/projetos/projeto_2_redes_neurais
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/run_all.py --config config/experiments.yaml
python scripts/generate_report.py
```

---

# Orientação final

No Windows CMD, a sequência comprovadamente adequada é:

```cmd
.venv\Scripts\activate.bat
python -m pytest -q
```

A adoção de `python -m pytest -q` evita o conflito observado quando `pytest -q` é resolvido por uma instalação global. Após a validação dos testes e das três execuções isoladas, arquive os resultados preliminares, restaure a configuração oficial e inicie a matriz completa.
