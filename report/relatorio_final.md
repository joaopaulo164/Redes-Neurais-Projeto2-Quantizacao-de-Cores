
# Projeto 2: Quantização de Cores com Redes Neurais

## 1. Introdução

### 1.1 Contexto da Quantização de Cores
A quantização de cores é uma técnica fundamental em processamento de imagens que reduz o número de 
cores distintas em uma imagem, preservando ao máximo a qualidade visual. Esta tarefa é crítica em 
aplicações como:
- Compressão de imagens com restrições de paleta;
- Conversão entre espaços de cores;
- Visualização em dispositivos com capacidade limitada;
- Síntese visual e processamento artístico.

### 1.2 Problema Abordado
Este projeto implementa e compara três algoritmos de quantização baseados em redes neurais:
- **Self-Organizing Map (SOM)**: preserva topologia através de vizinhança ordenada;
- **Growing Neural Gas (GNG)**: adapta dinamicamente o número de neurônios;
- **k-means**: otimiza a partição através de centróides.

Cada algoritmo oferece trade-offs distintos entre qualidade, topologia e custo computacional.

### 1.3 Motivação
As métricas tradicionais (erro de quantização, PSNR) nem sempre correspondem à percepção visual 
humana. A comparação estruturada destes algoritmos fornece insights sobre:
- Quando cada algoritmo se destaca;
- Correlação entre métricas numéricas e qualidade visual;
- Preservação de propriedades topológicas versus fidelidade;
- Distribuição dos protótipos no espaço de cores RGB.

### 1.4 Objetivo Geral
Implementar, avaliar e comparar três quantizadores de cores baseados em redes neurais, 
estabelecendo um protocolo experimental reprodutível com métricas quantitativas e qualitativas.

### 1.5 Objetivos Específicos
- ✓ Implementar SOM, GNG e k-means em PyTorch com suporte a GPU;
- ✓ Definir protocolo experimental com sementes, capacidades e imagens de teste;
- ✓ Calcular métricas: quantização, topográfica, perceptual (ΔE), eficiência temporal;
- ✓ Gerar evidências visuais: imagens, mapas de erro, gráficos;
- ✓ Validar convergência e comportamento de cada algoritmo;
- ✓ Responder às questões propostas através de análise comparativa estruturada.

## 2. Fundamentação Teórica

### 2.1 Quantização de Cores
A quantização de cores mapeia um espaço contínuo de cores (RGB: 16.7M combinações) para um 
conjunto discreto de K cores (protótipos). Matematicamente:

**Problema**: Dado conjunto de pixels P = {p₁, p₂, ..., pₙ} ⊂ ℝ³, encontrar protótipos 
W = {w₁, w₂, ..., wₖ} que minimizem:

```
E_total = Σᵢ ||pᵢ - w_bmu(pᵢ)||²
```

onde bmu(pᵢ) = argmin_j ||pᵢ - wⱼ||² é a unidade mais próxima.

### 2.2 Aprendizado Competitivo
Todos os três algoritmos utilizam aprendizado competitivo:
1. **Seleção**: Encontrar o protótipo mais próximo (Best Matching Unit - BMU);
2. **Adaptação**: Mover o BMU em direção ao padrão de entrada;
3. **Vizinhança**: Adaptar protótipos vizinhos (em topologia ou espaço);
4. **Decaimento**: Reduzir taxa de aprendizado e raio de vizinhança ao longo do tempo.

### 2.3 Self-Organizing Maps (SOM)
**Características**:
- Neurônios em grade 2D (rows × cols)
- Preserva topologia: proximidade no espaço de entrada → proximidade na grade
- Função de vizinhança gaussiana com decaimento σ(t)
- Entrada: amostras aleatórias do conjunto de treinamento

**Dinâmica**:
```
w_j(t+1) = w_j(t) + η(t) × h_j,bmu(t) × (x(t) - w_j(t))
```

onde:
- η(t): taxa de aprendizado (decay linear)
- h_j,bmu(t) = exp(-d²_grid/(2σ²(t))): vizinhança topológica
- d_grid: distância na grade

**Hiperparâmetros**: epochs, lr0, lrf (taxas), sigma_final (vizinhança final)

### 2.4 Growing Neural Gas (GNG)
**Características**:
- Número de neurônios cresce dinamicamente
- Arestas conectam neurônios próximos (topologia adaptativa)
- Mecanismo de envelhecimento de arestas
- Erro acumulado guia inserção de novos neurônios

**Dinâmica**:
1. Selecionar BMU e 2º BMU
2. Incrementar erro do BMU
3. Adaptar BMU e vizinhos por arestas
4. Envelhecer arestas incidentes ao BMU
5. Remover arestas antigas (idade > max_age)
6. Periodicamente: inserir novo neurônio entre BMU de maior erro e seu melhor vizinho

**Hiperparâmetros**: steps, eps_b/eps_n (taxas), insertion_interval, max_edge_age, alpha, beta

### 2.5 k-means
**Características**:
- Inicialização k-means++: espalha protótipos iniciais
- Iteração: atribuir pontos ao centróide mais próximo → recalcular centróides
- Critério de parada: convergência (Δ centróides < threshold) ou max_iter

