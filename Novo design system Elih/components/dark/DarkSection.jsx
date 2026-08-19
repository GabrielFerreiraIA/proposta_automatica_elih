import React from 'react';

/**
 * @typedef {Object} DarkSectionProps
 * @property {React.ReactNode} children
 * @property {'900'|'950'} [tone] - which navy to use as background
 * @property {boolean} [curveTop] - render a soft concave curve at the top edge (the
 *   transition seen where a light section rolls into a dark one)
 */
export function DarkSection({ children, tone = '900', curveTop = false }) {
  const bg = tone === '950' ? 'var(--navy-950)' : 'var(--navy-900)';
  return (
    <section
      style={{
        position: 'relative',
        background: bg,
        padding: '96px 0',
        overflow: 'hidden',
      }}
    >
      {curveTop && (
        <svg
          viewBox="0 0 100 6"
          preserveAspectRatio="none"
          style={{ position: 'absolute', top: -1, left: 0, width: '100%', height: 48, display: 'block' }}
        >
          <path d="M0,6 Q50,0 100,6 L100,0 L0,0 Z" fill="#ffffff" />
        </svg>
      )}
      <div style={{ maxWidth: 'var(--max-width)', margin: '0 auto', padding: '0 32px', position: 'relative' }}>
        {children}
      </div>
    </section>
  );
}
