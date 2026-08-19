Translucent quote card for `DarkSection` social-proof rows — same visual family as `DarkStatCard` (rgba white card on navy) but for a client/associate quote instead of a metric. Falls back to an initial-letter avatar when no photo is available (don't fabricate a stock photo).

```jsx
<div style={{display:'flex', gap: 20}}>
  <DarkTestimonial
    quote="Trocamos de operadora sem burocracia nenhuma — a Elih cuidou de tudo, do diagnóstico à implantação."
    name="Márcia Duarte"
    role="RH, Grupo Contabilis"
  />
  <DarkTestimonial
    quote="Atendimento direto, sem 0800. Resolvemos uma inclusão emergencial em minutos pelo WhatsApp."
    name="Renato Alves"
    role="Associado SEESP"
  />
</div>
```

Use 2–3 per row inside a `DarkSection`. Keep quotes short (1–2 sentences) — real, specific claims (as in the source content), never generic praise.
