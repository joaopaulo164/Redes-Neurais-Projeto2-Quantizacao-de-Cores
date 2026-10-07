# Conjunto de imagens do Projeto 2
## Quantização de cores com SOM, GNG e k-means

Este diretório contém o conjunto de imagens utilizado nos experimentos de quantização de cores do **Projeto 2 - Redes Neurais**. As imagens foram preparadas para representar diferentes distribuições cromáticas e diferentes dificuldades de quantização, permitindo comparar **Self-Organizing Maps (SOM)**, **Growing Neural Gas (GNG)** e **k-means** sob condições controladas e visualmente distintas.

---

## 1. Localização dos arquivos

Os arquivos de imagem devem ser mantidos em:

```text
data/raw/
```

Estrutura esperada:

```text
data/
├── README.md
└── raw/
    ├── 00_controle_16_cores.png
    ├── 01_poucas_cores.png
    ├── 02_gradiente_suave.png
    ├── 03_alta_saturacao.png
    ├── 04_cor_rara.png
    └── 05_cena_complexa.png
```

---

## 2. Especificações comuns

As seis imagens possuem as seguintes características:

- formato: PNG;
- modo de cor: RGB;
- dimensões: 512 × 512 pixels;
- quantidade de canais: 3;
- transparência: ausente;
- finalidade: treinamento, inferência e avaliação de algoritmos de quantização de cores;
- origem: imagens geradas com auxílio de inteligência artificial e preparadas especificamente para este projeto.

As imagens não devem ser convertidas para JPEG antes dos experimentos, pois a compressão com perdas poderia introduzir cores e artefatos adicionais. Recomenda-se preservar os arquivos PNG originais durante todas as execuções.

---

## 3. Descrição dos arquivos

### 3.1 `00_controle_16_cores.png`

**Categoria:** imagem de controle com paleta conhecida.

**Descrição visual:** composição em grade 4 × 4, formada por 16 regiões cromáticas. A grade inclui cores quentes, frias, saturadas, neutras, claras e escuras. Entre as regiões estão vermelho, laranja, amarelo, verde-claro, verde, ciano, azul, azul-escuro, violeta, magenta, rosa, marrom, branco, cinza-claro, cinza-escuro e preto.

**Finalidade experimental:**

- validar o pipeline de leitura, normalização, quantização e reconstrução;
- verificar o comportamento dos métodos quando a quantidade nominal de protótipos é igual ao número planejado de regiões cromáticas;
- observar se cada região recebe um protótipo próprio;
- detectar mistura indevida entre cores claramente separadas;
- verificar a quantidade de neurônios ou centroides efetivamente utilizados.

**Hipótese:** com capacidade 16 e treinamento adequado, os métodos devem representar a imagem com erro reduzido. Resultados significativamente piores podem indicar inicialização inadequada, treinamento insuficiente ou influência da restrição topológica.

**Uso recomendado:** validação da implementação. A imagem pode ser analisada separadamente das cinco imagens principais.

**Observação metodológica:** embora a composição tenha sido planejada como uma grade de 16 regiões, pequenas variações internas podem existir devido ao processo de geração e redimensionamento. Portanto, não se deve presumir que o arquivo contenha exatamente 16 valores RGB distintos sem realizar uma contagem computacional.

---

### 3.2 `01_poucas_cores.png`

**Categoria:** poucas cores dominantes e regiões bem definidas.

**Descrição visual:** ilustração com céu azul, nuvem clara, sol amarelo, casa clara com telhado vermelho, porta marrom, janelas azuis, árvore verde com tronco marrom, gramado verde e caminho cinza. A imagem apresenta formas grandes, bordas relativamente nítidas e áreas cromáticas extensas.

**Finalidade experimental:**

- avaliar a representação de paletas pequenas;
- observar a preservação de contornos entre regiões uniformes;
- verificar se os protótipos se concentram nas cores dominantes;
- comparar a reconstrução usando 16, 64 e 256 protótipos;
- analisar possíveis alterações nas cores de elementos menores, como janelas, maçaneta e pedras do caminho.

**Hipótese:** a imagem deve apresentar erro relativamente baixo mesmo com 16 protótipos, pois possui poucas famílias de cores e extensas regiões uniformes. Capacidades maiores devem melhorar nuances e elementos pequenos, mas o ganho pode ser menor do que nas imagens de gradiente ou na cena complexa.