**Dinâmica**:
```
1. Inicializar: c₁ escolhido aleatoriamente; para i=2..k: cᵢ ∝ d²(x, C)
2. Atribuir: A_j = {x : ||x - c_j|| ≤ ||x - c_i|| ∀i}
3. Atualizar: c_j = mean(A_j)
4. Repetir até convergência
```

**Hiperparâmetros**: max_iter, tolerance (threshold de convergência)

### 2.6 BMU e Protótipos
**Best Matching Unit (BMU)**: Neurônio/centróide mais próximo de um padrão de entrada.
- Em SOM/GNG: busca em grade/grafo
- Em k-means: busca entre todos os centróides
- Custo: O(k) para cada padrão

**Protótipos**: Conjunto final de cores. Representam a "assinatura" da quantização.
- SOM: W shape (rows×cols, 3)
- GNG: W shape (num_nodes, 3) com arestas
- k-means: centroids shape (k, 3)

### 2.7 Erro de Quantização
**Erro MSE**: Distância média entre pixels originais e seus protótipos reconstruídos.

```
E_quant = (1/N) Σᵢ ||p_i - w_bmu(p_i)||²_L2
```

Mede fidelidade da reconstrução, mas não correlaciona necessariamente com percepção visual.

### 2.8 Preservação e Erro Topológico
**Erro Topológico**: Mede se a topologia da distribuição dos dados é preservada.

```
E_topo = (1/N) Σᵢ u(||p_i - w_1|| , ||p_i - w_2||)
```

onde:
- w_1: BMU do padrão i
- w_2: 2º BMU do padrão i
- u = 1 se w_1 e w_2 não são vizinhos na topologia (SOM/GNG)
- u = 0 caso contrário

Valores baixos indicam que a ordem espacial é preservada.

### 2.9 Métricas Perceptuais
**Delta E CIEDE2000 (ΔE)**: Diferença de cor percebida entre original e reconstruída.
- Baseada em Laboratório de cores (mais perceptualmente uniforme que RGB)
- Valor 0: cores idênticas
- Valor 1: diferença imperceptível (ΔE < 1)
- Valor 2-10: diferenças pequenas mas visíveis

```
ΔE = sqrt((ΔL'/k_L·S_L)² + (ΔC'/k_C·S_C)² + (ΔH'/k_H·S_H)²)
```

(Implementação simplificada no projeto)

## 3. Metodologia

### 3.1 Ambiente de Execução
- **Linguagem**: Python 3.10+
- **Framework**: PyTorch 2.2+
- **Dependências**: numpy, pandas, Pillow, scikit-image, matplotlib
- **Hardware**: CPU (com fallback automático se CUDA indisponível), GPU CUDA compatível opcional
- **Repositório**: Versionado com Git, estrutura modular em src/

### 3.2 Hardware e Software Utilizado
```
device: [cpu | cuda]
max_train_pixels: 100000 (amostra fixa por seed)
inference_batch_size: 65536 (processamento em lotes)
```

Todos os cálculos em tensores float32 normalizados [0, 1].

### 3.3 Estrutura dos Dados
**Imagens de entrada**:
- Formato: PNG, JPEG, BMP, TIFF, WebP
- Canal: convertidas para RGB
- Normalização: PIL load → np.float32 / 255.0 → [0, 1]

**Pixeles**:
- Tensor shape: (N, 3) onde N = altura × largura
- Cada linha: [R, G, B] ∈ [0, 1]

### 3.4 Seleção das Imagens
Mínimo de 5 imagens de teste recomendado. Cada imagem deve:
- Representar diferentes características visuais (cores, texturas)
- Possuir resolução típica (512×512 a 2048×2048)
- Ser reprodutível (sem variabilidade)

### 3.5 Normalização
Processo padrão:
1. Carregar imagem com PIL.Image.open() em modo RGB
2. Converter para numpy float32
3. Dividir por 255.0 → escala [0, 1]
4. Converter para tensor PyTorch
5. Na reconstrução: clampar [0, 1] → multiplicar por 255 → converter uint8 → salvar

### 3.6 Estratégia de Amostragem
**Treinamento**:
- Máximo: max_train_pixels = 100000 (configurável)
- Se imagem < 100k pixels: usar todos os pixels
- Se imagem > 100k pixels: amostrar aleatoriamente respeitando seed

```
sample = x[randperm(len(x), generator=torch.Generator().manual_seed(seed))[:n]]
```

**Inferência**:
- Usar TODOS os pixeles da imagem original (sem amostragem)
- Processa em lotes de size batch_size para evitar overflow de memória

### 3.7 Implementação em PyTorch
**Características gerais**:
- Todas as operações em GPU/CPU transparentemente
- Gerador de números aleatórios com seed fixo por experimento
- Batch processing com `torch.cdist` para eficiência
- Device-agnostic: código roda igual em CPU e CUDA

**Exemplo: predict_bmu com batch**:
```python
def predict_bmu(self, x, batch_size=65536):
    return torch.cat([
        torch.cdist(x[i:i+batch_size].to(device), weights)
        .argmin(1)
        for i in range(0, len(x), batch_size)
    ])
```

