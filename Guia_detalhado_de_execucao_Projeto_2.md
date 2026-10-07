# Guia detalhado de execução
## Projeto 2: Quantização de cores com SOM, GNG e k-means

Este guia apresenta o processo completo para preparar o ambiente, selecionar as imagens, validar a implementação, executar os experimentos e gerar as evidências do relatório. Recomenda-se realizar primeiro uma execução reduzida de validação e somente depois iniciar o protocolo completo, pois a matriz oficial pode chegar a **225 execuções** com cinco imagens.

---

# 1. Visão geral do fluxo de execução

O processo recomendado é:

```text
1. Baixar e extrair o projeto
2. Instalar o Python
3. Criar um ambiente virtual
4. Instalar as dependências
5. Selecionar e organizar as imagens
6. Executar os testes
7. Realizar uma execução de validação
8. Inspecionar as evidências produzidas
9. Configurar os hiperparâmetros
10. Executar o protocolo completo
11. Consolidar média e desvio padrão
12. Gerar o relatório preliminar
13. Analisar resultados e completar o relatório
```

---

# 2. Requisitos

## 2.1 Software necessário

Recomenda-se:

- Python 3.10, 3.11 ou 3.12;
- `pip`;
- terminal do Windows, PowerShell, Prompt de Comando ou terminal Linux;
- editor ou IDE, preferencialmente:
  - Visual Studio Code;
  - PyCharm;
  - JupyterLab, apenas para análises complementares.

## 2.2 Hardware

A implementação pode ser executada em CPU. Entretanto, o protocolo completo envolve:

- pelo menos cinco imagens;
- três algoritmos;
- três capacidades;
- cinco sementes.

Isso representa:

\[
5 \times 3 \times 3 \times 5 = 225
\]

execuções.

Uma GPU compatível com CUDA pode reduzir o tempo de algumas operações matriciais. Entretanto, a GNG possui operações sequenciais e gerenciamento de grafo, portanto seu ganho com GPU pode ser menor do que o obtido na SOM e no k-means.

## 2.3 Espaço em disco

O projeto gera, para cada execução:

- um checkpoint;
- uma imagem reconstruída;
- quatro figuras;
- uma linha no arquivo de métricas.

Para 225 execuções, podem ser produzidos mais de 900 arquivos gráficos. Reserve pelo menos alguns gigabytes, dependendo da resolução das imagens.

---

# 3. Download e extração

Baixe o arquivo ZIP do projeto e extraia-o para um diretório de sua preferência.

No Windows, um local possível é:

```text
C:\Projetos\projeto_2_redes_neurais
```

No Linux:

```text
~/projetos/projeto_2_redes_neurais
```

Depois da extração, a estrutura principal deverá ser semelhante a:

```text
projeto_2_redes_neurais/
├── config/
│   └── experiments.yaml
├── data/
│   └── raw/
├── outputs/
│   ├── checkpoints/
│   ├── figures/
│   ├── metrics/
│   ├── reconstructed/
│   └── tables/
├── report/
│   └── relatorio_final.md
├── scripts/
│   ├── generate_report.py
│   ├── run_all.py
│   └── run_single.py
├── src/
├── tests/
├── README.md
└── requirements.txt
```

---

# 4. Abrir o terminal no diretório do projeto

## Windows PowerShell

```powershell
cd C:\Projetos\projeto_2_redes_neurais
```

## Linux ou macOS

```bash
cd ~/projetos/projeto_2_redes_neurais
```

Confirme que o terminal está no diretório correto.

### Windows PowerShell

```powershell
Get-ChildItem
```

### Linux ou macOS

```bash
ls
```

Devem aparecer, entre outros:

```text
config
data
outputs
report
scripts
src
tests
requirements.txt
```

> Todos os comandos seguintes devem ser executados a partir da raiz do projeto.

---

# 5. Verificar a instalação do Python

Execute:

```bash
python --version
```

Se o comando não funcionar no Windows, experimente:

```powershell
py --version
```

O resultado deverá ser semelhante a:

```text
Python 3.11.9
```

Não é recomendável usar versões muito antigas do Python.

---

# 6. Criar um ambiente virtual

O ambiente virtual mantém as bibliotecas do projeto separadas das demais instalações do computador.

