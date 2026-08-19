Floating navy-950 CTA panel — the darkest surface in the system, used as a standalone
card next to lighter content (e.g. "Faça sua cotação simples" beside a light description
column). Not a full-bleed section — a contained card with its own strong shadow.

```jsx
<DarkCTACard
  badge="Cotação simplificada"
  title={<>Faça sua cotação simples — você pode reduzir em até <span style={{color:'var(--accent-300)'}}>30%</span> o valor do seu plano atual.</>}
  description="São perguntas rápidas e diretas. Leva menos de um minuto."
  action={<Button variant="primary" surface="dark">Começar cotação</Button>}
/>
```

Use inline `<span style={{color:'var(--accent-300)'}}>` to highlight one figure/word in the title, matching the "30%" accent treatment.
