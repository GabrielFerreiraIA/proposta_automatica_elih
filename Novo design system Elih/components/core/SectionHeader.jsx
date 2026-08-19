import React from 'react';

/**
 * @typedef {Object} SectionHeaderProps
 * @property {string} overline
 * @property {React.ReactNode} title
 * @property {React.ReactNode} [description]
 * @property {'dark'|'light'} [surface]
 * @property {'left'|'center'} [align]
 * @property {React.ReactNode} [action] - e.g. a pair of nav arrows or a filter button, right-aligned
 */
export function SectionHeader({ overline, title, description, surface = 'light', align = 'left', action }) {
  const onDark = surface === 'dark';
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-end',
        gap: 24,
        textAlign: align,
        flexWrap: 'wrap',
      }}
    >
      <div style={{ maxWidth: 640 }}>
        <div className={onDark ? 'overline overline--on-dark' : 'overline'}>{overline}</div>
        <h2
          style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 700,
            fontSize: 'var(--text-2xl)',
            letterSpacing: 'var(--tracking-tight)',
            lineHeight: 'var(--leading-tight)',
            color: onDark ? '#ffffff' : 'var(--text-primary)',
            margin: '8px 0 0 0',
            textWrap: 'balance',
          }}
        >
          {title}
        </h2>
        {description && (
          <p
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: 'var(--text-md)',
              lineHeight: 'var(--leading-relaxed)',
              color: onDark ? 'var(--text-on-dark-secondary)' : 'var(--text-secondary)',
              margin: '10px 0 0 0',
            }}
          >
            {description}
          </p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