## Windows usando `py`

```powershell
py -m venv .venv
```

## Windows usando `python`

```powershell
python -m venv .venv
```

## Linux ou macOS

```bash
python3 -m venv .venv
```

Uma pasta chamada `.venv` será criada na raiz do projeto.

---

# 7. Ativar o ambiente virtual

## Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Se o PowerShell impedir a execução, utilize temporariamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois:

```powershell
.venv\Scripts\Activate.ps1
```

## Windows Prompt de Comando

```cmd
.venv\Scripts\activate.bat
```

## Linux ou macOS

```bash
source .venv/bin/activate
```

Quando o ambiente estiver ativo, o terminal normalmente apresentará:

```text
(.venv)
```

Para desativá-lo posteriormente:

```bash
deactivate
```

---

# 8. Atualizar o pip

Com o ambiente virtual ativo:

```bash
python -m pip install --upgrade pip
```

No Windows, também pode ser usado:

```powershell
py -m pip install --upgrade pip
```

---

# 9. Instalar as dependências

Execute:

```bash
pip install -r requirements.txt
```

Serão instaladas as bibliotecas principais:

- PyTorch;
- NumPy;
- pandas;
- Pillow;
- Matplotlib;
- scikit-image;
- PyYAML;
- pytest;
- tabulate.

A instalação do PyTorch pode levar alguns minutos.

## Verificação rápida

```bash
python -c "import torch; print(torch.__version__)"
```

Depois:

```bash
python -c "import numpy, pandas, PIL, matplotlib, skimage, yaml; print('Dependências carregadas com sucesso')"
```

Resultado esperado:

```text
Dependências carregadas com sucesso
```

---

# 10. Verificar CPU e GPU

Para verificar o dispositivo disponível:

```bash
python -c "import torch; print('CUDA disponível:', torch.cuda.is_available()); print('Dispositivo:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

Exemplo com CPU:

```text
CUDA disponível: False
Dispositivo: CPU
```

Exemplo com GPU:

```text
CUDA disponível: True
Dispositivo: NVIDIA ...
```

Se o comando informar `False`, mantenha no arquivo de configuração:

```yaml
device: cpu
```

Se CUDA estiver disponível e o PyTorch tiver suporte a CUDA, pode-se usar:

```yaml
device: cuda
```

> Antes do experimento completo, execute uma configuração isolada com CUDA. Isso permite detectar incompatibilidades sem comprometer uma longa sequência de execuções.

---

# 11. Preparar o conjunto de imagens

Coloque as imagens dentro de:

```text
data/raw/
```

Exemplo:

```text
data/raw/
├── 01_poucas_cores.png
├── 02_gradiente_suave.png
├── 03_alta_saturacao.jpg
├── 04_cor_rara.png
└── 05_cena_natural.jpg
```

## 11.1 Perfis recomendados

### Imagem 1: poucas cores dominantes

Pode ser:

- logotipo;
- ilustração vetorial;
- desenho;
- composição com áreas uniformes.

### Imagem 2: gradiente suave

Pode conter:

- céu;
- pôr do sol;
- fundo degradê;
- iluminação gradual.

### Imagem 3: alta saturação

Pode conter:

- flores;
- brinquedos;
- frutas;
- objetos coloridos.

### Imagem 4: objeto pequeno de cor rara

Deve conter uma pequena região com uma cor pouco frequente em relação ao restante da imagem.

Exemplo:

```text
um objeto vermelho pequeno sobre uma área predominantemente verde
```

### Imagem 5: cena natural complexa

Pode ser:

- paisagem;
- cena urbana;
- fotografia com texturas;
- composição com grande diversidade cromática.

## 11.2 Formatos aceitos

O carregador reconhece:

```text
.png
.jpg
.jpeg
.bmp
.tif
.tiff
.webp
```

## 11.3 Cuidados com os nomes

Prefira nomes simples:

```text
01_poucas_cores.png
02_gradiente.png
03_saturacao.jpg
04_cor_rara.png
05_paisagem.jpg
```

Evite inicialmente:

- caracteres especiais;
- nomes excessivamente longos;
- símbolos incomuns;
- vários arquivos com o mesmo nome-base.

## 11.4 Resolução

Para os primeiros testes, use imagens menores, por exemplo:

```text
256 × 256
512 × 512
```

Imagens muito grandes aumentam:

- tempo de inferência;
- tempo de geração das figuras;
- consumo de memória;
- tamanho dos arquivos de evidências.

O treinamento já limita a quantidade de pixels amostrados, mas a inferência e as métricas são calculadas sobre todos os pixels.

---

# 12. Executar os testes básicos

Com as dependências instaladas:

```bash
pytest -q
```

O resultado esperado deve indicar que os testes foram aprovados, por exemplo:

```text
3 passed
```

Os testes verificam:

- treinamento mínimo da SOM;
- treinamento mínimo da GNG;
- treinamento mínimo do k-means;
- formato da saída quantizada;
- respeito ao limite de neurônios da GNG.

## Em caso de erro de importação

Confirme que:

1. o terminal está na raiz do projeto;
2. o ambiente virtual está ativo;
3. as dependências foram instaladas;
4. existe uma pasta `src`.

Use:

```bash
python -c "import torch; print('PyTorch OK')"
```

---

# 13. Realizar a primeira execução de validação

Não inicie diretamente as 225 execuções. Realize primeiro um experimento simples.

## Windows PowerShell

```powershell
python scripts/run_single.py `
  --image data/raw/01_poucas_cores.png `
  --model som `
  --capacity 16 `
  --seed 13