**Regiões de interesse:**

- transição entre céu e gramado;
- bordas do telhado;
- quatro partes da janela;
- pedras do caminho;
- contorno da copa da árvore;
- pequeno círculo amarelo na porta.

---

### 3.3 `02_gradiente_suave.png`

**Categoria:** gradientes contínuos e tonalidades próximas.

**Descrição visual:** composição semelhante a um horizonte sobre água, com transição vertical entre azul-escuro, azul, ciano, tons claros, amarelo, laranja e uma faixa avermelhada próxima ao horizonte. A parte inferior apresenta reflexos e variações suaves de azul e laranja.

**Finalidade experimental:**

- avaliar a representação de transições cromáticas contínuas;
- identificar o aparecimento de faixas artificiais de cor, ou *color banding*;
- comparar a suavidade das reconstruções com 16, 64 e 256 protótipos;
- verificar a distribuição dos protótipos ao longo de uma trajetória contínua no espaço RGB;
- relacionar erro de quantização, Delta E e avaliação visual.

**Hipótese:** a capacidade 16 deve produzir faixas mais visíveis. O aumento para 64 e 256 protótipos deve reduzir a discretização aparente e melhorar as métricas. A diferença entre capacidades tende a ser mais evidente nesta imagem do que na imagem com poucas cores dominantes.

**Regiões de interesse:**

- gradiente azul na parte superior;
- transição de tons claros para amarelo e laranja;
- faixa horizontal avermelhada;
- reflexo alaranjado na água;
- gradações azuis na parte inferior.

---

### 3.4 `03_alta_saturacao.png`

**Categoria:** alta saturação e ampla diversidade de matizes.

**Descrição visual:** flor com pétalas intensamente coloridas em vermelho, laranja, amarelo, verde, ciano, azul, violeta, magenta e rosa. O centro possui tonalidades amarelas e alaranjadas, enquanto o fundo é predominantemente verde-escuro. Há pequenas gotas e detalhes de textura sobre as pétalas.

**Finalidade experimental:**

- avaliar a preservação de cores altamente saturadas;
- observar se os protótipos cobrem regiões distantes do espaço RGB;
- verificar a preservação das transições entre pétalas de matizes diferentes;
- analisar a competição entre as cores do objeto principal e o fundo escuro;
- avaliar a preservação de texturas e pequenos brilhos.

**Hipótese:** métodos com poucos protótipos podem fundir tonalidades próximas ou deslocar cores saturadas. Capacidades maiores devem preservar melhor a diversidade cromática das pétalas e os detalhes do centro, embora parte da textura possa continuar sendo simplificada.

**Regiões de interesse:**

- limites entre pétalas adjacentes;
- gradientes internos das pétalas;
- gotas e pontos luminosos;
- centro amarelo e alaranjado;
- transição entre a flor e o fundo verde-escuro.

---

### 3.5 `04_cor_rara.png`

**Categoria:** objeto pequeno com cor rara.

**Descrição visual:** composição predominantemente verde, formada por folhas com diferentes níveis de foco, iluminação e textura. Um pequeno objeto vermelho com detalhes escuros aparece sobre uma folha central. A área vermelha ocupa apenas uma pequena parte da imagem e contrasta com o fundo verde.

**Finalidade experimental:**

- avaliar se uma cor de baixa frequência é preservada;
- verificar se o algoritmo dedica um protótipo à região vermelha;
- comparar métricas globais com uma falha visual localizada;
- analisar a influência da amostragem aleatória sobre cores raras;
- observar a distribuição de vitórias dos protótipos.

**Hipótese:** o erro médio global pode permanecer baixo mesmo que a pequena região vermelha seja alterada ou perdida, porque a maior parte dos pixels pertence a tons de verde. Essa imagem é particularmente importante para demonstrar que métricas médias não substituem a inspeção visual localizada.

**Regiões de interesse:**

- pequeno objeto vermelho;
- detalhes escuros do objeto;
- borda entre o objeto e a folha;
- nervura clara da folha central;
- folhas desfocadas no fundo.

**Análise complementar recomendada:** produzir um recorte ampliado da região do objeto vermelho e comparar esse recorte entre SOM, GNG e k-means nas capacidades 16, 64 e 256.

---

### 3.6 `05_cena_complexa.png`

**Categoria:** cena natural complexa.

