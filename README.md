# Cotador-Elih

Aplicação web mobile-first (PWA instalável) que lê os PDFs de cotação da
plataforma (agencialink) e devolve **uma** proposta remodelada no design system
da Elih: **capa + 3 páginas de informação**, com copy persuasiva, comparativo
entre operadoras, quebras de objeção e checklist de documentos.

Aceita **até 5 PDFs de uma vez** — um por operadora, como sai da plataforma — e
unifica tudo numa proposta só.

**Nenhuma informação do PDF original é alterada.** Valores, faixas etárias, rede
credenciada e tabela de reembolso são reproduzidos literalmente. O que a
ferramenta faz é selecionar, ordenar e diagramar — nunca reescrever um número.

---

## Como rodar no seu PC

```bash
pip install -r requirements.txt
python -m playwright install chromium
python -m uvicorn app.main:app --reload --port 8000
```

Abra `http://127.0.0.1:8000`. No Windows, dá para usar o atalho `iniciar.bat`.

Para acessar do celular na mesma rede Wi-Fi, suba com
`--host 0.0.0.0` e use `http://SEU-IP-LOCAL:8000`.

---

## Como usar

1. **Envie as cotações** — de 1 a 5 PDFs, um por operadora. Também funciona com
   um "mega PDF" que já traga várias operadoras empilhadas, ou uma mistura dos dois.
2. **Confirme os dados.** A tela mostra o que foi lido e pergunta:
   - **Quais planos entram na proposta** — todos os produtos encontrados aparecem
     numa lista. O primeiro que você marcar (★) é o recomendado; marque de 2 a 4
     para gerar a página de comparação lado a lado.
   - **Região** — as macro-regiões vêm do próprio PDF (São Paulo capital,
     Interior, ABCD, Alto Tietê, Baixada Santista, Grande São Paulo, Vale do
     Paraíba, Campinas e Região, Sorocaba e Região). Opcionalmente dá para
     filtrar cidades ou zonas específicas.
   - **Cliente já tem plano ativo?** Muda a lista de documentos e ativa o bloco
     de aproveitamento de carência.
   - **Tipo de CNPJ** — MEI acrescenta o CCMEI; Limitada acrescenta o contrato social.
   - **Abrangência / coparticipação** — perguntadas **por plano**, e só para os
     planos em que o PDF não declara. A ferramenta prefere perguntar a supor.
3. **Gere e baixe.**

---

## O que sai no PDF

O documento tem uma seção completa **por plano cotado** — cada operadora tem a sua
própria rede credenciada e a sua própria tabela de reembolso, então cada uma ganha
o seu descritivo.

| Página | Conteúdo |
|---|---|
| Capa | A sua imagem de `assets/capa/`, inteira e sem sobreposição. Sem arquivo, uma capa navy gerada com nome do plano, total, selos e dados do consultor |
| Comparativo | *(só com 2+ planos)* Coluna por plano com logo da operadora, **ponto forte de cada opção**, total mensal, valores por faixa etária, abrangência, coparticipação, obstetrícia, reembolso, remissão, adesão e tamanho da rede. Coluna recomendada destacada em navy, com o bloco "Como ler esta tabela" |
| Plano *(por opção)* | Logo da operadora, nome do produto, selos, resumo do que está sendo contratado, valores por faixa etária, total do grupo e tabela per capita quando agrega |
| Rede *(por opção)* | Contadores da região, principais hospitais e laboratórios distribuídos por zona/cidade, cidades cobertas e a tabela de reembolso **daquela** operadora |
| Fechamento | Quebras de objeção, próximos passos, documentos necessários, aproveitamento de carência, CTA e disclaimer |

Total de páginas: `1 (capa) + 1 (comparativo, se houver) + 2 × nº de planos + 1
(fechamento)`. Um plano dá 4 páginas; dois dão 7; quatro dão 11.

**Ponto forte de cada opção.** Na tabela comparativa, cada plano recebe o critério
mais forte em que ele ganha e que nenhum outro já tenha levado — "Menor
mensalidade", "Maior rede hospitalar", "Abrangência nacional", "Sem
coparticipação", "Com remissão", "Menor custo por vida" e assim por diante. Nada
disso é opinião: todos saem de um número ou atributo que já está na tabela, e um
critério empatado entre duas opções não é usado, porque não ajuda a decidir
(`aplica_destaques()` em `app/copy_engine.py`).