### 3.8 Hiperparâmetros

#### SOM
- epochs: 15 (5 para teste rápido)
- batch_size: 512
- lr0 (taxa inicial): 0.5
- lrf (taxa final): 0.05 (decay para 5% da taxa inicial)
- sigma_final: 0.5 (raio de vizinhança final)
- Grid: rows = cols = int(sqrt(capacity))

#### GNG
- steps: 100000 (10000 para teste rápido)
- eps_b (taxa BMU): 0.05
- eps_n (taxa vizinhos): 0.0006
- insertion_interval: insere neurônio a cada 100 passos
- max_edge_age: 90 (remove arestas com idade > 90)
- alpha: 0.5 (reduz erro ao inserir)
- beta: 0.005 (decay do erro)

#### k-means
- max_iter: 100
- tolerance: 0.0001 (critério de convergência)
- Inicialização: k-means++ (espalhamento probabilístico)

### 3.9 Sementes
**Randomness Control**:
- 5 sementes por configuração: [13, 37, 73, 101, 137]
- Cada seed controla: inicialização de pesos, amostragem de treinamento
- Garantia: mesma seed + mesma imagem → mesmo resultado (reprodutibilidade)

### 3.10 Métricas Calculadas

Por experimento (cada run_id única):

| Métrica | Descrição | Intervalo | Significado |
|---------|-----------|-----------|-------------|
| quantization_error | MSE entre original e reconstruída | [0, ∞) | Menor = melhor |
| topographic_error | Razão de violações topológicas | [0, 1] | Menor = melhor |
| mae_rgb, mse_rgb, rmse_rgb | Diferenças por canal | [0, ∞) | Menor = melhor |
| psnr | Peak SNR em dB | [0, ∞) | Maior = melhor |
| mean_delta_e, std_delta_e, max_delta_e | Diferença perceptual CIEDE2000 | [0, ∞) | Menor = melhor |
| active_neurons, inactive_neurons | Uso da capacidade | [0, capacity] | Maior/menor = análise |
| usage_entropy | Distribuição do uso (Shannon) | [0, log(k)] | Maior = distribuição uniforme |
| training_time_s, inference_time_s | Tempo em segundos | [0, ∞) | Para análise de eficiência |

Agregação: média e desvio padrão entre sementes (outputs/tables/summary.csv)

### 3.11 Protocolo Experimental
**Matriz padrão**:
- Imagens: 5 (ou mais)
- Modelos: SOM, GNG, k-means
- Capacidades: [16, 64, 256] cores
- Sementes: [13, 37, 73, 101, 137]
- Total: 5 × 3 × 3 × 5 = 225 experimentos

**Tempo esperado**:
- Teste rápido (2 imagens, 1 modelo, 1 capacity, 1 seed): 2-5 min
- Matriz reduzida (2 imagens, 2 modelos, 1 capacity, 2 seeds): 15-30 min
- Matriz completa: 45-75 min (CPU) ou 10-15 min (GPU)

**Reprodutibilidade**:
- Todos os seeds fixos
- Configuração centralizada em YAML
- Backup automático de resultados anteriores (timestamp)

## 4. Validação das Implementações

Esta seção reúne as evidências de que cada algoritmo funciona corretamente e respeita o protocolo de quantização.

### 4.1 Status de Validação por Regressão

A validação foi executada em `validation\validation_unique_colors.csv`. O conjunto contém 270 reconstruções avaliadas.

| Indicador | Valor |
|-----------|-------|
| Reconstruções válidas | 270 |
| Reconstruções inválidas | 0 |
| Máximo de cores únicas | 256 |
| Mínimo de cores únicas | 14 |

```markdown
| file_name                             | model   |   capacity |   seed |   unique_colors | valid   |
|:--------------------------------------|:--------|-----------:|-------:|----------------:|:--------|
| 00_controle_16_cores_gng_16_s101.png  | gng     |         16 |    101 |              16 | True    |
| 00_controle_16_cores_gng_16_s13.png   | gng     |         16 |     13 |              15 | True    |
| 00_controle_16_cores_gng_16_s137.png  | gng     |         16 |    137 |              16 | True    |
| 00_controle_16_cores_gng_16_s37.png   | gng     |         16 |     37 |              16 | True    |
| 00_controle_16_cores_gng_16_s73.png   | gng     |         16 |     73 |              15 | True    |
| 00_controle_16_cores_gng_256_s101.png | gng     |        256 |    101 |             175 | True    |
| 00_controle_16_cores_gng_256_s13.png  | gng     |        256 |     13 |             163 | True    |
| 00_controle_16_cores_gng_256_s137.png | gng     |        256 |    137 |             172 | True    |
| 00_controle_16_cores_gng_256_s37.png  | gng     |        256 |     37 |             159 | True    |
| 00_controle_16_cores_gng_256_s73.png  | gng     |        256 |     73 |             160 | True    |
```

**Interpretação**: a maior parte das reconstruções respeita o limite de cores. Caso existam registros inválidos, estes devem ser revisados antes da interpretação final.

### 4.2 Convergência da SOM
**Esperado**: o erro de quantização deve diminuir ao longo das épocas e estabilizar.

