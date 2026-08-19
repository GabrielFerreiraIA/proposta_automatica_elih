import React from 'react';

/**
 * @typedef {Object} InputProps
 * @property {string} [label]
 * @property {string} [placeholder]
 * @property {string} [value]
 * @property {(v: string) => void} [onChange]
 * @property {'text'|'email'|'tel'} [type]
 * @property {string} [error]
 */
export function Input({ label, placeholder, value, onChange, type = 'text', error }) {
  const [focus, setFocus] = React.useState(false);
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontFamily: 'var(--font-body)' }}>
      {label && (
        <span style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--text-primary)' }}>{label}</span>
      )}
      <input
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange && onChange(e.target.value)}
        onFocus={() => setFocus(true)}
        onBlur={() => setFocus(false)}
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: 'var(--text-base)',
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          border: error ? '1.5px solid var(--danger-500)' : focus ? '1.5px solid var(--accent-500)' : '1.5px solid var(--border-default)',
          boxShadow: focus ? 'var(--shadow-focus)' : 'none',
          outline: 'none',
          color: 'var(--text-primary)',
          background: '#ffffff',
          transition: 'border-color var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out)',
        }}
      />
      {error && <span style={{ fontSize: 'var(--text-xs)', color: 'var(--danger-500)' }}>{error}</span>}
    </label>
  );
}
