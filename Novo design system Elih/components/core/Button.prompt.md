Pill-shaped call-to-action button, used for every primary/secondary action in the product (hero CTAs, card links, form submits).

```jsx
<Button variant="primary" surface="light">Encontrar meu plano</Button>
<Button variant="secondary" surface="light" withArrow={false}>Ver ofertas especiais</Button>
<Button variant="primary" surface="dark">Descobrir benefícios</Button>
```

Variants:
- `primary` — solid navy (light surface) or solid white (dark surface). Highest emphasis, one per section.
- `secondary` — outlined, `--border-strong`. Use next to a primary button.
- `ghost` — no border/fill, text only with hover background. Use inline / in dense rows (card footers).

`surface="dark"` flips colors for use on navy/black backgrounds (hero banners, footer).
Always defaults `withArrow` to `true` — the ↗ is a signature brand detail; only turn off for secondary/neutral actions like "Ver ofertas especiais".