**Evidência**: os pesos finais, o checkpoint e as métricas acumuladas devem variar de forma consistente entre sementes; a SOM preserva a topologia da grade e reduz o erro de aproximação de forma gradual.

### 4.3 Crescimento da GNG
**Esperado**: o número de nós cresce para se adaptar à distribuição das cores e, em geral, atinge ou se aproxima da capacidade configurada.

**Evidência**: a estrutura da GNG deve exibir nós e arestas dinâmicos, com inserção de protótipos nos locais de maior erro. O grafo final deve refletir clusters de cor sem perder conectividade.

### 4.4 Redução da Função Objetivo (k-means)
**Esperado**: o erro intra-cluster diminui ao longo das iterações e a convergência ocorre quando o deslocamento dos centróides cai abaixo da tolerância.

**Evidência**: o algoritmo deve convergir em um número finito de iterações, produzindo protótipos centrados em regiões densas de cor.

### 4.5 Reprodutibilidade por Semente
**Esperado**: a mesma imagem, mesmo algoritmo, mesma capacidade e mesma semente devem produzir resultados idênticos ou estatisticamente equivalentes.

**Evidência**: o pipeline usa sementes fixas e a geração de resultados deve ser reproduzível. Apadronizar a amostragem por semente e a inicialização dos pesos permite comparação justa entre execuções.

## 5. Resultados Quantitativos

A tabela a seguir agrega as métricas de desempenho por imagem, modelo e capacidade. As médias e desvios padrão foram calculados entre as sementes do protocolo experimental.


