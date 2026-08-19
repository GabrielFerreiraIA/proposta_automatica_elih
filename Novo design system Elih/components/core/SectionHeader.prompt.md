Standard section intro: uppercase overline + Fredoka title + optional Nunito description. Used above every major section ("VITRINE DE OFERTAS", "TODOS OS BENEFÍCIOS", "POR QUE ELIH").

```jsx
<SectionHeader
  overline="Vitrine de ofertas"
  title="Ofertas em destaque para associados SEESP"
  action={<CarouselArrows />}
/>
```

`surface="dark"` for use on navy section backgrounds. `action` is for a right-aligned control (carousel arrows, filter button) — omit for simple centered headers.
