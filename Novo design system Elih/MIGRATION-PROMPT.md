# Prompt de migração — sistema visual antigo → Elih Seguros (novo, v1.1)

Cole este prompt no projeto de cada aplicação que ainda usa o design system antigo
("Executive / Clinical" — obsidiana + metálico) para adaptá-la ao novo sistema Elih Seguros.
Já reflete a v1.1 do sistema (Plus Jakarta Sans no lugar de Fredoka + componentes de seção
navy) — se um projeto já foi migrado usando a v1.0 com Fredoka, use em vez disso
`TYPOGRAPHY-FIX-PROMPT.md`, que é um ajuste pontual mais rápido.

---

Preciso migrar esta aplicação do design system visual antigo da Elih para o novo. Aplique
as seguintes mudanças em todo o app, mantendo estrutura, layout, conteúdo e componentes —
troque apenas a pele visual (cor, tipografia, radius, sombra, efeitos):

**1. Cor — pare de usar obsidiana/metálico como base. Nova cor de marca: `#011246`.**
- Fundo de página passa a ser predominantemente branco/quase-branco, não mais escuro.
  O navy escuro só aparece em blocos inteiros e pontuais (hero alternativo, footer,
  banners de parceria) — nunca como fundo geral.
- Troque toda referência a `obsidian` (#020617), `corp-navy` (#0F172A), `deep-navy` (#0C1324)
  pela nova escala navy abaixo (mesmo matiz H225 em toda a faixa):
  `#f2f5ff` `#e1e8fe` `#c9d6fd` `#a9bdf9` `#7796f3` `#3e69ea` `#1142d4` `#0931aa`
  `#042381` `#02195f` `#011246` (base) `#010b28`
- Troque `platinum`/`cool-gray`/`graphite` por neutros frios (leve tom azulado, não cinza puro):
  `#fafbfd` `#f2f4f7` `#e7e9ef` `#d6d9e1` `#b3b9c6` `#878fa1` `#606a80` `#454c5f` `#2d3443`
  `#1a202e` `#0d121c`
- Adicione um accent sky reservado a links/foco/pequenos destaques (nunca como cor primária):
  `#e2eefd` (100) `#2582f4` (500) `#0f5cc4` (700)
- Semânticas para status de cotação/plano: success `#298e5f`, warning `#f29e0d`, danger `#d3222e`
  (cada um com tom claro ~100 para fundo de badge/alerta).
- Texto sobre branco usa o navy mais escuro (`#010b28`/`#011246`), nunca preto puro.

**2. Tipografia — troque Inter/Space Grotesk/Playfair por:**
- **Plus Jakarta Sans** (display: títulos, overlines, números/preços em destaque) — pesos
  600–800. Geométrica com juntas levemente arredondadas: soa acessível sem parecer
  infantil/brinquedo em títulos grandes (h1/h2 reais).
- **Nunito** (corpo: parágrafos, UI, labels, texto de card) — pesos 400/600/700/800.
- Overlines continuam uppercase, tracking ~0.14em, em Plus Jakarta Sans 600.
- ⚠️ Não use Fredoka — foi a escolha inicial do novo sistema e foi descartada por ler
  como infantil em títulos grandes (ver `guidelines/type-before-after.card.html` no
  design system para o comparativo).

**3. Remova os efeitos "metálicos/vidro pesado" do sistema antigo:**
- Remova bordas metálicas com máscara `xor` (`.edge`, `.edge-soft`, `.edge-strong`).
- Remova a grade *blueprint* que desaparece radialmente (`.grid-fade`).
- Remova o overlay de ruído/grain SVG.
- Glassmorphism deixa de ser efeito onipresente — mantenha só como utilitário pontual e
  sutil (`.glass-dark`, sem saturação exagerada), aplicado apenas sobre blocos navy escuros
  (ex: card flutuante de campanha), nunca sobre fundo claro.

**4. Forma e sombra:**
- Radius mais generoso e arredondado em tudo: botões e badges viram pill (`border-radius:
  9999px`); cards usam 16–28px (não mais cantos quase retos).
- Sombras deixam de ser pretas puras/duras — usar tom navy suave:
  `rgba(1,18,70, opacidade baixa)` em vez de `rgba(2,6,23, …)`.
- Cards: fundo branco, borda 1px sutil, sombra leve em repouso, sombra média + leve
  `translateY(-2px)` no hover.

**5. Movimento:**
- Mantenha entradas de seção suaves (fade + translateY, ~400ms, easeOutExpo) mas **remova**
  o tilt 3D no cursor e a repulsão de cards — não combinam com uma marca mais simples.
- Hover de botão/card: cor + sombra + leve elevação, nada de brilho/glare.

**6. Logo:**
- Troque qualquer uso do símbolo metálico antigo (três traços formando um "E") pela nova
  logo: mark circular navy `elih-mark-navy-circle.png`, wordmark `elih-seguros-wordmark-navy.png`
  (navy sobre transparente, para uso em claro) e `elih-seguros-lockup-white-on-navy.png`
  (branco, para uso sobre navy escuro).

**7. Componentes de referência (já adaptados no novo design system):**
Button (pill, primary/secondary/ghost, `surface="dark"/"light"`), Badge (pill, tons
neutral/navy/accent/success/warning), SectionHeader (overline + título Plus Jakarta Sans
+ descrição Nunito), PlanCard, Navbar (pill branca flutuante, não mais vidro escuro), Input.

**8. Seções de fundo navy inteiro (branco + azul-claro sobre `--navy-900`/`--navy-950`):**
Se o app antigo tinha blocos escuros de prova social, mapa/cobertura, ou cotação em
destaque, não recrie do zero — use os componentes prontos: `DarkSection` (wrapper
full-bleed, com curva branca opcional no topo), `DarkStatCard` (métricas/credenciais),
`DarkChecklistItem` (check branco em anel translúcido), `DarkCTACard` (card navy-950
flutuante com badge+CTA), `PartnerLogoStrip` (logos de parceiros em chips translúcidos).
Reserve esses blocos para 1–2 momentos de "peso" por página — o resto do app continua
predominantemente branco.

Se este projeto tiver acesso ao design system "Elih Seguros — Design System" (Design System
attachment), copie tokens e componentes de lá em vez de recriar os valores acima manualmente.

---