**Cabeçalho.** Só a marca da Elih. O nome do plano e a tabela de referência saíram
dali: numa proposta com várias operadoras a informação ficava errada nas páginas
dos outros planos.

O volume de conteúdo se ajusta sozinho: o Chromium mede o transbordo real de cada
página e a aplicação reduz listas até tudo caber, sempre preservando as quebras de
objeção primeiro (`VARIANTES` em `app/renderer.py`).

---

## Personalização

### Capa

Coloque a imagem em **`assets/capa/capa.png`** (aceita `.png`, `.jpg`, `.webp`).

A capa personalizada é tratada como uma **peça fechada**: ela entra inteira, sem
nenhum texto por cima, porque normalmente já traz logo, título e assinatura no
próprio desenho. Os dados dinâmicos (consultor, contato, data de emissão) migram
para uma faixa de identificação no topo da página seguinte.

Sem arquivo, a ferramenta gera uma capa navy com nome do plano, total mensal,
selos e dados do consultor.

### Logos das operadoras

Coloque os arquivos em **`assets/logos_operadoras/`** (a pasta `Logos_Operadoras/`
na raiz também é lida). O nome do arquivo só precisa conter o nome da operadora:
`bradesco-saude-logo.webp`, `9-sulamerica-saude-logo-0.png` e `sulamerica.png`
funcionam igual. Sem logo, entra um selo tipográfico no padrão Elih.

### Textos

| O quê | Onde |
|---|---|
| Quebras de objeção | `objecoes()` em `app/copy_engine.py` |
| Resumo do plano | `resumo_plano()` |
| Próximos passos e documentos | `proximos_passos()` |
| Diferenciais da Elih | `DIFERENCIAIS_ELIH` |
| Hospitais que ganham destaque | `PRESTIGIO` em `app/parser.py` |
| Frases de leitura do comparativo | `_leitura_comparativo()` em `app/copy_engine.py` |
| Cores, fontes, espaçamento | `app/static/css/proposta.css` |

---

## Motor de copy

**Camada de regras (sempre ativa).** Cada bloco é montado a partir de atributos que
o parser leu literalmente do PDF. Atributo ausente, bloco ausente — é assim que a
proposta nunca promete cobertura que o plano não tem.

**Camada de IA (opcional).** Com `OPENAI_API_KEY` no ambiente, o modelo reescreve
resumo e objeções no tom da marca. Ele recebe uma lista fechada de fatos e é
proibido de introduzir números.

Duas travas na saída:

- `_valida_reescrita()` recusa a resposta se aparecer qualquer valor, percentual,
  prazo ou contagem que não esteja no texto original. A comparação normaliza
  pontuação e espaço (`R$109,76.` = `R$ 109,76`) para não acusar uma reescrita
  honesta, mas pega valor inventado, percentual novo, contagem de rede inflada e
  conta derivada ("sai por R$26,38 ao dia").
- `_taxa_reescrita()` descarta a saída quando o modelo devolve o texto
  praticamente igual — nesse caso a copy de regras, revisada por humano, é melhor
  que uma cópia dela.

Recusa, erro de rede ou ausência de chave caem de volta na copy de regras — a
geração nunca falha por causa da IA. O campo `motor` no JSON de resposta diz qual
camada produziu o texto e quanto foi reescrito.

**Modelo.** Padrão `gpt-4o-mini`. Os três candidatos passaram 4/4 na validação com
a carga real e produzem texto equivalente; troque por `ELIH_MODELO_IA`:

| Modelo | Custo por proposta | Observação |
|---|---|---|
| `gpt-4.1-nano` | ~R$ 0,0016 | mais barato |
| `gpt-4o-mini` | ~R$ 0,0023 | **padrão** |
| `gpt-4.1-mini` | ~R$ 0,0063 | texto um pouco mais fluido |

---

## Deploy com Docker / Easypanel

```bash
docker compose up -d --build
```

No **Easypanel**:

1. Crie um serviço **App** apontando para o repositório do GitHub.
2. Build: **Dockerfile** (o da raiz).
3. Porta interna: **8000**.
4. Variável de ambiente `OPENAI_API_KEY` (opcional).
5. Monte um volume em **`/app/assets`** para trocar capa e logos sem rebuildar.

A imagem base é a oficial do Playwright, que já traz Chromium e as bibliotecas de
sistema para renderização — não é preciso instalar fontes ou dependências extras.

---

## PWA — instalar no celular

O app é instalável com o nome **Cotador-Elih** e o ícone próprio.

