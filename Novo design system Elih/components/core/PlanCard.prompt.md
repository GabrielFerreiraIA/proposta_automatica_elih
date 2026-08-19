Full plan/product card — used in "Conheça todos os planos" grids. Composes category label, optional highlight tag, title/description, a checklist of features, and a price + CTA footer.

```jsx
<PlanCard
  category="Plano de Saúde"
  tag="MAIS ESCOLHIDO"
  title="São Cristóvão Saúde"
  description="Quatro categorias — Essencial, Conforto, Bem-estar e Select — com rede própria e credenciada."
  features={['Rede própria e credenciada', 'Referência em saúde e bem-estar', 'Tradição, excelência e humanização']}
  price="R$ 232,81/mês"
  priceNote="Categoria Essencial (adesão)"
/>
```

Keep `features` to 3 items max (matches source density). `tag` is optional — only the standout plan per grid gets one.
