Translucent stat/credential card for use inside `DarkSection` grids (social proof rows: "100% independência comercial", "8 de 10 parceria elite", "SLA Direct suporte sem 0800"). Not a standalone card for light backgrounds — use `PlanCard`/regular cards there instead.

```jsx
<div style={{display:'flex', gap: 20}}>
  <DarkStatCard value="100%" label="Independência comercial" description="Isenção analítica absoluta." />
  <DarkStatCard value="8 de 10" label="Parceria elite do país" description="Acesso de alto nível às maiores operadoras." />
  <DarkStatCard value="SLA Direct" label="Suporte sem 0800" description="RH livre de centrais telefônicas." />
</div>
```
