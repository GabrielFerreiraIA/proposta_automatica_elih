Floating pill navbar — light/white replacement for the old dark glass pill. Sits on white or light section backgrounds with a soft shadow instead of a dark blurred glass surface.

```jsx
<Navbar
  logo={<img src="/assets/logo/elih-seguros-wordmark-navy.png" style={{height: 28}} />}
  links={[{label:'Benefícios'}, {label:'Planos'}, {label:'Por que Elih'}]}
  cta={<Button size="sm">Cotação</Button>}
/>
```

Always rounded-full, white background, subtle border + shadow-sm (no backdrop-blur needed against a solid white/light section).
