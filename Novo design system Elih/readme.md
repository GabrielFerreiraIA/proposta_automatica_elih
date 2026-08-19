# Elih Seguros — Design System

Corretora de planos de saúde, odontológicos e seguro de vida (parceira do SEESP —
Sindicato dos Enfermeiros do Estado de São Paulo). Este sistema substitui o antigo
visual "Executive / Clinical" (obsidiana + prata metálica) por uma identidade mais
clara, calorosa e familiar — adequada a uma corretora que fala diretamente com
associados sobre saúde e cuidado, não a um banco de investimentos.

**Gatilho da mudança:** a logo antiga (três traços metálicos formando um "E") foi
trocada por uma wordmark redonda e amigável ("elih seguros") sobre um novo azul-marinho
`#011246`. Este sistema deriva toda a paleta, tipografia e componentes a partir dessa
logo nova.

## Fontes desta extração
- `uploads/ELIH-DESIGN-SYSTEM.md` — catálogo do sistema visual antigo (referência de estrutura, não de cor/tipo).
- `uploads/Nova Logo 1.jpg`, `uploads/Nova Logo 2.jpg`, `uploads/Logo Circular.png`, `uploads/2.png`, `uploads/1.png` — novos logos oficiais (azul `#011246`).
- `uploads/pasted-1783577356813-0.png` — site portfólio antigo (SEESP × Elih), a ser refeito numa próxima etapa com este sistema.

## Índice
- `styles.css` — entry point (importa todos os tokens).
- `tokens/colors.css` — escala navy, neutros, accent, semânticas + aliases.
- `tokens/typography.css` — Plus Jakarta Sans (display, v1.1) + Nunito (corpo), escala tipográfica.
- `tokens/effects.css` — radius, spacing, sombras, motion.
- `assets/logo/` — logos oficiais:
  - `elih-mark-navy-circle.png` — mark circular (fundo transparente).
  - `elih-seguros-wordmark-navy.png` — wordmark navy sobre transparente.
  - `elih-seguros-lockup-white-on-navy.png` — versão branca, para uso sobre `--navy-900`/`--navy-950`.
- `guidelines/` — specimen cards: `colors-navy`, `colors-neutral`, `colors-accent-semantic`,
  `type-pairing`, `type-display-scale`, `type-body-scale`, `type-before-after` (Fredoka × Plus Jakarta Sans),
  `spacing`, `radius`, `shadows`, `logo`.
- `components/core/` — `Button`, `Badge`, `SectionHeader`, `PlanCard`, `Navbar`, `Input`.
- `components/dark/` — componentes para **seções de fundo navy** com elementos brancos/azul-claro:
  `DarkSection` (wrapper full-bleed), `DarkStatCard`, `DarkChecklistItem`, `DarkCTACard`,
  `DarkTestimonial`, `PartnerLogoStrip`.
  (Componentes inferidos do screenshot do site antigo — ver aviso no final deste arquivo.)

## v1.1 — correção de tipografia + seções navy
Depois do rebuild do site com a v1.0, os títulos ficaram "infantis": Fredoka é uma fonte
bolha/toy em tamanhos grandes, e isso desviou da proposta "humanizada mas profissional".
Trocamos a fonte de display por **Plus Jakarta Sans** (geométrica, com juntas levemente
arredondadas — mantém o tom acessível sem parecer brinquedo) e ajustamos tracking. **Nunito
no corpo foi mantido** — a redondeza dela não incomoda em texto corrido, só em título grande.
Ver `guidelines/type-before-after.card.html` para o comparativo lado a lado.

Também adicionamos `components/dark/` para cobrir os blocos de fundo navy inteiro com
texto branco e acentos azul-claro que apareciam no site antigo (banner de parceria com
operadoras, mapa de cobertura, card de cotação) e que a v1.0 não tinha componentizado.

## Intentional additions
Nenhum código-fonte do site foi disponibilizado — apenas um screenshot do portfólio antigo
e o catálogo do sistema visual anterior. Os 6 componentes acima cobrem os padrões visíveis
no screenshot (navbar pill, cards de plano/oferta, botões primário/secundário, badges de
categoria, formulário de cotação, títulos de seção). Não foram adicionados componentes que
não aparecem no material de origem (ex: Tabs, Dialog, Toast) — se o rebuild do site precisar
deles, criar sob demanda.

---

## CONTENT FUNDAMENTALS