**Descrição visual:** paisagem com céu azul e nuvens, montanhas com áreas rochosas e claras, floresta, pequenas construções, lago com reflexos, barco vermelho, píer de madeira e flores rosadas ou avermelhadas no primeiro plano. A imagem reúne gradientes, texturas, sombras, reflexos, regiões extensas e pequenos elementos de cores distintas.

**Finalidade experimental:**

- avaliar os métodos em uma composição visual diversificada;
- combinar múltiplas dificuldades em uma única imagem;
- analisar a preservação de texturas, reflexos e pequenos objetos;
- comparar qualidade visual, erro de quantização, Delta E e custo computacional;
- observar como os protótipos se distribuem entre céu, vegetação, água, montanhas e elementos raros.

**Hipótese:** esta deve ser uma das imagens mais difíceis. A capacidade 16 provavelmente simplificará texturas, reflexos e nuances. Capacidades 64 e 256 devem melhorar a reconstrução, mas podem manter diferenças localizadas em flores, barco, construções e áreas claras das montanhas.

**Regiões de interesse:**

- gradiente e nuvens no céu;
- áreas claras e escuras das montanhas;
- floresta e pequenas construções;
- reflexos na água;
- barco vermelho;
- píer;
- flores no primeiro plano;
- transparência aparente da água próxima à margem.

---

## 4. Papel de cada imagem no protocolo

O conjunto foi organizado para que cada arquivo enfatize um aspecto diferente:

- `00_controle_16_cores.png`: validação técnica e paleta controlada;
- `01_poucas_cores.png`: regiões uniformes e bordas nítidas;
- `02_gradiente_suave.png`: continuidade tonal e formação de faixas;
- `03_alta_saturacao.png`: cobertura de matizes intensos;
- `04_cor_rara.png`: preservação de uma região pequena e pouco frequente;
- `05_cena_complexa.png`: combinação de texturas, gradientes, reflexos e cores variadas.

As cinco imagens numeradas de `01` a `05` formam o conjunto principal. A imagem `00` deve ser usada prioritariamente na validação da implementação e pode também ser incluída como experimento complementar.

---

## 5. Protocolo experimental recomendado

Para cada imagem principal, executar:

- SOM com grades 4 × 4, 8 × 8 e 16 × 16;
- GNG com limites de 16, 64 e 256 neurônios;
- k-means com 16, 64 e 256 centroides;
- cinco sementes por configuração.

Com cinco imagens principais:

```text
5 imagens × 3 modelos × 3 capacidades × 5 sementes = 225 execuções
```

Se a imagem de controle também for incluída na matriz completa:

```text
6 imagens × 3 modelos × 3 capacidades × 5 sementes = 270 execuções
```

Recomenda-se não misturar a imagem de controle com a média principal sem declarar explicitamente essa decisão no relatório.

---

## 6. Pré-processamento

O carregador do projeto deve:

1. abrir cada imagem;
2. converter explicitamente para RGB;
3. transformar a imagem de 512 × 512 × 3 em uma matriz de pixels;
4. normalizar os canais para o intervalo `[0, 1]`;
5. utilizar uma amostra de pixels para treinamento, quando configurado;
6. utilizar todos os pixels na inferência e nas métricas finais;
7. reconstruir a saída com as dimensões originais.

Não aplicar antes do treinamento:

- correção de cor;
- contraste automático;
- nitidez;
- redução de ruído;
- conversão para JPEG;
- redimensionamento diferente entre imagens;
- filtros artísticos.

Qualquer transformação adicional deve ser registrada no relatório e aplicada de maneira consistente.

---

## 7. Evidências a produzir

Para cada combinação relevante, gerar:

- imagem original e reconstruída lado a lado;
- imagem reconstruída isolada;
- mapa de Delta E CIEDE2000;
- histograma das diferenças RGB;
- histograma de vitórias dos protótipos;
- quantidade de protótipos ativos e inativos;
- projeção dos pixels e protótipos no espaço RGB;
- estrutura topológica da SOM ou da GNG, quando aplicável;
- erro de quantização;
- erro topológico;
- MAE, MSE, RMSE e PSNR;
- média, desvio padrão e máximo de Delta E;
- tempo de treinamento;
- tempo de inferência.

Para `04_cor_rara.png`, incluir também um recorte ampliado da região vermelha. Para `02_gradiente_suave.png`, destacar visualmente a ocorrência de faixas de cor. Para `05_cena_complexa.png`, selecionar recortes do barco, das flores, das montanhas e dos reflexos.

