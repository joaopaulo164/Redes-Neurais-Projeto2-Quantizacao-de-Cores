# README do `.gitignore`
## Projeto 2: Quantização de cores com SOM, GNG e k-means

## Índice de navegação

- [README principal](README.md)
- [Comece aqui](COMECE_AQUI.md)
- [Guia de automação](AUTOMACAO.md)
- [Quick start](AUTOMATE_QUICK_START.md)
- [Pipeline completo](PIPELINE_COMPLETO.md)

## Descrição

Este documento explica as decisões adotadas no arquivo `.gitignore` do projeto. O objetivo é manter o repositório **reproduzível, leve e independente do ambiente local**, evitando o versionamento de ambientes virtuais, caches, credenciais, resultados intermediários, modelos treinados e configurações pessoais de IDE.

---

## 1. Onde colocar os arquivos

Coloque os dois arquivos na raiz do projeto:

```text
projeto_2_redes_neurais/
├── .gitignore
├── README_GITIGNORE.md
├── README.md
├── requirements.txt
├── config/
├── data/
├── outputs/
├── report/
├── scripts/
├── src/
└── tests/
```

O nome do arquivo principal deve ser exatamente:

```text
.gitignore
```

Ele não deve receber extensão adicional, como `.txt`.

---

## 2. Princípios utilizados

O arquivo foi preparado a partir dos seguintes princípios:

1. **Não versionar o ambiente virtual**. A pasta `.venv/` é específica de cada máquina e pode ser reconstruída por meio do `requirements.txt`.
2. **Não versionar caches e arquivos temporários**. Esses arquivos são gerados automaticamente pelo Python, pelos testes ou pelas ferramentas de análise.
3. **Não versionar segredos ou configurações locais**. Arquivos `.env`, credenciais e configurações privadas devem permanecer fora do repositório.
4. **Não versionar todas as saídas experimentais**. Checkpoints, reconstruções, gráficos e métricas podem ocupar muito espaço e são reproduzíveis pelos scripts.
5. **Preservar a estrutura das pastas**. Arquivos `.gitkeep` permanecem versionados em diretórios que ficariam vazios.
6. **Permitir configurações portáveis do VS Code**. Alguns arquivos da pasta `.vscode/` podem ser compartilhados, desde que não contenham caminhos absolutos ou dados pessoais.
7. **Preservar as evidências finais selecionadas**. A pasta `report/assets/` pode armazenar apenas figuras e tabelas efetivamente citadas no relatório.

---

## 3. Ambientes virtuais Python

São ignorados:

```gitignore
.venv/
venv/
env/
ENV/
```

Essas pastas contêm uma instalação local do Python e das dependências. Elas variam conforme:

- sistema operacional;
- versão do Python;
- arquitetura do processador;
- instalação com CPU ou CUDA;
- caminhos locais do usuário.

O ambiente deve ser reconstruído com:

```bash
python -m venv .venv
```

Depois, deve ser ativado e receber as dependências:

```bash
pip install -r requirements.txt
```

---

## 4. Caches e arquivos compilados

São ignorados diretórios e arquivos como:

```text
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
```

Eles são produzidos por:

- interpretador Python;
- pytest;
- ferramentas de tipagem;
- linters;
- ferramentas de cobertura.

Esses arquivos não fazem parte do código-fonte e podem ser recriados automaticamente.

---

## 5. Configurações do Visual Studio Code

A regra adotada é:

```gitignore
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json
!.vscode/launch.json
!.vscode/tasks.json
```

Isso significa:

- arquivos locais ou não previstos dentro de `.vscode/` são ignorados;
- quatro configurações úteis podem ser versionadas;
- configurações portáveis podem ser compartilhadas entre os integrantes do projeto.

### Arquivos que podem ser compartilhados

- `settings.json`: configurações do projeto, pytest e análise de código;
- `extensions.json`: extensões recomendadas;
- `launch.json`: perfis de depuração;
- `tasks.json`: tarefas para testes e experimentos.

### O que não deve aparecer nesses arquivos

Evite caminhos absolutos como:

```json
{
  "python.defaultInterpreterPath": "C:\\Users\\nome_do_usuario\\projeto\\.venv\\Scripts\\python.exe"
}
```

Esse caminho funcionaria somente em uma máquina.

É preferível selecionar o interpretador localmente pelo VS Code ou utilizar configurações relativas e portáveis.

---

## 6. PyCharm e IDEs da JetBrains

São ignorados:

```gitignore
.idea/
*.iml
*.ipr
*.iws
```

Esses arquivos normalmente contêm preferências locais da IDE, caminhos e estado da área de trabalho.

---

## 7. Arquivos do sistema operacional

O `.gitignore` inclui arquivos produzidos automaticamente por:

- Windows, como `Thumbs.db` e `Desktop.ini`;
- macOS, como `.DS_Store`;
- Linux, como `.directory` e arquivos temporários NFS.

Esses itens não têm relação com a implementação ou com os experimentos.

---

## 8. Variáveis de ambiente e credenciais

São ignorados:

```gitignore
.env
.env.*
*.pem
*.key
credentials.json
secrets.json
config/local.yaml
config/private.yaml
```

A exceção é:

```gitignore
!.env.example
```

Assim, pode-se versionar um modelo sem segredos:

```dotenv
DEVICE=cpu
DATA_DIR=data/raw
OUTPUT_DIR=outputs
```

Nunca coloque senhas, tokens, chaves privadas ou credenciais reais no `.env.example`.

---

## 9. Dados de entrada

As pastas de dados são ignoradas, mantendo apenas `.gitkeep`:

```gitignore
data/raw/*
!data/raw/.gitkeep
```

A mesma estratégia é aplicada a:

```text
data/processed/
data/interim/
data/external/
```

Isso é importante porque as imagens podem:

- ser grandes;
- possuir restrições de redistribuição;
- ter licença incompatível com o repositório;
- variar entre os ambientes de execução.

### Documentação dos dados

O arquivo abaixo pode ser versionado:

```text
data/README.md
```

Ele deve informar, quando aplicável:

- nome da imagem;
- perfil experimental;
- origem;
- licença;
- resolução;
- instruções para obtenção;
- hash do arquivo.

### Quando versionar as imagens

Se todas as imagens forem pequenas e tiverem licença compatível, remova ou adapte as regras de `data/raw/`.

Outra alternativa é criar exceções específicas:

```gitignore
data/raw/*
!data/raw/.gitkeep
!data/raw/01_poucas_cores.png
!data/raw/02_gradiente_suave.png
```

Somente use essa estratégia depois de confirmar a licença de redistribuição.

---

## 10. Resultados dos experimentos

As seguintes pastas têm seu conteúdo ignorado:

```text
outputs/checkpoints/
outputs/reconstructed/
outputs/figures/
outputs/metrics/
outputs/tables/
outputs/logs/
```

Os respectivos arquivos `.gitkeep` continuam versionados.

Essa decisão evita incluir automaticamente:

- centenas de figuras;
- modelos treinados;
- resultados repetidos;
- arquivos de execução preliminar;
- métricas que podem ser reproduzidas pelos scripts.

### Preservar resultados importantes

Para preservar uma rodada oficial, recomenda-se uma destas alternativas:

1. publicar as saídas como artefato de uma versão ou release;
2. armazená-las em serviço apropriado para dados e modelos;
3. criar um pacote compactado fora do Git;
4. copiar somente as evidências citadas para `report/assets/`.

---

## 11. Checkpoints e modelos treinados

São ignoradas extensões comuns:

```gitignore
*.pt
*.pth
*.ckpt
*.onnx
*.pkl
*.pickle
*.joblib
```

Esses arquivos podem ser grandes e, no caso de formatos serializados como `pickle`, não devem ser tratados como código-fonte comum.

Se algum modelo final precisar ser distribuído, prefira:

- release do repositório;
- armazenamento de artefatos;
- serviço de modelos;
- Git LFS, se autorizado e configurado.

---

## 12. CSVs e resultados tabulares

O `.gitignore` não ignora todos os arquivos CSV globalmente. Isso é intencional.

Um projeto pode possuir CSVs pequenos e importantes, como:

- metadados das imagens;
- catálogo dos experimentos;
- documentação do conjunto de dados;
- resultados finais consolidados selecionados.

Os CSVs produzidos dentro de `outputs/` já são ignorados pelas regras do diretório.

São ignorados globalmente formatos normalmente usados para grandes volumes:

```gitignore
*.parquet
*.feather
```

Se um desses arquivos for essencial e pequeno, ele pode ser incluído com uma exceção explícita.

---

## 13. Imagens e figuras

O arquivo não contém regras globais como:

```gitignore
*.png
*.jpg
*.jpeg
```

Essas regras seriam excessivamente amplas e poderiam impedir o versionamento de:

- imagens do README;
- diagramas da documentação;
- evidências finais do relatório;
- arquivos legítimos em `report/assets/`.

As figuras geradas automaticamente já são ignoradas em `outputs/figures/`.

---

## 14. Relatórios

O relatório automaticamente gerado é ignorado:

```gitignore
report/relatorio_gerado.md
```

O relatório-base editado manualmente pode continuar versionado:

```text
report/relatorio_final.md
```

Também são ignorados arquivos auxiliares de LaTeX e o diretório:

```text
report/generated/
```

### Evidências finais

A pasta abaixo não é ignorada:

```text
report/assets/
```

Use-a para versionar apenas:

- reconstruções selecionadas;
- mapas de erro citados;
- gráficos consolidados;
- tabelas finais;
- figuras efetivamente usadas no relatório.

---

## 15. Arquivos compactados

São ignorados:

```gitignore
*.zip
*.tar
*.tar.gz
*.tgz
*.7z
*.rar
```

Isso evita o envio acidental de:

- cópias completas do projeto;
- backups locais;
- pacotes duplicados;
- resultados compactados muito grandes.

Se um arquivo compactado for parte intencional de uma entrega, utilize `git add -f arquivo.zip` somente depois de verificar seu conteúdo e tamanho.

---

