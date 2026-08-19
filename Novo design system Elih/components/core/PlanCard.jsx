import React from 'react';

/**
 * @typedef {Object} PlanCardProps
 * @property {string} category - e.g. "Plano de Saúde"
 * @property {string} tag - e.g. "MAIS ESCOLHIDO"
 * @property {string} title
 * @property {string} description
 * @property {string[]} features
 * @property {string} priceLabel - e.g. "a partir de"
 * @property {string} price - e.g. "R$ 232,81/mês"
 * @property {string} [priceNote] - small line under price, e.g. plan tier name
 * @property {() => void} [onDetails]
 */
export function PlanCard({ category, tag, title, description, features = [], priceLabel = 'a partir de', price, priceNote, onDetails }) {
  const [hover, setHover] = React.useState(false);
  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        background: '#ffffff',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-xl)',
        padding: 28,
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
        boxShadow: hover ? 'var(--shadow-md)' : 'var(--shadow-sm)',
        transform: hover ? 'translateY(-2px)' : 'translateY(0)',
        transition: 'all var(--duration-base) var(--ease-out)',
        fontFamily: 'var(--font-body)',
        minWidth: 280,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          {category}
        </span>
        {tag && (
          <span style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--accent-700)', background: 'var(--accent-100)', padding: '4px 10px', borderRadius: 'var(--radius-full)' }}>
            {tag}
          </span>
        )}
      </div>

      <div>
        <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 'var(--text-lg)', color: 'var(--text-primary)', margin: '0 0 6px 0' }}>{title}</h3>
        <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 }}>{description}</p>
      </div>

      <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {features.map((f, i) => (
          <li key={i} style={{ display: 'flex', gap: 8, fontSize: 'var(--text-sm)', color: 'var(--text-primary)' }}>
            <span style={{ color: 'var(--success-500)', fontWeight: 700 }}>✓</span>
            {f}
          </li>
        ))}
      </ul>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', paddingTop: 8, borderTop: '1px solid var(--border-subtle)' }}>
        <div>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>{priceLabel}</div>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 'var(--text-lg)', color: 'var(--navy-900)' }}>{price}</div>
          {priceNote && <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' }}>{priceNote}</div>}
        </div>
        <button
          onClick={onDetails}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontFamily: 'var(--font-display)',
            fontWeight: 600,
            fontSize: 'var(--text-sm)',
            color: 'var(--navy-900)',
            display: 'flex',
            alignItems: 'center',
            gap: 4,
          }}
        >
          Saiba mais ↗
        </button>
      </div>
    </div>
  );
}