- **Tom:** consultivo e direto, nunca corporativo-frio nem "vendedor". Fala como um
  consultor de confiança, não como um portal de comparação de preços.
- **Pessoa:** trata o leitor por "você". Frases curtas, verbos de ação ("Encontrar
  meu plano", "Solicite sua cotação", "Descobrir benefícios").
  Exemplo real do site: "Condições exclusivas para associados." e "Planos de saúde,
  odonto e vida com o atendimento próximo e consultivo da Elih Seguros."
- **Prova social / especificidade > adjetivos vagos:** preços reais ("a partir de
  R$ 109,14/mês"), nomes de operadoras reais (Ameplan, Hapvida, Blue Med), condições
  concretas ("isenção analítica na recomendação") em vez de "as melhores condições do mercado".
  Exemplo: "Mais do que um plano. Uma orientação certa para sua escolha." e "Sem 0800
  e sem robôs. Você fala direto com quem resolve — da dúvida à contratação."
- **Estrutura de rótulos:** overlines curtos em CAIXA ALTA (`VITRINE DE OFERTAS`,
  `TODOS OS BENEFÍCIOS`, `POR QUE ELIH`, `COTAÇÃO ESPECIAL`) acima de cada título de seção.
- **CTAs:** verbo + benefício + seta (↗ ou →): "Encontrar meu plano ↗", "Iniciar
  cotação →", "Saiba mais ↗".
- **Emoji:** não são usados. Ícones (Lucide) substituem qualquer necessidade de emoji.
- **Disclaimers legais:** sempre presentes no rodapé, tom neutro/legal, fonte pequena.

---

## VISUAL FOUNDATIONS

### De "metálico" para "confiável e caloroso"
O sistema antigo usava luz/sombra sobre prata para hierarquia ("o acento é o brilho,
não uma cor"). A nova identidade inverte isso: **o azul `#011246` É o acento** — usado
com intenção sobre fundos majoritariamente brancos/claros. Sem gradientes prata, sem
bordas metálicas, sem grid blueprint.

### Cor
- **Navy `--navy-900` (`#011246`)** é a cor de marca — usada em texto de destaque,
  botões primários, headers/footers escuros pontuais e no mark circular.
  A escala completa (`--navy-50`…`--navy-950`) mantém o mesmo matiz (H225) em toda a
  faixa tonal — nada de azul genérico ou cinza-azulado desconectado da marca.
- **Fundo predominante é branco/quase-branco** (`--bg-page`, `--bg-section`). O navy
  aparece em blocos inteiros (hero alternativo, footer, banners de parceria) — nunca
  como fundo geral de página.
- **Accent sky (`--accent-500`)** é reservado a links, foco, e pequenos destaques
  (badges de destaque, ícone ativo) — nunca compete com o navy como cor primária.
- **Semânticas** (`--success`, `--warning`, `--danger`) só aparecem em contexto de
  status de cotação/plano (ex: "economize até 35%", alertas de formulário).
- Texto sobre branco usa `--text-primary` (`--navy-950`, não preto puro) para manter
  o texto "na família" do azul de marca.

### Tipografia
- **Plus Jakarta Sans** (display, v1.1) — títulos, overlines, números de destaque (preços, %).
  Geométrica com juntas levemente arredondadas: mantém um tom acessível sem cair no
  "bolha/infantil" que a Fredoka produzia em títulos grandes. Pesos 600–800.
  > Substituiu Fredoka na v1.1 — Fredoka lia como brinquedo em h1/h2 reais, incoerente
  > com o tom "consultivo e direto" de uma corretora falando com RH/procurement.
- **Nunito** (corpo) — parágrafos, UI, labels de formulário, texto de card. Mantida sem
  alteração: a redondeza dela é praticamente imperceptível em corpo de texto e é o que
  sustenta a sensação "humanizada" do sistema — o problema estava só nos títulos grandes.
- Hierarquia de peso: h1/h2 em Plus Jakarta Sans 700; overlines em 600 uppercase tracking
  0.14em; corpo em Nunito 400, ênfases em Nunito 700.
- `text-wrap: balance` em títulos de 2+ linhas.
- Use a classe utilitária `.heading` (`tokens/typography.css`) sempre que escrever um
  h1/h2/h3 fora do componente `SectionHeader`.

### Forma e espaço
- **Radius generoso** (12–28px) e **pills** (`--radius-full`) em botões/chips/badges —
  ecoa o círculo do mark e as curvas da wordmark. Nunca cantos vivos (0–4px) em cards
  ou botões.
- **Sombras** são suaves e tingidas de navy (`rgba(1,18,70,…)`), nunca pretas puras,
  nunca coloridas em accent — a sombra sugere profundidade, não decoração.
- Cards: fundo branco, borda `1px solid var(--border-subtle)`, `--shadow-sm` em repouso,
  `--shadow-md` no hover, leve `translateY(-2px)`.

### Seções de fundo navy (branco + azul-claro sobre `--navy-900`/`--navy-950`)
Além do uso pontual de navy descrito acima, o sistema agora tem componentes dedicados
para blocos full-bleed inteiramente escuros — usados para 1–2 momentos de "peso" por
página (prova social/parceria, mapa de cobertura, cotação), nunca no corpo geral:
- `DarkSection` — wrapper full-bleed navy, com curva branca opcional no topo para a
  transição vindo de uma seção clara.
- `DarkStatCard` — card translúcido (`rgba(255,255,255,0.05)` + borda `--border-on-dark`)
  para métricas/credenciais ("100%", "8 de 10", "SLA Direct").
- `DarkChecklistItem` — check circular em anel translúcido + texto branco.
- `DarkCTACard` — card navy-950 flutuante com badge, título e CTA (o mais escuro do
  sistema, usado como painel de destaque, não como seção inteira).
- `DarkTestimonial` — card translúcido de depoimento (aspas + citação + avatar/nome/cargo),
  mesma família visual do `DarkStatCard`; usar 2–3 por linha dentro de um `DarkSection`.
- `PartnerLogoStrip` — chips com logos de parceiros, dessaturados/clareados para
  consistência sobre navy.
Dentro dessas seções, títulos usam `SectionHeader surface="dark"`; texto secundário usa
`--text-on-dark-secondary`; qualquer destaque pontual (um número, uma palavra) usa
`--accent-300` (`#7db4f7`) — nunca branco puro para o acento, para não competir com o título.
- Bordas metálicas com máscara `xor` (`.edge`) — removidas.
- Grid *blueprint* que desaparece radialmente (`.grid-fade`) — removida.
- Ruído/grain SVG — removido.
- Glassmorphism como efeito onipresente — mantido apenas como utilitário pontual
  (`.glass-dark`) para uso sobre blocos navy escuros (ex: card flutuante de campanha),
  bem mais sutil que antes (sem saturação exagerada).
- Playfair Display (toques editoriais) — removida; a marca agora fala só através de
  Plus Jakarta Sans + Nunito.
- Fredoka (v1.0 → v1.1) — removida como fonte de display; lia como infantil/toy em
  títulos grandes. Ver seção "v1.1" no topo deste arquivo.

### Movimento
- Mantido o espírito "sutil" do sistema antigo, mas sem os efeitos 3D/parallax de
  cursor (não combinam com uma marca mais simples e confiável).
- Entrada de seção: `opacity 0→1`, `translateY(16px→0)`, `var(--duration-slow)`,
  `var(--ease-out)`, uma vez ao entrar na viewport.
- Hover de botão/card: cor + sombra + `translateY(-2px)`, `var(--duration-base)`.
- Sempre respeitar `prefers-reduced-motion`.

### Iconografia
- **Lucide** (`lucide-react` ou CDN `unpkg.com/lucide-static`) — mantido do sistema
  antigo. `strokeWidth` sobe de 1–1.5 (traço fino/frio) para **1.75–2** (traço mais
  espesso, mais amigável, combina com a wordmark arredondada).
  Ícones em contêiner: quadrado/circular `radius-md`+, fundo `--navy-50` ou
  `--accent-100`, ícone em `--navy-900` ou `--accent-700`.
- Não são usados emojis, pictogramas customizados desenhados à mão, nem unicode como ícone.

---

## Aviso
Este pacote define **fundações + componentes core + componentes de seção navy**.
Componentes específicos do site (navbar pill, offer card, plan card, blocos de fundo
navy) foram inferidos do screenshot do site antigo (`pasted-1783577356813-0.png` e,
na v1.1, os screenshots adicionais de seções reais já usando a v1.0) já que não há
acesso ao código-fonte — a geometria/hierarquia foi preservada, só a pele visual foi
trocada. Se houver acesso ao repositório real do site, revisar `components/` contra
o código fonte.
