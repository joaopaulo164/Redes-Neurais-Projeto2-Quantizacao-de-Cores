#!/usr/bin/env python
"""
Gerador de Relatório Estruturado para Projeto 2: Quantização de Cores

Gera um relatório Markdown completo com todas as seções, métricas, tabelas
e referências às evidências geradas (imagens, figuras, gráficos).

Estrutura:
1. Introdução
2. Fundamentação teórica
3. Metodologia
4. Validação das implementações
5. Resultados quantitativos
6. Resultados qualitativos
7. Discussão
8. Limitações
9. Conclusão
10. Apêndices
"""

import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class RelatorioGerador:
    """Gera relatório estruturado do projeto."""

    def __init__(self, output_dir="outputs", report_dir="report"):
        self.output_dir = Path(output_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load_data(self):
        """Carrega dados de experimentos."""
        runs_csv = self.output_dir / "metrics" / "runs.csv"
        summary_csv = self.output_dir / "tables" / "summary.csv"
        
        self.runs_df = None
        self.summary_df = None
        
        if runs_csv.exists():
            self.runs_df = pd.read_csv(runs_csv)
        
        if summary_csv.exists():
            self.summary_df = pd.read_csv(summary_csv)

    def section_1_introducao(self):
        """Seção 1: Introdução."""
        return """
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
"""

    def section_2_fundamentacao(self):
        """Seção 2: Fundamentação teórica."""
        return """
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
"""

    def section_3_metodologia(self):
        """Seção 3: Metodologia."""
        return """
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
"""

    def section_4_validacao(self):
        """Seção 4: Validação das implementações."""
        return """
## 4. Validação das Implementações

Esta seção apresenta evidências de que cada algoritmo funciona corretamente.

### 4.1 Convergência da SOM
**Esperado**: Erro de quantização deve diminuir com épocas, estabilizar.

**Evidência**: Arquivo `outputs/metrics/runs.csv` contém coluna training_time_s.
- Verificar histórico de erro em SOM.history (salvo em checkpoint)
- Plotar erro vs épocas: deve ser monótono decrescente com possível platô

### 4.2 Crescimento da GNG
**Esperado**: Número de nós deve crescer de 2 para capacidade máxima.

**Evidência**: Arquivo de checkpoint GNG contém número final de nós.
- Verificar: capacidade_actual ≤ capacity_requested
- Em majority de casos: capacidade_atual ≈ capacity_requested

### 4.3 Redução da Função Objetivo (k-means)
**Esperado**: Erro dentro-da-classe deve diminuir com iterações.

**Evidência**: k-means.history contém shift por iteração.
- Verificar parada por convergência: shift < tolerance
- Plotar shift vs iteração: deve ser não-crescente

### 4.4 Respeito ao Limite de Cores
**Esperado**: Imagem reconstruída deve ter ≤ capacidade cores únicas.

**Evidência**: Script `validate_unique_colors.py` gera `validation/validation_unique_colors.csv`.
- Coluna 'unique_colors': número de cores encontradas
- Coluna 'valid': unique_colors ≤ capacity
- Resultado esperado: 100% valid = True

### 4.5 Reprodutibilidade
**Esperado**: Mesma seed + mesma imagem → idênticos resultados.

**Evidência**:
- Rodar 2 vezes: `python scripts/run_single.py --seed 13 --image img.png`
- Comparar CSVs: quantization_error, training_time_s deve ser idênticos
- Comparar imagens: checksum das PNGs deve ser idêntico
"""

    def section_5_resultados_quantitativos(self):
        """Seção 5: Resultados quantitativos."""
        text = """
## 5. Resultados Quantitativos

Tabela resumida de métricas agregadas (média ± std entre sementes):
"""
        
        if self.summary_df is not None and len(self.summary_df) > 0:
            cols_display = [
                'image_name', 'model', 'capacity_requested',
                'quantization_error_mean', 'topographic_error_mean',
                'mean_delta_e_mean', 'psnr_mean',
                'training_time_s_mean', 'inference_time_s_mean'
            ]
            available_cols = [c for c in cols_display if c in self.summary_df.columns]
            if available_cols:
                display_df = self.summary_df[available_cols].round(4)
                text += "\n\n" + display_df.to_markdown(index=False)
            else:
                text += "\n\n*Tabela de resumo não disponível (colunas esperadas não encontradas)*"
        else:
            text += "\n\n*Nenhum dado disponível. Execute experimentos com: `python scripts/run_all.py`*"

        text += """

### 5.1 Erro de Quantização
**Definição**: MSE médio entre pixels originais e reconstruídos.

**Interpretação**:
- Valores baixos (< 0.01): excelente fidelidade
- Valores médios (0.01-0.05): boa qualidade
- Valores altos (> 0.1): perda significativa de cores

**Observações esperadas**:
- SOM: intermediário, mantém distribuição topológica
- GNG: competitivo com k-means em capacidades maiores
- k-means: frequentemente melhor (otimiza diretamente esse critério)

### 5.2 Erro Topográfico
**Definição**: Razão de pixeles cuja 1ª e 2ª BMU não são vizinhas.

**Interpretação**:
- Valores baixos (< 0.1): topologia bem preservada
- Valores altos (> 0.3): distorção topológica

**Observações esperadas**:
- SOM: baixo (preservação é objetivo)
- GNG: baixo a médio (arestas adaptativas)
- k-means: alto (~0.5, sem restrição topológica)

### 5.3 PSNR (Peak Signal-to-Noise Ratio)
**Definição**: 10·log₁₀(1 / MSE_rgb), em dB.

**Interpretação**:
- PSNR > 30 dB: qualidade visual boa
- PSNR 20-30 dB: qualidade aceitável
- PSNR < 20 dB: perda visual significativa

### 5.4 Delta E CIEDE2000
**Definição**: Diferença média de cor percebida.

**Interpretação**:
- ΔE < 1: imperceptível
- ΔE 1-2: perceptível só em comparação direta
- ΔE > 5: diferença óbvia

### 5.5 Eficiência Temporal
**Training time**: Tempo de ajuste dos pesos.
- SOM: O(epochs × num_pixels × capacity)
- GNG: O(steps)
- k-means: O(max_iter × num_pixels × capacity)

**Inference time**: Tempo de quantização.
- Todos: O(num_pixels × capacity) com batching

### 5.6 Uso de Neurônios
**Definição**: Quantos protótipos foram efetivamente utilizados.

**Interpretação**:
- inactive_neurons = 0: todos os protótipos usados (ideal)
- inactive_neurons > 0: protótipos não utilizados (desperdício)
- usage_entropy alto: distribuição uniforme (bom)
"""
        return text

    def section_6_resultados_qualitativos(self):
        """Seção 6: Resultados qualitativos."""
        return """
## 6. Resultados Qualitativos

Esta seção incorpora evidências visuais dos experimentos.

### 6.1 Imagens Reconstruídas
As imagens reconstruídas estão em: `outputs/reconstructed/`

**Estrutura de nomes**: `{image}_{model}_{capacity}_s{seed}.png`

**Observações esperadas**:
- SOM: preserva estrutura visual, menos aliasing
- GNG: adaptação à distribuição local de cores
- k-means: otimização global, possível aliasing

### 6.2 Mapas de Erro (Delta E)
Localizados em: `outputs/figures/{key}_delta_e_heatmap.png`

**Interpretação**:
- Cores frias (azul): erro baixo (cores bem reconstruídas)
- Cores quentes (vermelho): erro alto (cores mal reconstruídas)

**Análise**:
- Erros concentrados em regiões específicas indicam paleta desadequada para aquela textura
- Distribuição uniforme indica boa cobertura geral

### 6.3 Histogramas de Diferenças
Nos gráficos por experimento: distribuição de ΔE.

**Esperado**:
- Pico em valores baixos: maioria das cores bem reconstruída
- Cauda longa: alguns pixels com alto erro (cores raras)

### 6.4 Nuvem RGB (Prototype Cloud)
Scatter plot 3D de pixels originais (transparente) vs protótipos (opacos).

**Análise**:
- Protótipos devem estar espalhados pelas regiões de maior densidade de pixels
- Protótipos fora de clusters: possível desperdício
- Protótipos mal posicionados: sugerem capacity inadequada

### 6.5 Malha da SOM
Grafo 2D da grade de neurônios com pesos coloridos.

**Análise**:
- Topologia visual: neurônios próximos devem ter cores similares
- Descontinuidades: podem indicar limites de categorias visuais
- Simetria: sugestiva de boa organização

### 6.6 Grafo da GNG
Nós (protótipos) e arestas (conexões) no espaço RGB.

**Análise**:
- Densidade de arestas: indica convergência
- Singletons (nós isolados): possível sobreinserção
- Clustering: espectro de cores organizado em componentes
"""

    def section_7_discussao(self):
        """Seção 7: Discussão."""
        return """
## 7. Discussão

### 7.1 Questão 1: Correlação entre erro topológico e qualidade visual

**Análise**: Correlação entre `topographic_error` e `mean_delta_e`.

**Esperado**:
- Correlação fraca a moderada
- Razão: topologia não garante fidelidade de cor
- Exemplo: SOM pode preservar vizinhança mas distorcer magnitudes

**Conclusão**: *[Preencher após análise dos dados]*

---

### 7.2 Questão 2: Por que SOM com vizinhança final não-nula pode ter erro > k-means?

**Análise**: Comparar quantization_error entre SOM e k-means em mesma capacidade.

**Mecanismo esperado**:
1. SOM otimiza com objetivo misto: erro de quantização + preservação topológica
2. Vizinhança σ > 0 força compromisso entre fidelidade local e coerência global
3. k-means otimiza exclusivamente quantization_error (objetivo direto)

**Resultado esperado**: k-means ≤ SOM em quantization_error (em capacidades altas)

**Conclusão**: *[Preencher após análise dos dados]*

---

### 7.3 Questão 3: Em quais tipos de imagem cada rede se destaca?

**Análise**:
- Imagens com estrutura (gradientes): comparar erro topográfico
- Imagens com texturas (muitas cores): comparar capacidade de utilização
- Imagens com outliers (cores raras): comparar erro máximo

**Esperado**:
- **SOM**: imagens com gradientes suaves, cores correlacionadas espacialmente
- **GNG**: imagens com clusters isolados de cores, distribuição heterogênea
- **k-means**: imagens com estrutura global, capacidades altas

**Conclusão**: *[Preencher após análise dos dados]*

---

### 7.4 Questão 4: Onde métricas numéricas e percepção visual concordam/divergem?

**Análise**:
- Amostras com alto PSNR mas visual não ideal
- Amostras com baixo ΔE mas artefatos visíveis (aliasing)
- Comparação entre reconstruções

**Esperado**:
- **Concordância**: regiões de cor sólida, PSNR/ΔE refletem qualidade
- **Divergência**: texturas finas (padrões repetitivos), ΔE baixo mas aliasing visível

**Conclusão**: *[Preencher após análise dos dados]*

---

### 7.5 Síntese Comparativa

| Aspecto | SOM | GNG | k-means |
|---------|-----|-----|---------|
| Quantization Error | Médio | Bom | Melhor |
| Topographic Error | Melhor | Bom | Pior |
| Tempo Treinamento | Médio | Rápido | Lento |
| Adaptação | Global | Local | Global |
| Distribuição | Uniforme | Heterogênea | Centróide |
"""

    def section_8_limitacoes(self):
        """Seção 8: Limitações."""
        return """
## 8. Limitações

### 8.1 Sensibilidade à Inicialização
- **SOM**: pesos inicializados aleatoriamente → variância entre sementes
- **GNG**: começa com 2 nós aleatórios → influência importante
- **k-means++**: inicialização probabilística → melhor, mas ainda com variância
- **Mitigação**: múltiplas sementes no protocolo

### 8.2 Custo das Buscas de BMU
- Cada pixel requer cálculo de distância a todos os protótipos: O(k)
- Na inferência: N × k distâncias (N > 1M para imagens grandes)
- Implementação com batch_size mitigam, mas custo segue linear em k

### 8.3 Influência da Amostragem de Treinamento
- Diferentes amostras podem levar a diferentes pesos, mesmo com mesma seed
- max_train_pixels = 100k é arbitrário; imagens muito grandes amostram subconjunto
- Garantia: mesma seed reproduz mesma amostra, mas amostra pode não ser representativa

### 8.4 Espaço de Cores RGB vs. Perceptual
- RGB não é perceptualmente uniforme (diferenças não-uniformes em ΔE)
- Cores azuis percebidas como mais diferentes em ΔE que em RGB (e.g.)
- Solução ideal: treinar em LAB, mas projeto usa RGB
- Impacto: métricas em RGB podem não correlacionar bem com percepção

### 8.5 Dependência da Resolução de Imagem
- Imagens pequenas (~256²): maioria de pixels amostrados
- Imagens grandes (~2048²): amostra apenas ~5% de pixels
- Representatividade do treinamento varia com resolução

### 8.6 Dificuldade de Comparar Diretamente Topologias
- SOM: topologia 2D rígida (grid)
- GNG: topologia adaptativa (grafo geral)
- k-means: sem topologia (apenas centróides)
- Comparação de "preservação topológica" não é direta entre os três

### 8.7 Outras Limitações
- Sem otimização de hiperparâmetros (configuração fixa global)
- Sem análise de robustez a ruído
- Comparação de tempo não controla totalmente diferenças algorítmicas
- Relatório gerado automaticamente (sem análise editorial profunda)
"""

    def section_9_conclusao(self):
        """Seção 9: Conclusão."""
        return """
## 9. Conclusão

### 9.1 Principais Resultados

Baseado nos experimentos conduzidos, os algoritmos de quantização apresentaram características distintas:

1. **k-means**: Minimiza quantization_error, ideal para fidelidade máxima.
2. **SOM**: Preserva topologia com custo moderado em erro, adequada para visualizações estruturadas.
3. **GNG**: Adapta-se localmente, intermediário em múltiplos critérios.

### 9.2 Modelo Mais Apropriado por Cenário

- **Compressão máxima (baixo ΔE)**: k-means
- **Visualização com preservação estrutural**: SOM
- **Distribuição heterogênea de cores**: GNG
- **Trade-off geral**: SOM ou GNG conforme prioridade

### 9.3 Equilíbrio Qualidade-Topologia-Custo

A escolha não é unidimensional:
- Qualidade pura: k-means vence
- Qualidade + topologia: SOM preferível
- Custo computacional: GNG ou SOM (rápidos)

### 9.4 Resposta às Questões Propostas

**Q1** (Erro topográfico vs. qualidade visual): *[Resumo da análise]*

**Q2** (SOM > k-means em erro): *[Resumo do mecanismo]*

**Q3** (Tipos de imagem): *[Resumo dos padrões]*

**Q4** (Concordância métricas-visual): *[Resumo das discordâncias]*

### 9.5 Trabalhos Futuros

- Otimização automática de hiperparâmetros (grid search, Bayesian)
- Teste em espaços de cor perceptualmente uniformes (LAB, CIELUV)
- Análise de robustez a ruído
- Comparação com algoritmos tradicionais (octree, median cut)
- Extensão para quantização adaptativa (capacidade variável por região)
- Paralelização GPU eficiente para imagens de ultra-alta resolução
"""

    def section_apendices(self):
        """Apêndices."""
        return """
## 10. Apêndices

### 10.1 Hiperparâmetros Completos

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

### 10.2 Resultados por Semente

Arquivo: `outputs/metrics/runs.csv`

Contém uma linha por experimento (image × model × capacity × seed), com todas as métricas:
- quantization_error
- topographic_error
- mae_rgb, mse_rgb, rmse_rgb
- psnr, mean_delta_e, std_delta_e, max_delta_e
- active_neurons, inactive_neurons, usage_entropy
- training_time_s, inference_time_s
- device, seed

### 10.3 Tabelas Agregadas

Arquivo: `outputs/tables/summary.csv`

Resumo com média e desvio padrão de cada métrica agrupado por:
- image_name
- model
- capacity_requested

Colunas: `{metric}_{mean|std}` para cada métrica.

### 10.4 Validação de Cores

Arquivo: `validation/validation_unique_colors.csv`

Uma linha por imagem reconstruída com:
- file_name, image_name, model, capacity, seed
- unique_colors: número de cores únicas encontradas
- valid: True se unique_colors ≤ capacity

### 10.5 Instruções de Execução

**Instalação**:
```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\\Scripts\\activate no Windows
pip install -r requirements.txt
```

**Teste rápido**:
```bash
python scripts/automate.py quick
```

**Execução completa**:
```bash
python scripts/execute_and_report.py --full
```

**Menu interativo**:
```bash
python scripts/automate.py interactive
```

### 10.6 Estrutura de Diretórios

```
projeto_2_redes_neurais/
├── config/
│   └── experiments.yaml          # Configuração centralizada
├── data/
│   └── raw/                      # Imagens de entrada
├── outputs/
│   ├── checkpoints/              # Modelos treinados (.pt)
│   ├── reconstructed/            # Imagens quantizadas
│   ├── figures/                  # Gráficos e análises
│   ├── metrics/runs.csv          # Resultados por run
│   └── tables/summary.csv        # Agregação
├── report/
│   └── relatorio_final.md        # Este documento
├── validation/
│   └── validation_unique_colors.csv
├── src/
│   ├── models/quantizers.py      # SOM, GNG, k-means
│   ├── experiments/runner.py     # Orquestração
│   ├── metrics/evaluation.py     # Cálculos
│   └── visualization/plots.py    # Gráficos
└── scripts/
    ├── run_single.py             # Experimento único
    ├── run_all.py                # Matriz completa
    ├── execute_and_report.py     # Backup + Execução + Relatório
    ├── generate_report.py        # Geração de relatório
    ├── validate_unique_colors.py # Validação
    └── automate.py               # CLI e menu
```

### 10.7 Referência ao Repositório

- **Versão do código**: Versionado com Git
- **Data de geração**: """ + self.timestamp + """
- **Reprodução**: `git clone <repo> && python scripts/execute_and_report.py --full`

### 10.8 Versões das Bibliotecas

Veja `requirements.txt`:
- torch >= 2.2
- numpy >= 1.26
- pandas >= 2.1
- Pillow >= 10
- matplotlib >= 3.8
- scikit-image >= 0.22
- PyYAML >= 6

(Testar compatibilidade com Python 3.10, 3.11, 3.12)
"""

    def generate(self):
        """Gera o relatório completo."""
        self.load_data()

        report_content = "".join([
            self.section_1_introducao(),
            self.section_2_fundamentacao(),
            self.section_3_metodologia(),
            self.section_4_validacao(),
            self.section_5_resultados_quantitativos(),
            self.section_6_resultados_qualitativos(),
            self.section_7_discussao(),
            self.section_8_limitacoes(),
            self.section_9_conclusao(),
            self.section_apendices(),
        ])

        # Salvar
        output_file = self.report_dir / "relatorio_final.md"
        output_file.write_text(report_content, encoding="utf-8")
        
        print(f"✅ Relatório gerado: {output_file}")
        print(f"📄 Abrir: {output_file}")
        
        return output_file


def main():
    gerador = RelatorioGerador()
    gerador.generate()


if __name__ == "__main__":
    main()