## 16. Arquivos `.gitkeep`

O Git não versiona diretórios vazios. Por isso, utiliza-se um arquivo vazio chamado `.gitkeep`.

Exemplo:

```text
outputs/figures/.gitkeep
```

A regra:

```gitignore
outputs/figures/*
!outputs/figures/.gitkeep
```

ignora todo o conteúdo gerado, mas mantém a pasta no repositório.

Se os arquivos ainda não existirem, crie-os.

### Linux e macOS

```bash
touch data/raw/.gitkeep
touch outputs/checkpoints/.gitkeep
touch outputs/reconstructed/.gitkeep
touch outputs/figures/.gitkeep
touch outputs/metrics/.gitkeep
touch outputs/tables/.gitkeep
touch outputs/logs/.gitkeep
```

### Windows PowerShell

```powershell
New-Item data/raw/.gitkeep -ItemType File -Force
New-Item outputs/checkpoints/.gitkeep -ItemType File -Force
New-Item outputs/reconstructed/.gitkeep -ItemType File -Force
New-Item outputs/figures/.gitkeep -ItemType File -Force
New-Item outputs/metrics/.gitkeep -ItemType File -Force
New-Item outputs/tables/.gitkeep -ItemType File -Force
New-Item outputs/logs/.gitkeep -ItemType File -Force
```

---

## 17. Verificar se as regras funcionam

Depois de colocar o `.gitignore` na raiz, execute:

```bash
git status
```

A pasta `.venv/` e os arquivos gerados em `outputs/` não devem aparecer como novos arquivos.

Para verificar qual regra ignora um item:

```bash
git check-ignore -v .venv/
```

Para um checkpoint:

```bash
git check-ignore -v outputs/checkpoints/modelo.pt
```

Para uma imagem de entrada:

```bash
git check-ignore -v data/raw/01_poucas_cores.png
```

O Git exibirá a regra responsável pelo bloqueio.

---

## 18. Arquivos já rastreados pelo Git

O `.gitignore` não remove arquivos que já estejam sendo rastreados.

Se `.venv/` já foi adicionada:

```bash
git rm -r --cached .venv
```

Se `outputs/` já foi adicionado:

```bash
git rm -r --cached outputs
```

Se `data/raw/` já foi adicionado:

```bash
git rm -r --cached data/raw
```

Depois, adicione novamente os arquivos que devem permanecer:

```bash
git add .gitignore README_GITIGNORE.md
git add data/raw/.gitkeep
git add outputs/checkpoints/.gitkeep
git add outputs/reconstructed/.gitkeep
git add outputs/figures/.gitkeep
git add outputs/metrics/.gitkeep
git add outputs/tables/.gitkeep
git add outputs/logs/.gitkeep
```

Finalize com:

```bash
git commit -m "Configura arquivos ignorados do projeto"
```

---

## 19. Arquivos recomendados para versionamento

Normalmente devem ser versionados:

```text
.gitignore
README.md
README_GITIGNORE.md
requirements.txt
config/experiments.yaml
src/
scripts/
tests/
report/relatorio_final.md
report/assets/
data/README.md
data/raw/.gitkeep
outputs/checkpoints/.gitkeep
outputs/reconstructed/.gitkeep
outputs/figures/.gitkeep
outputs/metrics/.gitkeep
outputs/tables/.gitkeep
outputs/logs/.gitkeep
```

Também podem ser versionados, se forem portáveis:

```text
.vscode/settings.json
.vscode/extensions.json
.vscode/launch.json
.vscode/tasks.json
```

---

## 20. Arquivos que normalmente não devem ser versionados

```text
.venv/
__pycache__/
.pytest_cache/
.idea/
.env
config/local.yaml
config/private.yaml
data/raw/*.png
outputs/checkpoints/*.pt
outputs/reconstructed/*.png
outputs/figures/*.png
outputs/metrics/runs.csv
outputs/tables/summary.csv
report/relatorio_gerado.md
```

---

## 21. Ajustes futuros

O `.gitignore` deve acompanhar a evolução do projeto. Revise-o quando ocorrer alguma destas mudanças:

- adoção de nova IDE;
- uso de Jupyter Notebook;
- introdução de Docker;
- geração de documentos em PDF, DOCX ou LaTeX;
- uso de TensorBoard;
- inclusão de novos formatos de dados;
- adoção de Git LFS;
- implantação de pipeline de integração contínua;
- mudança na política de versionamento dos resultados.

Antes de adicionar uma nova regra global, avalie se ela pode ocultar arquivos relevantes do projeto.

---

# Recomendação final

A política adotada mantém no Git o código, os testes, as configurações reproduzíveis e as evidências finais selecionadas. Ao mesmo tempo, mantém fora do repositório os ambientes locais, os dados potencialmente restritos e a grande quantidade de artefatos produzida pelas execuções.

O arquivo `.gitignore` não substitui uma política de organização. A equipe ainda deve documentar as imagens utilizadas, registrar os hiperparâmetros, preservar a rodada oficial e selecionar conscientemente quais evidências serão incorporadas ao relatório final.
