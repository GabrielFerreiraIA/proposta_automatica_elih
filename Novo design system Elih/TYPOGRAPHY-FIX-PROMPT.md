# Prompt de correção — tipografia + seções navy (v1.0 → v1.1 do Elih Seguros Design System)

Use este prompt nos projetos que **já foram migrados** para o novo design system Elih
Seguros (v1.0, com Fredoka) e só precisam do ajuste de tipografia + dos novos
componentes de seção navy — não é uma migração do zero.

---

Já migrei este app para o novo design system Elih Seguros (v1.0), mas os títulos ficaram
muito infantis — a Fredoka é redonda/bolha demais em tamanhos grandes de título, o que
tirou peso e credibilidade da marca. Preciso corrigir só a tipografia de título, sem
tocar em cor, radius, sombra, layout ou nos demais componentes. Aplique:

**1. Troque a fonte de display de Fredoka para Plus Jakarta Sans em todo o app:**
```css
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Nunito:wght@400;500;600;700;800&display=swap');

--font-display: 'Plus Jakarta Sans', ui-sans-serif, 'SF Pro Display', sans-serif;
```
- **Nunito no corpo de texto continua igual** — não mexa em parágrafos/UI/labels, o
  problema era só a fonte de título/display.
- Onde havia `font-family: 'Fredoka', ...` diretamente (fora do token `--font-display`),
  troque também.

**2. Ajustes finos que acompanham a troca de fonte** (Plus Jakarta Sans tem métricas
diferentes de Fredoka — sem isso os títulos ficam soltos/gappy):
- `letter-spacing` de títulos: de `-0.01em` para `-0.02em`.
- `letter-spacing` de overlines/uppercase: de `0.16em` para `0.14em`.
- Peso de h1/h2: mantenha 700 (não suba para 800 só porque a fonte é mais "neutra" —
  isso reintroduziria peso excessivo).
- Não aumente o tamanho dos títulos para compensar — o objetivo é reduzir a
  personalidade "toy", não aumentar a escala.

**3. Não altere:**
- A paleta navy/neutros/accent — inalterada.
- Radius, sombras, spacing — inalterados.
- Nunito no corpo — inalterada.
- Botões, badges, cards — só o texto de título dentro deles muda de fonte, a forma
  (pill, radius) permanece.

**4. Novidade opcional — componentes de seção navy:**
Se este app tem (ou vai ter) blocos de fundo 100% navy com texto branco/azul-claro
(banner de parceria com operadoras, mapa de cobertura, cotação em destaque), o design
system agora tem componentes prontos para isso em vez de recriar do zero:
`DarkSection`, `DarkStatCard`, `DarkChecklistItem`, `DarkCTACard`, `PartnerLogoStrip`.
Copie-os de `components/dark/` no design system anexado, em vez de estilizar manualmente.
Use-os com moderação — 1–2 blocos navy por página, o resto do app permanece claro.

Se este projeto tiver acesso ao design system "Elih Seguros — Design System" (Design
System attachment), use `tokens/typography.css` (v1.1) e `components/dark/` de lá
diretamente em vez de recriar os valores acima manualmente.