```

## Windows Prompt de Comando

```cmd
python scripts/run_single.py --image data/raw/01_poucas_cores.png --model som --capacity 16 --seed 13
```

## Linux ou macOS

```bash
python scripts/run_single.py \
  --image data/raw/01_poucas_cores.png \
  --model som \
  --capacity 16 \
  --seed 13
```

## Significado dos argumentos

### `--image`

Caminho da imagem:

```text
--image data/raw/01_poucas_cores.png
```

### `--model`

Algoritmo:

```text
som
gng
kmeans
```

### `--capacity`

Número de protótipos ou neurônios:

```text
16
64
256
```

Na SOM:

```text
16  → grade 4 × 4
64  → grade 8 × 8
256 → grade 16 × 16
```

### `--seed`

Semente usada na inicialização e na amostragem:

```text
13
37
73
101
137
```

---

# 14. Verificar as saídas da primeira execução

Após uma execução bem-sucedida, examine as pastas a seguir.

## 14.1 Imagem reconstruída

```text
outputs/reconstructed/
```

Exemplo:

```text
01_poucas_cores_som_16_s13.png
```

## 14.2 Figuras

```text
outputs/figures/
```

São produzidos arquivos equivalentes a:

```text
01_poucas_cores_som_16_s13_comparison.png
01_poucas_cores_som_16_s13_deltae.png
01_poucas_cores_som_16_s13_hist.png
01_poucas_cores_som_16_s13_rgb.png
```

### `comparison`

Apresenta a imagem original e a reconstruída.

### `deltae`

Mapa de diferenças perceptuais calculadas por Delta E CIEDE2000.

### `hist`

Apresenta:

- histograma das diferenças RGB;
- distribuição das vitórias entre os protótipos.

### `rgb`

Apresenta:

- uma amostra dos pixels no espaço RGB;
- os protótipos aprendidos;
- conexões quando aplicável.

## 14.3 Checkpoint

```text
outputs/checkpoints/
```

O checkpoint contém:

- protótipos;
- histórico de treinamento;
- estrutura da rede;
- conexões da GNG, quando aplicável.

## 14.4 Métricas

```text
outputs/metrics/runs.csv
```

Cada execução adiciona uma linha ao arquivo.

Entre as colunas estão:

```text
run_id
image_name
model
capacity_requested
capacity_actual
seed
train_pixels
total_pixels
quantization_error
topographic_error
mae_rgb
mse_rgb
rmse_rgb
psnr
mean_delta_e
std_delta_e
max_delta_e
active_neurons
inactive_neurons
usage_entropy
training_time_s
inference_time_s
device
```

---

# 15. Validar separadamente os três modelos

Antes da execução completa, execute uma configuração de cada modelo.

## SOM

```bash
python scripts/run_single.py --image data/raw/01_poucas_cores.png --model som --capacity 16 --seed 13
```

## GNG

```bash
python scripts/run_single.py --image data/raw/01_poucas_cores.png --model gng --capacity 16 --seed 13
```

## k-means

```bash
python scripts/run_single.py --image data/raw/01_poucas_cores.png --model kmeans --capacity 16 --seed 13
```

Depois, compare visualmente:

```text
outputs/reconstructed/
```

E verifique os três novos registros em:

```text
outputs/metrics/runs.csv
```

---

# 16. Configurar os experimentos

O arquivo principal é:

```text
config/experiments.yaml
```

Configuração inicial:

```yaml
data_dir: data/raw
output_dir: outputs
device: cpu