- **Android / Chrome / Edge:** aparece o botão **Instalar** no cabeçalho.
- **iPhone / Safari:** o iOS não permite instalação automática. Um aviso explica o
  caminho: **Compartilhar → Adicionar à Tela de Início**.

Instalado, abre em tela cheia, sem barra de navegador. O service worker guarda só
a casca da interface — upload, análise e geração sempre vão ao servidor.

Para a instalação funcionar o site precisa ser servido por **HTTPS** (ou
`localhost`). No Easypanel, basta ativar o certificado do domínio.

Os ícones são gerados a partir de `Logo PWA APP/`. Para trocar, substitua a
imagem e rode de novo o trecho de geração de ícones descrito em `app/static/img/`.

---

## Estrutura

```
app/
  parser.py        extração determinística do PDF (nunca infere)
                   Documento -> blocos -> colunas de preço
  copy_engine.py   copy por regras + refinamento opcional por IA
  renderer.py      montagem do contexto, HTML -> PDF, auto-ajuste de página
  main.py          API FastAPI e interface
  templates/       proposta.html (PDF) e index.html (web)
  static/          css/proposta.css (impressão), css/fontes.css (fontes embutidas),
                   css/app.css (web), app.js, sw.js, manifest.webmanifest, ícones
scripts/
  gerar_fontes.py  regenera css/fontes.css (só quando trocar de fonte)
assets/
  capa/                 sua capa personalizada
  logos_operadoras/     logos das operadoras
output/          PDFs gerados (não versionado)
```

## Como o parser lê o PDF

O gerador da plataforma usa cor e posição de forma consistente, e é isso que
identifica o papel de cada linha:

| x | cor | peso | papel |
|---|---|---|---|
| 23 | 7107965 | normal | nome do prestador |
| >450 | 2172201 | normal | tipos de atendimento |
| 23 | 6513507 | negrito | categoria (Hospitais / Laboratórios / Rede Própria) |
| 31 | 6709595 | negrito | cidade ou zona |
| 23 | 2172201 | negrito | macro-região |

Tabelas de valores e reembolso são reconstruídas por agrupamento geométrico de
palavras em linhas e colunas, não por parsing de texto corrido — por isso
funcionam com uma ou várias colunas de plano e acomodação.

### Fontes e geração offline

As fontes ficam embutidas em base64 em `app/static/css/fontes.css`, e o CSS entra
inline no HTML. A geração do PDF não faz **nenhuma** requisição de rede — testado
com todo o tráfego do Chromium bloqueado. Antes disso, com `@import` do Google
Fonts, 1 em 90 cenários falhava por timeout esperando a fonte; numa VPS sem saída
para a internet, falhariam todos.

### PDFs com várias operadoras

O rótulo **"Valores"** em negrito aparece exatamente uma vez por cotação, e é ele
que delimita os blocos. O corte real fica no topo da página do último título grande
antes do próximo "Valores" — que é a abertura do bloco seguinte. Cortar ali (e não
no primeiro título) evita que a página de reembolso, que repete o mesmo título no
topo, vaze para a cotação de baixo.

Cada bloco carrega seu próprio título, operadora, referência, condições, tabela de
preços, rede credenciada e reembolso. Um bloco pode ainda ter várias colunas de
preço (produtos ou acomodações diferentes da mesma operadora) — na interface, cada
combinação bloco + coluna é uma opção contratável, identificada como `"bloco:coluna"`.

Quando chegam vários arquivos, `unifica()` concatena os blocos de todos eles na
ordem de envio, e os índices `"bloco:coluna"` passam a valer para o conjunto. Do
ponto de vista do resto do sistema, tanto faz se as 4 opções vieram de 4 PDFs ou
de um só.

### Ajuste de página

O Chromium mede o transbordo real de cada página, e **cada página tem seus
próprios controles de densidade** (`NIVEIS` em `app/renderer.py`): a página do
plano encolhe o resumo, a de rede encolhe as listas, a de fechamento encolhe as
objeções. Só a página que transborda é reduzida — antes, uma escada única fazia a
rede do Interior comer as quebras de objeção sem sequer resolver o próprio
estouro.

Duas formas de corte silencioso já apareceram e estão cobertas: conteúdo que
extrapola a altura (medido via DOM) e tabela quebrada pela paginação do Chromium e
comida pelo `overflow:hidden` (resolvido com `break-inside: avoid` e verificado
pelo **texto extraído do PDF gerado**, não só pelo layout).
