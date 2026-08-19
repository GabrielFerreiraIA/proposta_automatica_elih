Full-bleed navy section wrapper. Use for the 1–2 "weight" moments per page that should
read as a deliberate break from the white page — partnership/social-proof banners,
the coverage-map section, footer. Handles max-width container + padding; you still
lay out children (SectionHeader with `surface="dark"`, DarkStatCard grid, etc.) inside.

```jsx
<DarkSection curveTop>
  <SectionHeader surface="dark" align="center" overline="Parceria com as maiores operadoras" title="Acesso premium às melhores redes do Brasil." />
  <div style={{display:'flex', gap: 20, marginTop: 40}}>
    <DarkStatCard value="100%" label="Independência comercial" description="Isenção analítica absoluta." />
    <DarkStatCard value="8 de 10" label="Parceria elite do país" description="Acesso de alto nível às maiores operadoras." />
  </div>
</DarkSection>
```

`curveTop` only when the section directly follows a white/light section — never stack two `curveTop` sections back to back.