seeds: [13, 37, 73, 101, 137]

capacities: [16, 64, 256]

models:
  - som
  - gng
  - kmeans

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

## 16.1 `data_dir`

Diretório das imagens:

```yaml
data_dir: data/raw
```

## 16.2 `output_dir`

Diretório das evidências:

```yaml
output_dir: outputs
```

## 16.3 `device`

CPU:

```yaml
device: cpu
```

GPU:

```yaml
device: cuda
```

## 16.4 `seeds`

As cinco sementes obrigatórias:

```yaml
seeds: [13, 37, 73, 101, 137]
```

Não altere as sementes durante uma mesma rodada comparativa.

## 16.5 `capacities`

```yaml
capacities: [16, 64, 256]
```

Permite comparar os algoritmos com a mesma capacidade nominal.

## 16.6 `max_train_pixels`

```yaml
max_train_pixels: 100000
```

Se uma imagem possuir mais de 100.000 pixels, será selecionada uma amostra de treinamento. Todos os pixels permanecem na inferência e na avaliação.

Para um teste rápido:

```yaml
max_train_pixels: 10000
```

Para a execução oficial:

```yaml
max_train_pixels: 100000
```

## 16.7 `inference_batch_size`

```yaml
inference_batch_size: 65536
```

Se ocorrer falta de memória:

```yaml
inference_batch_size: 16384
```

Ou:

```yaml
inference_batch_size: 8192
```

---

# 17. Configuração da SOM

## Número de épocas

```yaml
epochs: 15
```

Para teste rápido:

```yaml
epochs: 2
```

Para experimentação oficial:

```yaml
epochs: 15
```

Posteriormente, pode-se avaliar:

```text
10, 15, 30 ou 50 épocas
```

## Tamanho do lote

```yaml
batch_size: 512
```

Valores menores reduzem o consumo por operação, mas podem aumentar o tempo.

## Taxa inicial

```yaml
lr0: 0.5
```

## Taxa final

```yaml
lrf: 0.05
```

## Raio final

```yaml
sigma_final: 0.5
```

Esse parâmetro é particularmente relevante para discutir o efeito da vizinhança final sobre:

- erro de quantização;
- preservação topológica;
- organização dos protótipos.

Uma análise complementar pode comparar:

```text
sigma_final = 0.1
sigma_final = 0.5
sigma_final = 1.0
```

Não misture resultados de configurações diferentes sem registrá-las separadamente.

---

# 18. Configuração da GNG

## Número de passos

```yaml
steps: 100000
```

Para teste rápido:

```yaml
steps: 1000
```

Para validação intermediária:

```yaml
steps: 10000
```

Para execução oficial:

```yaml
steps: 100000
```

## Taxa do vencedor

```yaml
eps_b: 0.05
```

## Taxa dos vizinhos

```yaml
eps_n: 0.0006
```

A taxa dos vizinhos deve ser menor que a taxa do vencedor.

## Intervalo de inserção

```yaml
insertion_interval: 100
```

A cada 100 apresentações, a rede verifica a inserção de uma nova unidade.

## Idade máxima das conexões

```yaml
max_edge_age: 90
```

Conexões mais antigas que esse limite são removidas.

## Redução local do erro

```yaml
alpha: 0.5
```

## Decaimento global

```yaml
beta: 0.005
```

---

# 19. Configuração do k-means

## Número máximo de iterações

```yaml
max_iter: 100
```

## Tolerância

```yaml
tolerance: 0.0001
```

O treinamento termina quando o deslocamento dos centroides fica abaixo da tolerância ou quando o limite de iterações é atingido.

---

# 20. Configuração rápida para validação

Antes da execução oficial, pode-se editar temporariamente o arquivo:

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

