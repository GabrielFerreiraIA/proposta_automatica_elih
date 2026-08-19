import React from 'react';

/**
 * @typedef {Object} PartnerLogoStripProps
 * @property {{src: string, alt: string}[]} logos
 */
export function PartnerLogoStrip({ logos = [] }) {
  return (
    <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', justifyContent: 'center' }}>
      {logos.map((l, i) => (
        <div
          key={i}
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid var(--border-on-dark)',
            borderRadius: 'var(--radius-md)',
            padding: '14px 22px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minWidth: 120,
            height: 56,
          }}
        >
          <img src={l.src} alt={l.alt} style={{ maxHeight: 22, maxWidth: 110, filter: 'grayscale(1) brightness(4)', opacity: 0.75 }} />
        </div>
      ))}
    </div>
  );
}