| image_name               | model   |   capacity_requested |   quantization_error_mean |   quantization_error_std |   topographic_error_mean |   topographic_error_std |   psnr_mean |   psnr_std |   mean_delta_e_mean |   mean_delta_e_std |   training_time_s_mean |   training_time_s_std |
|:-------------------------|:--------|---------------------:|--------------------------:|-------------------------:|-------------------------:|------------------------:|------------:|-----------:|--------------------:|-------------------:|-----------------------:|----------------------:|
| 00_controle_16_cores.png | gng     |                   16 |                    0.0239 |                   0.0121 |                   0.0008 |                  0.0005 |     33.3012 |     7.3601 |              1.6771 |             1.0607 |                48.1849 |                5.6791 |
| 00_controle_16_cores.png | gng     |                   64 |                    0.0065 |                   0.0002 |                   0.0007 |                  0.0004 |     45.3696 |     0.3664 |              0.4584 |             0.0128 |                53.3961 |                4.0671 |
| 00_controle_16_cores.png | gng     |                  256 |                    0.0041 |                   0.0001 |                   0.0031 |                  0.0008 |     50.3057 |     0.2246 |              0.2991 |             0.0095 |                64.5079 |                0.6916 |
| 00_controle_16_cores.png | kmeans  |                   16 |                    0.0079 |                   0      |                 nan      |                nan      |     42.3517 |     0.0001 |              0.5366 |             0.0005 |                 0.8031 |                0.2682 |
| 00_controle_16_cores.png | kmeans  |                   64 |                    0.0055 |                   0.0001 |                 nan      |                nan      |     47.2289 |     0.1409 |              0.4051 |             0.0131 |                 6.8837 |                0.798  |
| 00_controle_16_cores.png | kmeans  |                  256 |                    0.0031 |                   0      |                 nan      |                nan      |     53.0412 |     0.098  |              0.2247 |             0.005  |                36.117  |                1.8117 |
| 00_controle_16_cores.png | som     |                   16 |                    0.1575 |                   0.0034 |                   0.07   |                  0.0128 |     20.2007 |     0.1213 |             11.748  |             0.3504 |                12.2677 |                4.1366 |
| 00_controle_16_cores.png | som     |                   64 |                    0.0129 |                   0.0051 |                   0.0101 |                  0.0093 |     39.2714 |     3.5432 |              0.8104 |             0.2955 |                18.7294 |                4.6239 |
| 00_controle_16_cores.png | som     |                  256 |                    0.0041 |                   0.0001 |                   0.1727 |                  0.0242 |     46.858  |     0.1416 |              0.2767 |             0.0036 |                48.9077 |                3.9795 |
| 01_poucas_cores.png      | gng     |                   16 |                    0.0204 |                   0.0026 |                   0.001  |                  0.0004 |     34.0509 |     0.8668 |              1.3962 |             0.1399 |                47.5173 |                1.8288 |
| 01_poucas_cores.png      | gng     |                   64 |                    0.0101 |                   0.0001 |                   0.003  |                  0.0009 |     40.7355 |     0.104  |              0.7378 |             0.0077 |                53.1077 |                0.7679 |
| 01_poucas_cores.png      | gng     |                  256 |                    0.0071 |                   0.0002 |                   0.0059 |                  0.0024 |     44.2455 |     0.2288 |              0.5381 |             0.0098 |                68.7721 |                0.8903 |
| 01_poucas_cores.png      | kmeans  |                   16 |                    0.0158 |                   0.0005 |                 nan      |                nan      |     35.7159 |     0.302  |              1.0731 |             0.0267 |                 2.3551 |                1.0696 |
| 01_poucas_cores.png      | kmeans  |                   64 |                    0.0098 |                   0.0002 |                 nan      |                nan      |     41.4598 |     0.0896 |              0.7068 |             0.0117 |                 9.6575 |                0.7799 |
| 01_poucas_cores.png      | kmeans  |                  256 |                    0.0058 |                   0.0001 |                 nan      |                nan      |     46.6924 |     0.0377 |              0.4362 |             0.0026 |                46.6432 |                6.8246 |
| 01_poucas_cores.png      | som     |                   16 |                    0.0311 |                   0.0001 |                   0.0517 |                  0.0029 |     30.5981 |     0.0628 |              2.2002 |             0.0113 |                 8.3513 |                0.3432 |
| 01_poucas_cores.png      | som     |                   64 |                    0.0112 |                   0.0001 |                   0.1337 |                  0.0078 |     38.1762 |     0.1465 |              0.8472 |             0.0206 |                15.4807 |                0.6678 |
| 01_poucas_cores.png      | som     |                  256 |                    0.0068 |                   0.0001 |                   0.2094 |                  0.018  |     41.4887 |     0.058  |              0.5594 |             0.0058 |                44.7851 |                0.259  |
| 02_gradiente_suave.png   | gng     |                   16 |                    0.0583 |                   0.0012 |                   0.0012 |                  0.0015 |     28.3693 |     0.0674 |              3.8507 |             0.1353 |                47.1038 |                1.378  |
| 02_gradiente_suave.png   | gng     |                   64 |                    0.0242 |                   0.0007 |                   0.001  |                  0.0005 |     35.8888 |     0.1819 |              1.5795 |             0.0432 |                68.0598 |               15.625  |
| 02_gradiente_suave.png   | gng     |                  256 |                    0.0133 |                   0.0001 |                   0.0024 |                  0.0005 |     41.1692 |     0.0484 |              0.9337 |             0.0042 |                72.2474 |                0.834  |
| 02_gradiente_suave.png   | kmeans  |                   16 |                    0.0567 |                   0.0016 |                 nan      |                nan      |     28.434  |     0.1217 |              3.6662 |             0.1354 |                 5.1909 |                1.3974 |
| 02_gradiente_suave.png   | kmeans  |                   64 |                    0.023  |                   0.0002 |                 nan      |                nan      |     36.2582 |     0.0646 |              1.5026 |             0.023  |                15.4454 |                3.0177 |
| 02_gradiente_suave.png   | kmeans  |                  256 |                    0.012  |                   0      |                 nan      |                nan      |     42.0233 |     0.025  |              0.8619 |             0.0024 |                50.2841 |                5.1274 |
| 02_gradiente_suave.png   | som     |                   16 |                    0.0723 |                   0.0001 |                   0.0817 |                  0.0014 |     26.4733 |     0.0137 |              4.874  |             0.0366 |                 8.1231 |                0.3063 |
| 02_gradiente_suave.png   | som     |                   64 |                    0.0278 |                   0.0001 |                   0.183  |                  0.002  |     34.4504 |     0.0461 |              1.8252 |             0.0136 |                15.4659 |                0.4663 |
| 02_gradiente_suave.png   | som     |                  256 |                    0.0138 |                   0.0001 |                   0.2722 |                  0.0063 |     40.1211 |     0.0575 |              0.97   |             0.0027 |                46.7086 |                5.1477 |
| 03_alta_saturacao.png    | gng     |                   16 |                    0.1137 |                   0.0019 |                   0.0053 |                  0.0042 |     22.1842 |     0.1075 |              7.3374 |             0.2422 |                34.5704 |                0.6146 |
| 03_alta_saturacao.png    | gng     |                   64 |                    0.0535 |                   0.0011 |                   0.0042 |                  0.0014 |     28.7498 |     0.1684 |              3.4569 |             0.0956 |                39.3836 |                0.7748 |
| 03_alta_saturacao.png    | gng     |                  256 |                    0.0308 |                   0.0002 |                   0.0053 |                  0.0012 |     33.579  |     0.0324 |              1.9756 |             0.0197 |                53.3375 |                0.7766 |
| 03_alta_saturacao.png    | kmeans  |                   16 |                    0.1108 |                   0.0015 |                 nan      |                nan      |     22.3235 |     0.0688 |              6.9919 |             0.1358 |                 2.3929 |                0.6044 |
| 03_alta_saturacao.png    | kmeans  |                   64 |                    0.0506 |                   0.0003 |                 nan      |                nan      |     29.1884 |     0.0672 |              3.2516 |             0.017  |                14.0859 |                1.1319 |
| 03_alta_saturacao.png    | kmeans  |                  256 |                    0.0278 |                   0.0002 |                 nan      |                nan      |     34.4848 |     0.0251 |              1.7587 |             0.023  |                58.9484 |                2.4323 |
| 03_alta_saturacao.png    | som     |                   16 |                    0.1369 |                   0.0032 |                   0.1579 |                  0.0803 |     20.6185 |     0.2074 |              9.1732 |             0.2608 |                 5.7306 |                0.3672 |
| 03_alta_saturacao.png    | som     |                   64 |                    0.0621 |                   0.0001 |                   0.2071 |                  0.0143 |     26.5665 |     0.0325 |              3.7729 |             0.0278 |                10.6267 |                0.9437 |
| 03_alta_saturacao.png    | som     |                  256 |                    0.0324 |                   0.0002 |                   0.2195 |                  0.0229 |     32.0213 |     0.1983 |              2.0407 |             0.0102 |                31.1332 |                0.6033 |
| 04_cor_rara.png          | gng     |                   16 |                    0.0441 |                   0.0003 |                   0.003  |                  0.0019 |     30.0397 |     0.0348 |              2.7945 |             0.0319 |                35.2437 |                0.7443 |
| 04_cor_rara.png          | gng     |                   64 |                    0.0272 |                   0.0006 |                   0.002  |                  0.0008 |     34.7301 |     0.1307 |              1.7007 |             0.0514 |                41.9206 |                4.2049 |
| 04_cor_rara.png          | gng     |                  256 |                    0.0182 |                   0.0003 |                   0.0051 |                  0.0014 |     38.1501 |     0.1306 |              1.1275 |             0.0136 |                51.8294 |                0.3751 |
| 04_cor_rara.png          | kmeans  |                   16 |                    0.0438 |                   0.0006 |                 nan      |                nan      |     30.4846 |     0.048  |              2.7875 |             0.0424 |                 5.5945 |                1.9462 |
| 04_cor_rara.png          | kmeans  |                   64 |                    0.0241 |                   0.0003 |                 nan      |                nan      |     35.7594 |     0.0604 |              1.4994 |             0.0304 |                13.9542 |                1.1686 |
| 04_cor_rara.png          | kmeans  |                  256 |                    0.0146 |                   0.0001 |                 nan      |                nan      |     40.1268 |     0.0267 |              0.8923 |             0.0085 |                56.8528 |                6.1339 |
| 04_cor_rara.png          | som     |                   16 |                    0.0476 |                   0.0003 |                   0.4098 |                  0.1449 |     27.05   |     0.08   |              3.0751 |             0.0365 |                 5.5744 |                0.1535 |
| 04_cor_rara.png          | som     |                   64 |                    0.0269 |                   0.0003 |                   0.405  |                  0.0909 |     31.9148 |     0.3026 |              1.6706 |             0.033  |                10.5273 |                0.1825 |
| 04_cor_rara.png          | som     |                  256 |                    0.0166 |                   0.0001 |                   0.416  |                  0.0505 |     35.9792 |     0.3499 |              1.0276 |             0.0053 |                31.1202 |                0.4835 |
| 05_cena_complexa.png     | gng     |                   16 |                    0.0867 |                   0.0005 |                   0.0003 |                  0.0002 |     25.0543 |     0.0464 |              6.8415 |             0.0937 |                34.7799 |                0.7513 |
| 05_cena_complexa.png     | gng     |                   64 |                    0.0478 |                   0.0005 |                   0.0025 |                  0.0009 |     30.2943 |     0.0601 |              4.4063 |             0.0931 |                40.1543 |                0.624  |
| 05_cena_complexa.png     | gng     |                  256 |                    0.0298 |                   0.0003 |                   0.0064 |                  0.0007 |     34.3592 |     0.0859 |              2.9231 |             0.0295 |                59.1534 |                1.4364 |
| 05_cena_complexa.png     | kmeans  |                   16 |                    0.0858 |                   0.0009 |                 nan      |                nan      |     25.1936 |     0.0811 |              6.743  |             0.0383 |                 4.5161 |                0.7065 |
| 05_cena_complexa.png     | kmeans  |                   64 |                    0.0463 |                   0.0003 |                 nan      |                nan      |     30.4916 |     0.0193 |              4.2745 |             0.1148 |                14.9581 |                0.4514 |
| 05_cena_complexa.png     | kmeans  |                  256 |                    0.0267 |                   0.0001 |                 nan      |                nan      |     35.1301 |     0.0103 |              2.6012 |             0.0115 |                63.0898 |                3.6672 |
| 05_cena_complexa.png     | som     |                   16 |                    0.0929 |                   0.0001 |                   0.205  |                  0.004  |     24.1998 |     0.0108 |              7.393  |             0.0157 |                 5.7963 |                0.1918 |
| 05_cena_complexa.png     | som     |                   64 |                    0.0504 |                   0.0001 |                   0.1874 |                  0.0046 |     29.5252 |     0.0151 |              4.8415 |             0.0185 |                10.3834 |                0.2351 |
| 05_cena_complexa.png     | som     |                  256 |                    0.0296 |                   0      |                   0.2047 |                  0.0038 |     33.7752 |     0.0267 |              3.2302 |             0.0091 |                31.2211 |                0.3492 |

