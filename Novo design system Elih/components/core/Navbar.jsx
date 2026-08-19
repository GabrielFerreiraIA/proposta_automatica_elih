import React from 'react';

/**
 * @typedef {Object} NavLink
 * @property {string} label
 * @property {string} [href]
 *
 * @typedef {Object} NavbarProps
 * @property {React.ReactNode} logo
 * @property {NavLink[]} links
 * @property {React.ReactNode} [cta]
 */
export function Navbar({ logo, links = [], cta }) {
  return (
    <nav
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 24,
        padding: '14px 28px',
        background: '#ffffff',
        borderRadius: 'var(--radius-full)',
        boxShadow: 'var(--shadow-sm)',
        border: '1px solid var(--border-subtle)',
        fontFamily: 'var(--font-body)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>{logo}</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 28 }}>
        {links.map((l, i) => (
          <a
            key={i}
            href={l.href || '#'}
            style={{
              fontSize: 'var(--text-sm)',
              fontWeight: 700,
              color: 'var(--text-secondary)',
              textDecoration: 'none',
            }}
          >
            {l.label}
          </a>
        ))}
      </div>
      <div>{cta}</div>
    </nav>
  );
}
