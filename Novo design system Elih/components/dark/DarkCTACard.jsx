import React from 'react';

/**
 * @typedef {Object} DarkCTACardProps
 * @property {string} [badge] - small pill label, e.g. "COTAÇÃO SIMPLIFICADA"
 * @property {React.ReactNode} title
 * @property {string} [description]
 * @property {React.ReactNode} [action] - usually a light Button (surface="dark" not needed — parent bg is already navy)
 */
export function DarkCTACard({ badge, title, description, action }) {
  return (
    <div
      style={{
        background: 'var(--navy-950)',
        borderRadius: 'var(--radius-2xl)',
        padding: 40,
        display: 'flex',
        flexDirection: 'column',
        gap: 18,
        fontFamily: 'var(--font-body)',
        boxShadow: 'var(--shadow-dark-lg)',
      }}
    >
      {badge && (
        <span
          style={{
            alignSelf: 'flex-start',
            background: 'rgba(255,255,255,0.08)',
            color: 'var(--accent-300, #7db4f7)',
            fontFamily: 'var(--font-display)',
            fontWeight: 600,
            fontSize: 'var(--text-xs)',
            letterSpacing: 'var(--tracking-overline)',
            textTransform: 'uppercase',
            padding: '6px 14px',
            borderRadius: 'var(--radius-full)',
          }}
        >
          {badge}
        </span>
      )}
      <h3
        style={{
          fontFamily: 'var(--font-display)',
          fontWeight: 700,
          fontSize: 'var(--text-xl)',
          color: '#ffffff',
          letterSpacing: 'var(--tracking-tight)',
          lineHeight: 'var(--leading-snug)',
          margin: 0,
          textWrap: 'balance',
        }}
      >
        {title}
      </h3>
      {description && (
        <p style={{ fontSize: 'var(--text-base)', color: 'var(--text-on-dark-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>
          {description}
        </p>
      )}
      {action && <div style={{ marginTop: 8 }}>{action}</div>}
    </div>
  );
}