Essa configuração não deverá ser usada como resultado final. Sua finalidade é apenas verificar:

- leitura das imagens;
- execução dos modelos;
- escrita dos arquivos;
- geração dos gráficos;
- funcionamento das métricas.

---

# 21. Limpar resultados de testes anteriores

O programa acrescenta novas linhas ao arquivo:

```text
outputs/metrics/runs.csv
```

Portanto, antes da execução oficial, remova os resultados preliminares.

## Windows PowerShell

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

> Faça essa limpeza somente se os arquivos anteriores não precisarem ser preservados.

Uma alternativa mais segura é renomear a pasta:

```text
outputs
```

para:

```text
outputs_validacao
```

Depois, recriar uma pasta `outputs`.

---

# 22. Executar o protocolo completo

Restaure no arquivo de configuração:

```yaml
seeds: [13, 37, 73, 101, 137]
capacities: [16, 64, 256]
models: [som, gng, kmeans]
```

Em seguida:

```bash
python scripts/run_all.py --config config/experiments.yaml
```

O terminal apresentará cada combinação:

```text
01_poucas_cores.png som 16 13
01_poucas_cores.png som 16 37
01_poucas_cores.png som 16 73
...
```

## Recomendação

Não feche o terminal enquanto o processo estiver em execução.

No Windows:

- desative temporariamente a suspensão automática;
- mantenha o computador conectado à energia;
- verifique espaço disponível;
- evite iniciar aplicações muito pesadas simultaneamente.

---

# 23. Monitorar a execução

Durante o experimento, acompanhe:

```text
outputs/metrics/runs.csv
```

O número de linhas deverá crescer à medida que as execuções terminam.

Para cinco imagens, o total esperado é:

```text
225 linhas de resultados
```

Além do cabeçalho.

## Contar as linhas no PowerShell

```powershell
(Get-Content outputs\metrics\runs.csv).Count
```

Se houver 225 execuções e um cabeçalho:

```text
226
```

## Contar no Linux

```bash
wc -l outputs/metrics/runs.csv
```

Resultado esperado:

```text
226 outputs/metrics/runs.csv
```

---

# 24. Evitar duplicidade de resultados

Se o comando `run_all.py` for executado novamente sem limpar o CSV, as mesmas configurações serão acrescentadas outra vez.

Antes de reiniciar uma rodada completa:

1. faça uma cópia de `runs.csv`;
2. verifique quais execuções terminaram;
3. remova duplicidades ou limpe as saídas;
4. registre a razão da nova execução.

Sugestão de backup:

```text
outputs/metrics/runs_rodada_01.csv
```

---

# 25. Gerar a tabela agregada

Ao fim de `run_all.py`, o projeto gera:

```text
outputs/tables/summary.csv
```

O arquivo apresenta, por imagem, modelo e capacidade:

- média;
- desvio padrão;
- erro de quantização;
- erro topológico;
- Delta E;
- métricas RGB;
- utilização dos neurônios;
- tempo de treinamento;
- tempo de inferência.

É importante verificar se cada grupo possui cinco sementes.

---

# 26. Gerar o relatório preliminar

Execute:

```bash
python scripts/generate_report.py
```

O relatório será gerado em:

```text
report/relatorio_gerado.md
```

Esse arquivo inclui:

- estrutura de seções;
- tabela quantitativa agregada;
- espaços para a discussão;
- orientações para inserção das evidências.

O relatório gerado não substitui a análise acadêmica. Ele consolida os dados, mas ainda será necessário escrever:

- interpretação dos resultados;
- comparação entre redes;
- análise das imagens;
- resposta às quatro questões da proposta;
- limitações;
- conclusão.

---

# 27. Interpretar as principais métricas

## Erro de quantização

Quanto menor, mais próximo cada pixel ficou de seu protótipo.

\[
QE =
\frac{1}{N}
\sum_{i=1}^{N}
\|\mathbf{x}_i-\mathbf{w}_{b(i)}\|_2
\]

Interpretação:

```text
menor QE → menor distorção no espaço RGB
```

## Erro topológico

Na SOM, verifica se as duas unidades mais próximas são adjacentes na grade.

Na GNG, verifica se os dois protótipos mais próximos possuem uma aresta entre si.

