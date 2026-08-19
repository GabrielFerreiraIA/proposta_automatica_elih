# Elih — Design System

> Extraído do site oficial da Elih (`Site Elih/Site_Elih`, Next.js 15 + Tailwind 3 + Framer Motion).
> Estética: **"Executive / Clinical"** — obsidiana profunda + branco clínico, acentos em platina/prata,
> vidro (glassmorphism), bordas metálicas e grade *blueprint*. **Sem neon, sem cores saturadas.**
> Sofisticação corporativa de seguros premium.

---

## 1. Filosofia visual

| Princípio | Aplicação |
|---|---|
| **Dual-tone** | Superfícies escuras (`obsidian`/`corp-navy`) para impacto; superfícies claras (`clinical`/`pristine`) para conteúdo e confiança. |
| **Metálico, não colorido** | Hierarquia por luz/sombra e gradientes prata — não por matiz. O acento é o *brilho*, não uma cor. |
| **Vidro fosco** | Painéis e navbar usam `backdrop-blur` + saturação para profundidade. |
| **Tipografia editorial** | Inter para corpo, Space Grotesk para *overlines*/rótulos técnicos, Playfair para toques editoriais. |
| **Movimento sutil** | Parallax leve, *idle bob*, tilt 3D no cursor, repulsão de cards. Sempre respeitando `prefers-reduced-motion`. |

---

## 2. Paleta de cores

### Dark / Executive
| Token | HEX | HSL (shadcn) | Uso |
|---|---|---|---|
| `obsidian` | `#020617` | `229 84% 5%` | Fundo principal escuro, texto sobre claro |
| `corp-navy` | `#0F172A` | `222 47% 11%` | Hover de botões escuros, destaque de palavra |
| `deep-navy` | `#0C1324` | `223 50% 9%` | Gradientes de vidro escuro |
| `graphite` | `#1E293B` | `217 33% 17%` | Texto secundário, bordas em superfície clara |
| `platinum` | `#E2E8F0` | `214 32% 91%` | Texto principal sobre escuro |
| `cool-gray` | `#C5C6CB` | `229 5% 78%` | Texto terciário |

### Light / Clinical
| Token | HEX | HSL (shadcn) | Uso |
|---|---|---|---|
| `pristine` | `#FFFFFF` | `0 0% 100%` | Texto sobre escuro, botões claros |
| `clinical` | `#F8FAFC` | `210 40% 98%` | Fundo de seções claras (hero) |
| `soft-slate` | `#E5E7EB` | `220 13% 91%` | Divisores em superfície clara |
| `inst-blue` | `#CBD5E1` | `213 27% 84%` | Bordas suaves, estados disabled |

> **Opacidades características:** texto usa `/65` `/70` `/75` `/85` `/90`; bordas usam `/10` `/15` `/20`;
> vidro usa `rgba(15,23,42,0.65)`→`rgba(12,19,36,0.5)`.

---

## 3. Tipografia

| Família | Variável | Pesos | Papel |
|---|---|---|---|
| **Inter** | `--font-inter` | 400, 500, 600, 700, 800 | Corpo, títulos (sans padrão) |
| **Space Grotesk** | `--font-grotesk` | 400, 500 | *Overlines*, rótulos, métricas, micro-copy técnica |
| **Playfair Display** | `--font-playfair` | 400, 500, 600, 700 + itálico | Toques editoriais, citações |

### Escala de títulos
```
h1  text-[1.8rem] → sm:2.1rem → lg:2.25rem → xl:2.5rem   font-extrabold  tracking-tight  leading-[1.08]
h2  text-3xl → sm:4xl → lg:5xl                            font-bold       tracking-tight
sub text-base → sm:lg                                      leading-relaxed  text-balance
```

### Overline (assinatura da marca)
```
font-grotesk  uppercase  tracking-[0.18em]  text-xs  font-medium
```
Classe utilitária: `.overline`. Usada acima de cada título de seção.

---

## 4. Raios, sombras e espaçamento

**Border radius:** botões `10–11px` · chips/pills `rounded-full` · cards pequenos `rounded-2xl (16px)` · painéis `rounded-[20px]` · imagem hero `rounded-[28px]`→`lg:rounded-[34px]`.

**Sombras (todas em obsidiana, sem cor):**
```
card/painel   0 24px 60px -30px rgba(2,6,23,0.6)
navbar idle   0 14px 40px -22px rgba(2,6,23,0.5)
navbar scroll 0 18px 44px -18px rgba(2,6,23,0.55)
floating card 0 18px 44px -14px rgba(2,6,23,0.55)
botão hero    0 6px 20px -6px rgba(2,6,23,0.24)  → hover 0 10px 26px -6px rgba(2,6,23,0.32)
```

**Letter-spacing nomeado:** `overline = 0.18em`. **Max-width custom:** `8xl = 88rem`.

---

## 5. Efeitos / utilitários assinatura

