import React from 'react';

/**
 * @typedef {Object} BadgeProps
 * @property {'neutral'|'accent'|'success'|'warning'|'navy'} [tone]
 * @property {'dark'|'light'} [surface]
 * @property {React.ReactNode} children
 * @property {React.ReactNode} [icon]
 */
export function Badge({ tone = 'neutral', surface = 'light', children, icon }) {
  const onDark = surface === 'dark';
  const tones = {
    neutral: { bg: onDark ? 'rgba(255,255,255,0.08)' : 'var(--neutral-100)', color: onDark ? 'rgba(255,255,255,0.85)' : 'var(--text-secondary)' },
    accent: { bg: 'var(--accent-100)', color: 'var(--accent-700)' },
    success: { bg: 'var(--success-100)', color: 'var(--success-700)' },
    warning: { bg: 'var(--warning-100)', color: 'var(--warning-700)' },
    navy: { bg: 'var(--navy-100)', color: 'var(--navy-800)' },
  };
  const { bg, color } = tones[tone] || tones.neutral;

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: '6px 14px',
        borderRadius: 'var(--radius-full)',
        background: bg,
        color,
        fontFamily: 'var(--font-body)',
        fontWeight: 700,
        fontSize: 'var(--text-xs)',
      }}
    >
      {icon}
      {children}
    </span>
  );
}