---

## 8. Integridade dos arquivos

Os hashes SHA-256 dos arquivos preparados são:

```text
00_controle_16_cores.png  98eb22cbfdd5a86248d041d6145bca50271b6f2e2f9ce8fa0d5ef738c4d41451
01_poucas_cores.png       6e110dcb853e7c2a0a2c07ac6db02f8f5f4ba26f5f41efe136232d7b382bd9ac
02_gradiente_suave.png    0370cad367f2cc5949e476c772c4ce215b76ca9b70998b40ceb5dec0544c5695
03_alta_saturacao.png     6ef409201f6de90421a76d704a22bfad8a416da3df6e3251ab83a7e825f286c3
04_cor_rara.png           1abe774a67e29548a15e5309a8aed994a85da22d41012e64317f4454ab592158
05_cena_complexa.png      e6ef3a5e5dd34e9307e459739d9575f4c0f840e844398212c047492b01ce423b
```

Para conferir um arquivo em Python:

```python
from pathlib import Path
import hashlib

arquivo = Path("data/raw/00_controle_16_cores.png")
hash_sha256 = hashlib.sha256(arquivo.read_bytes()).hexdigest()
print(hash_sha256)
```

Se uma imagem for alterada, recortada, redimensionada ou novamente salva, o hash será diferente. Nesse caso, atualize este README e registre a alteração no relatório.

---

## 9. Licença, origem e uso

As imagens foram geradas com auxílio de inteligência artificial para uso neste projeto acadêmico. Não foram obtidas por download de bancos fotográficos ou páginas da internet.

Ao publicar o repositório ou o relatório:

- informar que as imagens são sintéticas ou geradas com IA;
- não atribuir autoria fotográfica a terceiros;
- não apresentar as cenas como registros documentais de locais ou eventos reais;
- preservar esta documentação junto ao conjunto de dados;
- verificar as normas da instituição sobre declaração de conteúdo gerado por IA.

---

## 10. Versionamento no Git

O `.gitignore` recomendado ignora o conteúdo de `data/raw/` para evitar o versionamento acidental de imagens grandes ou sujeitas a restrições. Como estas imagens foram preparadas para o projeto, há duas opções.

### Opção A: manter as imagens fora do Git

Preservar as regras:

```gitignore
data/raw/*
!data/raw/.gitkeep
```

Distribuir as imagens em pacote separado e manter este README no repositório.

### Opção B: versionar somente estas seis imagens

Adicionar exceções ao `.gitignore`:

```gitignore
data/raw/*
!data/raw/.gitkeep
!data/raw/00_controle_16_cores.png
!data/raw/01_poucas_cores.png
!data/raw/02_gradiente_suave.png
!data/raw/03_alta_saturacao.png
!data/raw/04_cor_rara.png
!data/raw/05_cena_complexa.png
```

Antes de escolher a opção B, verificar o limite de tamanho e a política do repositório utilizado.

---

## 11. Checklist antes da execução

- [ ] os seis arquivos estão em `data/raw/`;
- [ ] os nomes dos arquivos não foram alterados;
- [ ] todas as imagens estão em PNG;
- [ ] todas as imagens possuem 512 × 512 pixels;
- [ ] todas as imagens estão em RGB;
- [ ] os hashes correspondem aos registrados neste README;
- [ ] a imagem de controle foi separada das cinco imagens principais na análise;
- [ ] o arquivo `config/experiments.yaml` aponta para `data/raw`;
- [ ] os resultados de validação anteriores foram arquivados ou removidos;
- [ ] as cinco sementes oficiais estão configuradas;
- [ ] o dispositivo de execução foi registrado.

---

## 12. Observação final

O conjunto foi construído para permitir uma análise que vá além da comparação de uma única métrica. As conclusões devem considerar simultaneamente:

- distorção no espaço RGB;
- diferença perceptual de cor;
- preservação topológica;
- distribuição e utilização dos protótipos;
- preservação de cores raras;
- formação de faixas em gradientes;
- qualidade visual localizada;
- custo computacional.

A comparação final não deve buscar apenas um vencedor geral. O objetivo é identificar em quais perfis de imagem cada método apresenta vantagens, limitações e compromissos entre fidelidade cromática, organização topológica e tempo de execução.