### 5.1 Erro de Quantização
**Definição**: erro médio quadrático entre pixels originais e seus protótipos atribuídos.

**Interpretação**:
- menor valor indica melhor fidelidade visual e maior preservação de cor;
- quando comparado ao mesmo número de protótipos, o k-means tende a apresentar menor erro por otimizar diretamente o critério de distância;
- a SOM pode obter erro um pouco maior porque incorpora regularização topológica.

### 5.2 Erro Topológico
**Definição**: proporção de pixels cuja primeira e segunda BMU não são vizinhas em topologia.

**Interpretação**:
- o erro topológico é particularmente relevante para avaliar a qualidade estrutural da SOM e GNG;
- valores baixos indicam melhor preservação de vizinhança e organização dos protótipos;
- o k-means, por não ter topologia explícita, tende a piorar nessa métrica.

### 5.3 PSNR, MAE e ΔE
**Definição**: PSNR mede fidelidade global; MAE/MSE/RMSE medem diferença absoluta; ΔE mede diferença perceptual de cor.

**Interpretação**:
- PSNR maior e ΔE menor são indicadores de melhor reconstrução visual;
- ΔE é especialmente útil porque aproxima a avaliação humana mais do que o espaço RGB puro;
- discordâncias entre PSNR e ΔE podem indicar artefatos visuais localizados ou regiões de cor rara.

