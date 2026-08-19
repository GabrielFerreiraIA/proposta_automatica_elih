import React from 'react';

/**
 * @typedef {Object} DarkTestimonialProps
 * @property {string} quote
 * @property {string} name
 * @property {string} role - e.g. "RH, Empresa XPTO" or "Associada SEESP"
 * @property {string} [avatarSrc]
 */
export function DarkTestimonial({ quote, name, role, avatarSrc }) {
  return (
    <div
      style={{
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid var(--border-on-dark)',
        borderRadius: 'var(--radius-xl)',
        padding: 32,
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        fontFamily: 'var(--font-body)',
        minWidth: 280,
        flex: 1,
      }}
    >
      <span
        style={{
          fontFamily: 'var(--font-display)',
          fontSize: 32,
          lineHeight: 1,
          color: 'var(--accent-300, #7db4f7)',
        }}
        aria-hidden="true"
      >
        “
      </span>
      <p
        style={{
          fontSize: 'var(--text-md)',
          lineHeight: 'var(--leading-relaxed)',
          color: '#ffffff',
          margin: 0,
          textWrap: 'balance',
        }}
      >
        {quote}
      </p>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 'auto' }}>
        {avatarSrc ? (
          <img
            src={avatarSrc}
            alt={name}
            style={{ width: 44, height: 44, borderRadius: 'var(--radius-full)', objectFit: 'cover' }}
          />
        ) : (
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 'var(--radius-full)',
              background: 'rgba(255,255,255,0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: 'var(--font-display)',
              fontWeight: 700,
              fontSize: 'var(--text-sm)',
              color: '#ffffff',
            }}
          >
            {name.charAt(0)}
          </div>
        )}
        <div>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 'var(--text-sm)', color: '#ffffff' }}>{name}</div>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-on-dark-secondary)' }}>{role}</div>
        </div>
      </div>
    </div>
  );
}