Interpretação:

```text
menor erro topológico → melhor preservação das relações de vizinhança
```

O erro topológico não é calculado para k-means porque esse algoritmo não possui uma topologia entre os centroides.

## Delta E

Representa a diferença perceptual de cor no espaço CIELAB.

Interpretação geral:

```text
menor Delta E → menor diferença perceptual
```

Compare:

- média;
- desvio padrão;
- valor máximo;
- distribuição espacial no mapa de erro.

## PSNR

Em geral:

```text
maior PSNR → reconstrução mais próxima da imagem original
```

## Neurônios inativos

Um protótipo é considerado inativo quando não vence para nenhum pixel.

Muitos neurônios inativos podem indicar:

- configuração inadequada;
- treinamento insuficiente;
- redundância de protótipos;
- desequilíbrio na distribuição das cores.

## Entropia de uso

Indica quão distribuídas foram as vitórias entre os protótipos.

Não deve ser interpretada isoladamente. Uma distribuição uniforme pode ser positiva, mas imagens com poucas cores dominantes naturalmente podem produzir utilização desigual.

---

# 28. Selecionar evidências para o relatório

Não é recomendável inserir todas as centenas de figuras no corpo principal.

## Corpo do relatório

Selecione:

- uma comparação representativa por perfil de imagem;
- uma comparação entre 16, 64 e 256 cores;
- um mapa Delta E importante;
- um caso de preservação de cor rara;
- um caso de falha em gradiente;
- uma projeção RGB da SOM;
- uma projeção RGB da GNG;
- gráficos agregados das métricas.

## Apêndice

Inclua:

- tabelas completas;
- hiperparâmetros;
- resultados por semente;
- figuras adicionais;
- instruções de reprodução;
- versões das bibliotecas.

---

# 29. Responder às questões da proposta

## 29.1 Erro topológico versus qualidade visual

Compare o erro topológico com:

- Delta E;
- erro de quantização;
- PSNR;
- reconstruções lado a lado;
- mapas de erro.

Não assuma que menor erro topológico produz sempre melhor imagem. A topologia representa organização dos protótipos, enquanto a qualidade visual depende também da posição deles no espaço de cores.

## 29.2 SOM versus k-means com o mesmo número de protótipos

A SOM atualiza:

- a BMU;
- os neurônios vizinhos.

O k-means ajusta cada centro diretamente ao grupo atribuído. Por isso, uma vizinhança final não nula pode impedir os protótipos da SOM de se especializarem tanto quanto os centroides do k-means.

A evidência deverá combinar:

- erro de quantização;
- raio final;
- distribuição dos protótipos;
- qualidade visual.

## 29.3 Tipo de imagem em que cada rede se destaca

Analise separadamente:

- poucas cores;
- gradientes;
- alta saturação;
- cor rara;
- cena complexa.

Evite uma conclusão genérica baseada somente na média geral.

## 29.4 Métricas versus percepção visual

Verifique situações como:

- PSNR melhor, mas perda de uma cor rara;
- erro médio baixo, mas degradação localizada;
- Delta E médio semelhante, mas mapas espacialmente diferentes;
- bom erro topológico, mas maior distorção RGB.

---

# 30. Solução de problemas

## Erro: `No module named torch`

Instale as dependências com o ambiente ativo:

```bash
pip install -r requirements.txt
```

Verifique:

```bash
python -c "import torch; print(torch.__version__)"
```

## Erro: arquivo de imagem não encontrado

Confira o nome:

```bash
python scripts/run_single.py --image data/raw/01_poucas_cores.png --model som --capacity 16 --seed 13
```

Liste a pasta:

### Windows

```powershell
Get-ChildItem data\raw
```

### Linux

```bash
ls data/raw
```

## Erro de memória

Reduza:

```yaml
max_train_pixels: 25000
inference_batch_size: 8192
```

Se estiver usando CUDA, faça uma tentativa em CPU:

```yaml
device: cpu
```

## Execução muito demorada

Para validação:

```yaml
seeds: [13]
capacities: [16]
max_train_pixels: 10000
```

E:

```yaml
som:
  epochs: 2
```

```yaml
gng:
  steps: 1000
```

```yaml
kmeans:
  max_iter: 10
```

Depois da validação, restaure a configuração oficial.