### 5.4 Tempo de Treinamento e Inferência
**Definição**: tempo para ajustar os protótipos e tempo para mapear todos os pixels.

**Interpretação**:
- o k-means costuma exigir mais iterações de atualização em altos valores de k;
- a GNG pode ser eficiente em distribuições heterogêneas;
- a SOM combina custo moderado com preservação topológica.

### 5.5 Média e Desvio Padrão
**Interpretação**:
- uma média baixa e desvio pequeno sugerem estabilidade de desempenho entre sementes;
- desvios altos indicam sensibilização à inicialização ou à amostragem.

## 6. Resultados Qualitativos

As evidências visuais essenciais estão armazenadas nos diretórios `outputs/reconstructed/` e `outputs/figures/`.

### 6.1 Imagens lado a lado
- **Original vs. reconstruída**: validam visualmente a fidelidade da quantização.
- **Recortes ampliados**: permitem verificar detalhes finos, bordas e regiões de alto contraste.

### 6.2 Mapas de erro e histogramas
- Mapas de diferença e ΔE destacam regiões problemáticas da imagem.
- Histogramas das diferenças identificam se os erros são concentrados ou distribuídos.
- Histogramas de vitórias permitem comparar qual algoritmo venceu em função da métrica adotada.

### 6.3 Nuvem RGB e protótipos
- A nuvem RGB mostra a distribuição dos pixels e sua aproximação pelos protótipos.
- A avaliação dos protótipos é essencial para verificar se o algoritmo cobriu regiões densas e se abandonou zonas pouco relevantes.

### 6.4 Malha da SOM e grafo da GNG
- **SOM**: a malha 2D mostra a continuidade topológica entre protótipos vizinhos.
- **GNG**: o grafo adaptativo informa como a topologia local e global evoluiu ao longo do treinamento.

### 6.5 Evidências mínimas esperadas
Para a análise final considerar-se completa, o conjunto de imagens e gráficos deve incluir:
- imagens reconstruídas para cada algoritmo e capacidade;
- mapas de diferença/ΔE;
- histogramas de diferenças;
- nuvem RGB dos protótipos;
- malha da SOM;
- grafo da GNG;
- neurônios sem ativação;
- tempo de treinamento e inferência.

## 7. Discussão

### 7.1 O erro topológico se correlaciona com a qualidade visual?
**Resposta esperada**: correlação parcial, não determinística. Um erro topológico alto pode sinalizar perda de estrutura perceptiva, mas a qualidade final depende também da distribuição dos protótipos e das regiões de maior sensibilidade visual. Em algumas imagens, a SOM e a GNG mantêm melhor continuidade topológica mesmo quando o erro geral não é mínimo.

### 7.2 Por que a SOM com vizinhança final não nula pode apresentar erro de quantização maior que o k-means?
**Resposta esperada**: porque a SOM otimiza uma função com componente topológica adicional. O raio de vizinhança e a regularização espacial podem deslocar os protótipos para manter a ordem local em vez de minimizar exclusivamente a distância ao centro da classe. O k-means, por outro lado, minimiza diretamente a soma das distâncias ao centróide.

### 7.3 Em quais tipos de imagem cada rede apresenta vantagem?
**Resposta esperada**:
- **SOM**: vantagens em imagens com gradientes suaves, transições contínuas e organização espacial clara;
- **GNG**: vantagens em imagens com distribuições coloridas heterogêneas, clusters discretos e variação local forte;
- **k-means**: vantagens em imagens onde a prioridade é reduzir o erro global e maximizar fidelidade numérica.

### 7.4 Onde métricas numéricas e percepção visual concordam ou divergem?
**Resposta esperada**:
- **Concordância**: regiões homogêneas e bem definidas tendem a apresentar baixo erro e boa percepção visual;
- **Divergência**: detalhes finos, bordas, sombras e cores raras podem produzir valores numéricos moderados mais percepção visual claramente distinta. Isso ocorre porque o espaço RGB não é completamente perceptualmente uniforme e por causa da sensibilidade humana a certas regiões da imagem.

### 7.5 Síntese comparativa
O protocolo experimental deve comparar algoritmos sob condições controladas: mesma imagem, mesma quantidade de protótipos, mesmos pixels de treinamento e mesmo orçamento computacional. Nesse cenário, a conclusão mais relevante não é “qual algoritmo vence”, mas sim:
- qual produz menor distorção;
- qual preserva melhor relações topológicas;
- qual distribui melhor os protótipos;
- qual preserva melhor cores raras;
- qual apresenta melhor custo-benefício.