| Classe | O que faz |
|---|---|
| `.glass-dark` | Gradiente `rgba(15,23,42,.65)`→`rgba(12,19,36,.5)` + `blur(20px) saturate(1.2)` |
| `.glass-light` | Gradiente branco translúcido + mesmo blur |
| `.edge` + `.edge-soft` / `.edge-strong` | **Borda metálica**: máscara `xor` com gradiente prata brilhante nos cantos (1px) |
| `.grid-fade` | Grade *blueprint* 64×64 que some radialmente (mask radial) |
| `.grain` | Overlay de ruído `feTurbulence` em SVG, `opacity 0.03`, `mix-blend overlay` |
| `.divider-platinum` | `border-platinum/10` |
| `.text-balance` | `text-wrap: balance` |

> A **borda metálica** (`edge`) é o detalhe mais característico da marca: aparece na navbar, nos cards
> flutuantes, no frame da imagem e nos badges. Combine `.edge .edge-soft` (sutil) ou `.edge-strong` (forte).

---

## 6. Componentes

### Botão primário
```
onDark:  bg-pristine text-obsidian hover:bg-platinum
onLight: bg-obsidian text-pristine hover:bg-corp-navy
base:    inline-flex items-center gap-2.5 px-6 py-3.5 rounded-[10px] text-sm font-semibold
         transition-colors duration-200
ícone:   <ArrowUpRight> translada no hover (group-hover:translate-x-0.5 -translate-y-0.5)
```

### Botão secundário (outline)
```
onDark:  border-platinum/20 text-platinum hover:border-platinum/60 hover:text-pristine
onLight: border-graphite/20 text-graphite hover:border-graphite/60 hover:text-obsidian
base:    border px-6 py-3.5 rounded-[10px] text-sm font-semibold
```

### Botão "metálico" (hero secundário) — premium
```
fundo:  linear-gradient(160deg, rgba(255,255,255,.96), rgba(241,245,249,.92))
sombra: inset 0 1px 0 rgba(255,255,255,.9), 0 0 0 1px rgba(15,23,42,.72), 0 4px 14px -4px rgba(15,23,42,.18)
sheen:  linha superior bg-gradient-to-r from-transparent via-white to-transparent
```

### GlassPanel
```
dark:  glass-dark border-platinum/10
light: glass-light border-graphite/10
base:  border rounded-[20px] shadow-[0_24px_60px_-30px_rgba(2,6,23,0.6)]
```

### Navbar (pill flutuante)
- Pílula central `glass-dark rounded-2xl` com `.edge .edge-soft`.
- Encolhe no scroll: `max-w-6xl h-16` → `max-w-4xl h-14` (transição 500ms).
- Links: `text-platinum/70 hover:text-pristine hover:bg-white/[0.06]`.
- CTA: botão primário `onDark`.
- Mobile: overlay `glass-dark` full-screen com stagger de Framer Motion.

### Floating card (hero)
- Vidro escuro custom + `.edge` + *corner sheen* radial.
- Ícone Lucide `strokeWidth={1.5}` num quadrado `bg-white/[0.06] border-white/10 rounded-[10px]`.
- Título em `font-grotesk uppercase tracking-[0.14em]`; texto em `font-sans text-platinum/55`.

---

## 7. Movimento (Framer Motion)

| Animação | Parâmetros |
|---|---|
| Ease padrão | `[0.22, 1, 0.36, 1]` (easeOutExpo-like) |
| Entrada de seção | `opacity 0→1`, `y 12–22→0`, `duration 0.5–0.72`, `whileInView once` |
| `pulse-soft` | opacity 0.6↔1, 3s infinito |
| `marquee` | translateX 0→-50%, 40s linear (trust bar) |
| Idle bob | `y: [0,-6,0]`, 5–7s, easeInOut |
| Tilt 3D | rotateX/Y ±9°, perspective 1200, spring |
| Repulsão de card | raio 175px, força 32px, spring stiffness 110 |
| Glare no cursor | radial `rgba(255,255,255,.16)` seguindo ponteiro, `mix-blend-overlay` |

**Sempre** condicionar a `useReducedMotion()`.

---

## 8. Ícones e libs

- **Ícones:** `lucide-react` (`strokeWidth` 1–1.5 para o traço fino premium).
- **Animação:** `framer-motion`.
- **Partículas/sparkles:** `@tsparticles` (usado pontualmente).
- **Utilitário de classes:** `clsx` + `tailwind-merge` → `cn()`.

---

## 9. Logo

PNG oficial (fundo removido):
```
https://res.cloudinary.com/dxpfoolyp/image/upload/q_auto/f_auto/v1780425930/ELIH_PNG-removebg-preview_c3koqg.png
```
Uso na navbar: `h-10 sm:h-12 w-auto object-contain`.

---

## 10. Arquivos desta extração

| Arquivo | Conteúdo |
|---|---|
| `ELIH-DESIGN-SYSTEM.md` | Este catálogo. |
| `elih-tokens.css` | Tokens HSL shadcn (light + dark) + classes utilitárias (`glass`, `edge`, `grid-fade`, `grain`, `overline`) prontos para colar no `src/index.css`. |
| `elih-tailwind.snippet.ts` | Bloco `theme.extend` (cores, fontes, radius, sombras, keyframes) para o `tailwind.config.ts`. |

> Próximo passo sugerido: aplicar `elih-tokens.css` + snippet ao CRM e rebrandar componente a componente
> (sidebar → navbar pill, cards → GlassPanel, remover glow neon).
