import React from 'react';

/**
 * @typedef {Object} ButtonProps
 * @property {'primary'|'secondary'|'ghost'} [variant] - visual style
 * @property {'dark'|'light'} [surface] - which background it sits on (flips colors)
 * @property {'sm'|'md'} [size]
 * @property {boolean} [withArrow] - append the trademark ↗ arrow
 * @property {React.ReactNode} children
 * @property {() => void} [onClick]
 */
export function Button({ variant = 'primary', surface = 'light', size = 'md', withArrow = true, children, onClick, type = 'button' }) {
  const isPrimary = variant === 'primary';
  const isGhost = variant === 'ghost';
  const onDark = surface === 'dark';

  const pad = size === 'sm' ? '10px 18px' : '14px 26px';
  const fontSize = size === 'sm' ? 'var(--text-sm)' : 'var(--text-base)';

  let bg, color, border, hoverBg, hoverColor;

  if (isPrimary) {
    bg = onDark ? '#ffffff' : 'var(--navy-900)';
    color = onDark ? 'var(--navy-900)' : '#ffffff';
    border = 'none';
    hoverBg = onDark ? 'var(--navy-100)' : 'var(--navy-950)';
    hoverColor = color;
  } else if (isGhost) {
    bg = 'transparent';
    color = onDark ? '#ffffff' : 'var(--navy-900)';
    border = 'none';
    hoverBg = onDark ? 'rgba(255,255,255,0.08)' : 'var(--navy-50)';
    hoverColor = color;
  } else {
    bg = 'transparent';
    color = onDark ? 'rgba(255,255,255,0.9)' : 'var(--navy-800)';
    border = onDark ? '1.5px solid rgba(255,255,255,0.28)' : '1.5px solid var(--border-strong)';
    hoverBg = onDark ? 'rgba(255,255,255,0.06)' : 'var(--navy-50)';
    hoverColor = color;
  }

  const [hover, setHover] = React.useState(false);

  return (
    <button
      type={type}
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        padding: pad,
        fontFamily: 'var(--font-display)',
        fontSize,
        fontWeight: 600,
        border,
        borderRadius: 'var(--radius-full)',
        background: hover ? hoverBg : bg,
        color: hover ? hoverColor : color,
        cursor: 'pointer',
        transition: `all var(--duration-base) var(--ease-out)`,
        boxShadow: isPrimary && !onDark ? (hover ? 'var(--shadow-md)' : 'var(--shadow-sm)') : 'none',
      }}
    >
      {children}
      {withArrow && (
        <span
          style={{
            display: 'inline-block',
            transform: hover ? 'translate(2px,-2px)' : 'translate(0,0)',
            transition: `transform var(--duration-base) var(--ease-out)`,
          }}
        >
          ↗
        </span>
      )}
    </button>
  );
}