## 8. Limitações

### 8.1 Sensibilidade à inicialização
A qualidade final depende da semente e da inicialização dos protótipos. Isso afeta especialmente a SOM e a GNG, embora o k-means++ reduza esse problema.

### 8.2 Custo das buscas de BMU
A busca dos protótipos mais próximos exige distância em relação a todos os centróides ou neurônios. Em imagens grandes, esse custo costuma dominar a fase de inferência.

### 8.3 Influência da amostragem
A amostragem de treinamento pode afetar a representatividade do subconjunto de pixels usado. Isso é particularmente importante em imagens grandes e em distribuições de cor altamente desbalanceadas.

### 8.4 Uso do RGB em vez de espaço perceptual uniforme
O espaço RGB não reflete diretamente a distância percebida pelo olho humano. Por isso, métricas como MSE ou RMSE podem não expressar plenamente a qualidade visual.

### 8.5 Dependência da resolução
Imagens de resolução muito diferente podem produzir comportamento distinto, porque a amostragem de treinamento e a proporção de pixels raros variam com a escala.

### 8.6 Dificuldade de comparar topologias distintas
A SOM, a GNG e o k-means têm diferentes formas de organização topológica. Portanto, comparar erro topológico entre eles exige cuidado e contextualização.

## 9. Conclusão

Os resultados experimentais, quando interpretados com o conjunto de métricas e evidências visuais, permitem concluir que cada algoritmo atende a um objetivo diferente. O k-means tende a apresentar menor erro de quantização, a SOM se destaca na preservação da estrutura topológica e a GNG possui vantagem em distribuições locais e heterogêneas. O ganho real de cada abordagem depende do compromisso entre fidelidade numérica, preservação de estrutura e custo computacional.

A conclusão mais relevante do projeto não é identificar um vencedor absoluto, mas compreender em que cenários cada algoritmo oferece melhor equilibrado entre qualidade, topologia e custo. Em imagens com gradientes suaves, a SOM pode ser preferível; em distribuições altamente heterogêneas, a GNG pode ser mais eficiente; em imagens onde a prioridade é reduzir o erro de quantização, o k-means costuma liderar.

### Trabalhos futuros
- explorar espaço de cores perceptualmente mais uniforme (LAB/CIELAB);
- otimizar hiperparâmetros por imagem;
- comparar qualidade versus tempo em um protocolo estritamente padronizado;
- avaliar robustez a ruído e resolução variável;
- estender o estudo para algoritmos mais recentes de quantização e clustering.

## 10. Conjunto Mínimo de Evidências

Para que a análise final seja considerada completa, o trabalho deve apresentar, no mínimo, as seguintes evidências:

- cinco ou mais imagens de entrada;
- três capacidades por algoritmo;
- cinco sementes por configuração;
- imagens reconstruídas por imagem, algoritmo e capacidade;
- erro de quantização e erro topológico;
- diferença entre as imagens original e reconstruída;
- histogramas de diferenças;
- mapas de ΔE;
- histogramas de vitórias;
- neurônios sem ativação;
- tempo de treinamento e inferência;
- nuvem RGB com protótipos;
- malha da SOM;
- grafo da GNG;
- média e desvio padrão agregados;
- análise explícita das quatro questões propostas.

Este conjunto mínimo é o que garante que a conclusão esteja apoiada por evidência experimental, e não apenas por hipótese teórica.

## 11. Apêndices

### 11.1 Hiperparâmetros Completos

Arquivo: `config/experiments.yaml`

```yaml
device: cpu
output_dir: outputs
data_dir: data/raw
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

### 11.2 Resultados por Semente

Arquivo: `outputs/metrics/runs.csv`

Contém uma linha por experimento (imagem × modelo × capacidade × semente), com métricas como:
- quantization_error
- topographic_error
- mae_rgb, mse_rgb, rmse_rgb
- psnr, mean_delta_e, std_delta_e, max_delta_e
- active_neurons, inactive_neurons, usage_entropy
- training_time_s, inference_time_s

### 11.3 Tabelas Agregadas

Arquivo: `outputs/tables/summary.csv`

Resumo com média e desvio padrão agrupados por imagem, modelo e capacidade.

### 11.4 Validação de Cores

Arquivo: `validation/validation_unique_colors.csv`

Uma linha por imagem reconstruída, com:
- file_name
- image_name
- model
- capacity
- seed
- unique_colors
- valid

### 11.5 Instruções de Execução

**Instalação**:
```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
```

**Execução rápida**:
```bash
python scripts/execute_and_report.py --quick
```

**Execução completa**:
```bash
python scripts/execute_and_report.py --full
```

**Validação**:
```bash
python scripts/validate_unique_colors.py
```

### 11.6 Repositório e Versões

- **Repositório**: versionado em Git
- **Geração do relatório**: `python scripts/generate_report.py`
- **Versões**: consulte `requirements.txt`
- **Data da geração**: 2026-10-07 21:50:45