## Arquivo `runs.csv` com resultados repetidos

Isso normalmente ocorre quando uma configuração já concluída foi executada outra vez. Faça backup do arquivo, remova duplicidades ou limpe as saídas antes de uma nova rodada oficial.

## O PyTorch não reconhece a GPU

Execute:

```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```

Se o resultado for:

```text
False
None
```

a instalação atual do PyTorch não possui suporte CUDA ou o ambiente não está corretamente configurado. Nesse caso, use CPU até instalar uma distribuição apropriada.

## O relatório não é gerado

Verifique se existe:

```text
outputs/metrics/runs.csv
```

O relatório depende da existência de resultados experimentais.

---

# 31. Checklist de execução oficial

## Ambiente

- [ ] Python instalado;
- [ ] ambiente virtual criado;
- [ ] ambiente virtual ativo;
- [ ] dependências instaladas;
- [ ] testes executados.

## Dados

- [ ] pelo menos cinco imagens;
- [ ] perfis visuais distintos;
- [ ] formatos reconhecidos;
- [ ] nomes organizados;
- [ ] resolução documentada.

## Validação

- [ ] SOM executada com 16 neurônios;
- [ ] GNG executada com 16 neurônios;
- [ ] k-means executado com 16 centroides;
- [ ] imagens reconstruídas verificadas;
- [ ] figuras verificadas;
- [ ] CSV inspecionado.

## Execução oficial

- [ ] resultados preliminares removidos ou arquivados;
- [ ] cinco sementes configuradas;
- [ ] capacidades 16, 64 e 256;
- [ ] três modelos configurados;
- [ ] hiperparâmetros registrados;
- [ ] dispositivo registrado;
- [ ] execução completa iniciada;
- [ ] 225 execuções confirmadas.

## Evidências

- [ ] reconstruções;
- [ ] mapas Delta E;
- [ ] histogramas de diferenças;
- [ ] histogramas de vitórias;
- [ ] neurônios ativos e inativos;
- [ ] projeções RGB;
- [ ] grafo da GNG;
- [ ] tempos de treinamento e inferência;
- [ ] tabela de média e desvio padrão.

## Relatório

- [ ] metodologia descrita;
- [ ] ambiente computacional informado;
- [ ] imagens caracterizadas;
- [ ] hiperparâmetros apresentados;
- [ ] resultados quantitativos;
- [ ] resultados qualitativos;
- [ ] quatro questões respondidas;
- [ ] limitações discutidas;
- [ ] conclusão fundamentada.

---

# 32. Sequência resumida de comandos

## Windows PowerShell

```powershell
cd C:\Projetos\projeto_2_redes_neurais

py -m venv .venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

pytest -q

python scripts/run_single.py --image data/raw/01_poucas_cores.png --model som --capacity 16 --seed 13

python scripts/run_single.py --image data/raw/01_poucas_cores.png --model gng --capacity 16 --seed 13

python scripts/run_single.py --image data/raw/01_poucas_cores.png --model kmeans --capacity 16 --seed 13

python scripts/run_all.py --config config/experiments.yaml

python scripts/generate_report.py
```

## Linux ou macOS

```bash
cd ~/projetos/projeto_2_redes_neurais

python3 -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

pip install -r requirements.txt

pytest -q

python scripts/run_single.py \
  --image data/raw/01_poucas_cores.png \
  --model som \
  --capacity 16 \
  --seed 13

python scripts/run_single.py \
  --image data/raw/01_poucas_cores.png \
  --model gng \
  --capacity 16 \
  --seed 13

python scripts/run_single.py \
  --image data/raw/01_poucas_cores.png \
  --model kmeans \
  --capacity 16 \
  --seed 13

python scripts/run_all.py --config config/experiments.yaml

python scripts/generate_report.py
```

---

# Orientação final

A sequência mais segura é executar primeiro **uma imagem, uma capacidade e uma semente**. Depois de validar SOM, GNG e k-means, arquive ou limpe as evidências preliminares, restaure a configuração oficial e execute as 225 combinações.

O guia foi organizado para separar claramente preparação, validação, execução oficial, interpretação das métricas e construção do relatório. Isso reduz o risco de misturar resultados de testes rápidos com os resultados experimentais definitivos.
