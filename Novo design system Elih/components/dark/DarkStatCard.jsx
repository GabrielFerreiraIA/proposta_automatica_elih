import React from 'react';

/**
 * @typedef {Object} DarkStatCardProps
 * @property {string} value - big headline figure, e.g. "100%" or "8 de 10"
 * @property {string} label - short caps label under the value
 * @property {string} [description]
 */
export function DarkStatCard({ value, label, description }) {
  return (
    <div
      style={{
        flex: 1,
        minWidth: 220,
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid var(--border-on-dark)',
        borderRadius: 'var(--radius-lg)',
        padding: 24,
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
        fontFamily: 'var(--font-body)',
      }}
    >
      <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 'var(--text-2xl)', color: '#ffffff', letterSpacing: 'var(--tracking-tight)' }}>
        {value}
      </div>
      <div style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 'var(--text-xs)', textTransform: 'uppercase', letterSpacing: 'var(--tracking-overline)', color: 'var(--accent-300, #7db4f7)' }}>
        {label}
      </div>
      {description && (
        <p style={{ fontSize: 'var(--text-sm)', lineHeight: 'var(--leading-relaxed)', color: 'var(--text-on-dark-secondary)', margin: 0 }}>{description}</p>
      )}
    </div>
  );
}
