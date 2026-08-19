import React from 'react';

/**
 * @typedef {Object} DarkChecklistItemProps
 * @property {React.ReactNode} children
 */
export function DarkChecklistItem({ children }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontFamily: 'var(--font-body)' }}>
      <span
        style={{
          width: 26,
          height: 26,
          flexShrink: 0,
          borderRadius: 'var(--radius-full)',
          background: 'rgba(255,255,255,0.08)',
          border: '1px solid var(--border-on-dark-strong)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--accent-300, #7db4f7)',
          fontSize: 13,
          fontWeight: 700,
        }}
      >
        ✓
      </span>
      <span style={{ fontSize: 'var(--text-base)', color: '#ffffff' }}>{children}</span>
    </div>
  );
}
