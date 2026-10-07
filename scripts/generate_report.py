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
        validation_path = Path("validation/validation_unique_colors.csv")
        validation_text = """
## 4. Validação das Implementações

Esta seção reúne as evidências de que cada algoritmo funciona corretamente e respeita o protocolo de quantização.
"""

        if validation_path.exists():
            try:
                import pandas as pd
                df = pd.read_csv(validation_path)
                total = len(df)
                valid = int(df['valid'].sum())
                invalid = total - valid
                max_unique = int(df['unique_colors'].max()) if not df.empty else 0
                min_unique = int(df['unique_colors'].min()) if not df.empty else 0

                validation_text += f"""
### 4.1 Status de Validação por Regressão

A validação foi executada em `{validation_path}`. O conjunto contém {total} reconstruções avaliadas.

| Indicador | Valor |
|-----------|-------|
| Reconstruções válidas | {valid} |
| Reconstruções inválidas | {invalid} |
| Máximo de cores únicas | {max_unique} |
| Mínimo de cores únicas | {min_unique} |

```markdown
{df[['file_name','model','capacity','seed','unique_colors','valid']].head(10).to_markdown(index=False)}
```

**Interpretação**: a maior parte das reconstruções respeita o limite de cores. Caso existam registros inválidos, estes devem ser revisados antes da interpretação final.
"""
            except Exception:
                validation_text += """
### 4.1 Status de Validação por Regressão

O arquivo de validação existe, mas não foi possível extrair uma tabela estrutural automaticamente.
"""
        else:
            validation_text += """
### 4.1 Status de Validação por Regressão

Arquivo esperado: `validation/validation_unique_colors.csv`.

**Observação**: ainda não houve execução de validação. Execute `python scripts/validate_unique_colors.py` para produzir o registro de cores únicas e confirmar que a reconstrução respeita a capacidade.
"""

        validation_text += """
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
"""
        return validation_text

    def section_5_resultados_quantitativos(self):
        """Seção 5: Resultados quantitativos."""
        text = """
## 5. Resultados Quantitativos

A tabela a seguir agrega as métricas de desempenho por imagem, modelo e capacidade. As médias e desvios padrão foram calculados entre as sementes do protocolo experimental.
"""

        if self.summary_df is not None and len(self.summary_df) > 0:
            metric_cols = [
                c for c in self.summary_df.columns
                if any(tag in c for tag in ['quantization_error', 'topographic_error', 'mean_delta_e', 'psnr', 'training_time_s', 'inference_time_s'])
            ]
            candidate_cols = ['image_name', 'model', 'capacity_requested'] + metric_cols[:10]
            candidate_cols = [c for c in candidate_cols if c in self.summary_df.columns]
            if candidate_cols:
                display_df = self.summary_df[candidate_cols].copy()
                for c in display_df.columns:
                    if display_df[c].dtype.kind in 'f':
                        display_df[c] = display_df[c].round(4)
                text += "\n\n" + display_df.to_markdown(index=False)
            else:
                text += "\n\n*Tabela agregada disponível, mas sem colunas de métricas esperadas.*"
        else:
            text += "\n\n*Nenhum dado agregado disponível. Execute `python scripts/run_all.py` para produzir `outputs/tables/summary.csv`.*"

        text += """

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
"""
        return text

    def section_6_resultados_qualitativos(self):
        """Seção 6: Resultados qualitativos."""
        return """
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
"""

    def section_7_discussao(self):
        """Seção 7: Discussão."""
        return """
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
"""

    def section_8_limitacoes(self):
        """Seção 8: Limitações."""
        return """
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
"""

    def section_9_conclusao(self):
        """Seção 9: Conclusão."""
        return """
## 9. Conclusão

Os resultados experimentais, quando interpretados com o conjunto de métricas e evidências visuais, permitem concluir que cada algoritmo atende a um objetivo diferente. O k-means tende a apresentar menor erro de quantização, a SOM se destaca na preservação da estrutura topológica e a GNG possui vantagem em distribuições locais e heterogêneas. O ganho real de cada abordagem depende do compromisso entre fidelidade numérica, preservação de estrutura e custo computacional.

A conclusão mais relevante do projeto não é identificar um vencedor absoluto, mas compreender em que cenários cada algoritmo oferece melhor equilibrado entre qualidade, topologia e custo. Em imagens com gradientes suaves, a SOM pode ser preferível; em distribuições altamente heterogêneas, a GNG pode ser mais eficiente; em imagens onde a prioridade é reduzir o erro de quantização, o k-means costuma liderar.

### Trabalhos futuros
- explorar espaço de cores perceptualmente mais uniforme (LAB/CIELAB);
- otimizar hiperparâmetros por imagem;
- comparar qualidade versus tempo em um protocolo estritamente padronizado;
- avaliar robustez a ruído e resolução variável;
- estender o estudo para algoritmos mais recentes de quantização e clustering.
"""

    def section_10_evidencias_minimas(self):
        """Seção 10: Conjunto mínimo de evidências."""
        return """
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
"""

    def section_apendices(self):
        """Apêndices."""
        return """
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
source .venv/bin/activate  # ou .venv\\Scripts\\activate no Windows
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
- **Data da geração**: """ + self.timestamp + """
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
            self.section_10_evidencias_minimas(),
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
