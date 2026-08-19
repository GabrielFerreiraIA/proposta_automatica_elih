function Button({ variant = 'primary', surface = 'light', size = 'md', withArrow = true, children, onClick, type = 'button' }) {
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
  return React.createElement(
    'button',
    {
      type,
      onClick,
      onMouseEnter: () => setHover(true),
      onMouseLeave: () => setHover(false),
      style: {
        display: 'inline-flex', alignItems: 'center', gap: 8, padding: pad,
        fontFamily: 'var(--font-display)', fontSize, fontWeight: 600, border,
        borderRadius: 'var(--radius-full)', background: hover ? hoverBg : bg,
        color: hover ? hoverColor : color, cursor: 'pointer',
        transition: 'all var(--duration-base) var(--ease-out)',
        boxShadow: isPrimary && !onDark ? (hover ? 'var(--shadow-md)' : 'var(--shadow-sm)') : 'none',
      },
    },
    children,
    withArrow && React.createElement(
      'span',
      { style: { display: 'inline-block', transform: hover ? 'translate(2px,-2px)' : 'translate(0,0)', transition: 'transform var(--duration-base) var(--ease-out)' } },
      '↗'
    )
  );
}

function Badge({ tone = 'neutral', surface = 'light', children, icon }) {
  const onDark = surface === 'dark';
  const tones = {
    neutral: { bg: onDark ? 'rgba(255,255,255,0.08)' : 'var(--neutral-100)', color: onDark ? 'rgba(255,255,255,0.85)' : 'var(--text-secondary)' },
    accent: { bg: 'var(--accent-100)', color: 'var(--accent-700)' },
    success: { bg: 'var(--success-100)', color: 'var(--success-700)' },
    warning: { bg: 'var(--warning-100)', color: 'var(--warning-700)' },
    navy: { bg: 'var(--navy-100)', color: 'var(--navy-800)' },
  };
  const { bg, color } = tones[tone] || tones.neutral;
  return React.createElement(
    'span',
    { style: { display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 'var(--radius-full)', background: bg, color, fontFamily: 'var(--font-body)', fontWeight: 700, fontSize: 'var(--text-xs)' } },
    icon,
    children
  );
}

function SectionHeader({ overline, title, description, surface = 'light', align = 'left', action }) {
  const onDark = surface === 'dark';
  return React.createElement(
    'div',
    { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', gap: 24, textAlign: align, flexWrap: 'wrap' } },
    React.createElement(
      'div',
      { style: { maxWidth: 640 } },
      React.createElement('div', { className: onDark ? 'overline overline--on-dark' : 'overline' }, overline),
      React.createElement(
        'h2',
        {
          style: {
            fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 'var(--text-2xl)',
            letterSpacing: 'var(--tracking-tight)', lineHeight: 'var(--leading-tight)',
            color: onDark ? '#ffffff' : 'var(--text-primary)', margin: '8px 0 0 0', textWrap: 'balance',
          },
        },
        title
      ),
      description && React.createElement(
        'p',
        {
          style: {
            fontFamily: 'var(--font-body)', fontSize: 'var(--text-md)', lineHeight: 'var(--leading-relaxed)',
            color: onDark ? 'var(--text-on-dark-secondary)' : 'var(--text-secondary)', margin: '10px 0 0 0',
          },
        },
        description
      )
    ),
    action && React.createElement('div', null, action)
  );
}

function PlanCard({ category, tag, title, description, features = [], priceLabel = 'a partir de', price, priceNote, onDetails }) {
  const [hover, setHover] = React.useState(false);
  return React.createElement(
    'div',
    {
      onMouseEnter: () => setHover(true),
      onMouseLeave: () => setHover(false),
      style: {
        background: '#ffffff', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-xl)',
        padding: 28, display: 'flex', flexDirection: 'column', gap: 16,
        boxShadow: hover ? 'var(--shadow-md)' : 'var(--shadow-sm)',
        transform: hover ? 'translateY(-2px)' : 'translateY(0)',
        transition: 'all var(--duration-base) var(--ease-out)', fontFamily: 'var(--font-body)', minWidth: 280,
      },
    },
    React.createElement(
      'div',
      { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } },
      React.createElement('span', { style: { fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em' } }, category),
      tag && React.createElement('span', { style: { fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--accent-700)', background: 'var(--accent-100)', padding: '4px 10px', borderRadius: 'var(--radius-full)' } }, tag)
    ),
    React.createElement(
      'div',
      null,
      React.createElement('h3', { style: { fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 'var(--text-lg)', color: 'var(--text-primary)', margin: '0 0 6px 0' } }, title),
      React.createElement('p', { style: { fontSize: 'var(--text-sm)', color: 'var(--text-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 } }, description)
    ),
    React.createElement(
      'ul',
      { style: { listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 8 } },
      features.map((f, i) => React.createElement(
        'li',
        { key: i, style: { display: 'flex', gap: 8, fontSize: 'var(--text-sm)', color: 'var(--text-primary)' } },
        React.createElement('span', { style: { color: 'var(--success-500)', fontWeight: 700 } }, '✓'),
        f
      ))
    ),
    React.createElement(
      'div',
      { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', paddingTop: 8, borderTop: '1px solid var(--border-subtle)' } },
      React.createElement(
        'div',
        null,
        React.createElement('div', { style: { fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' } }, priceLabel),
        React.createElement('div', { style: { fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 'var(--text-lg)', color: 'var(--navy-900)' } }, price),
        priceNote && React.createElement('div', { style: { fontSize: 'var(--text-xs)', color: 'var(--text-tertiary)' } }, priceNote)
      ),
      React.createElement(
        'button',
        {
          onClick: onDetails,
          style: { background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 'var(--text-sm)', color: 'var(--navy-900)', display: 'flex', alignItems: 'center', gap: 4 },
        },
        'Saiba mais ↗'
      )
    )
  );
}

function Navbar({ logo, links = [], cta }) {
  return React.createElement(
    'nav',
    { style: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 24, padding: '14px 28px', background: '#ffffff', borderRadius: 'var(--radius-full)', boxShadow: 'var(--shadow-sm)', border: '1px solid var(--border-subtle)', fontFamily: 'var(--font-body)' } },
    React.createElement('div', { style: { display: 'flex', alignItems: 'center' } }, logo),
    React.createElement(
      'div',
      { style: { display: 'flex', alignItems: 'center', gap: 28 } },
      links.map((l, i) => React.createElement('a', { key: i, href: l.href || '#', style: { fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--text-secondary)', textDecoration: 'none' } }, l.label))
    ),
    React.createElement('div', null, cta)
  );
}

function Input({ label, placeholder, value, onChange, type = 'text', error }) {
  const [focus, setFocus] = React.useState(false);
  return React.createElement(
    'label',
    { style: { display: 'flex', flexDirection: 'column', gap: 6, fontFamily: 'var(--font-body)' } },
    label && React.createElement('span', { style: { fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--text-primary)' } }, label),
    React.createElement('input', {
      type, value, placeholder,
      onChange: (e) => onChange && onChange(e.target.value),
      onFocus: () => setFocus(true),
      onBlur: () => setFocus(false),
      style: {
        fontFamily: 'var(--font-body)', fontSize: 'var(--text-base)', padding: '12px 16px',
        borderRadius: 'var(--radius-md)',
        border: error ? '1.5px solid var(--danger-500)' : focus ? '1.5px solid var(--accent-500)' : '1.5px solid var(--border-default)',
        boxShadow: focus ? 'var(--shadow-focus)' : 'none', outline: 'none', color: 'var(--text-primary)',
        background: '#ffffff', transition: 'border-color var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out)',
      },
    }),
    error && React.createElement('span', { style: { fontSize: 'var(--text-xs)', color: 'var(--danger-500)' } }, error)
  );
}

function DarkSection({ children, tone = '900', curveTop = false }) {
  const bg = tone === '950' ? 'var(--navy-950)' : 'var(--navy-900)';
  return React.createElement(
    'section',
    { style: { position: 'relative', background: bg, padding: '96px 0', overflow: 'hidden' } },
    curveTop && React.createElement(
      'svg',
      { viewBox: '0 0 100 6', preserveAspectRatio: 'none', style: { position: 'absolute', top: -1, left: 0, width: '100%', height: 48, display: 'block' } },
      React.createElement('path', { d: 'M0,6 Q50,0 100,6 L100,0 L0,0 Z', fill: '#ffffff' })
    ),
    React.createElement('div', { style: { maxWidth: 'var(--max-width)', margin: '0 auto', padding: '0 32px', position: 'relative' } }, children)
  );
}

function DarkStatCard({ value, label, description }) {
  return React.createElement(
    'div',
    { style: { flex: 1, minWidth: 220, background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-on-dark)', borderRadius: 'var(--radius-lg)', padding: 24, display: 'flex', flexDirection: 'column', gap: 10, fontFamily: 'var(--font-body)' } },
    React.createElement('div', { style: { fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 'var(--text-2xl)', color: '#ffffff', letterSpacing: 'var(--tracking-tight)' } }, value),
    React.createElement('div', { style: { fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 'var(--text-xs)', textTransform: 'uppercase', letterSpacing: 'var(--tracking-overline)', color: 'var(--accent-300, #7db4f7)' } }, label),
    description && React.createElement('p', { style: { fontSize: 'var(--text-sm)', lineHeight: 'var(--leading-relaxed)', color: 'var(--text-on-dark-secondary)', margin: 0 } }, description)
  );
}

function DarkChecklistItem({ children }) {
  return React.createElement(
    'div',
    { style: { display: 'flex', alignItems: 'center', gap: 12, fontFamily: 'var(--font-body)' } },
    React.createElement('span', { style: { width: 26, height: 26, flexShrink: 0, borderRadius: 'var(--radius-full)', background: 'rgba(255,255,255,0.08)', border: '1px solid var(--border-on-dark-strong)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-300, #7db4f7)', fontSize: 13, fontWeight: 700 } }, '✓'),
    React.createElement('span', { style: { fontSize: 'var(--text-base)', color: '#ffffff' } }, children)
  );
}

function DarkCTACard({ badge, title, description, action }) {
  return React.createElement(
    'div',
    { style: { background: 'var(--navy-950)', borderRadius: 'var(--radius-2xl)', padding: 40, display: 'flex', flexDirection: 'column', gap: 18, fontFamily: 'var(--font-body)', boxShadow: 'var(--shadow-dark-lg)' } },
    badge && React.createElement('span', { style: { alignSelf: 'flex-start', background: 'rgba(255,255,255,0.08)', color: 'var(--accent-300, #7db4f7)', fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 'var(--text-xs)', letterSpacing: 'var(--tracking-overline)', textTransform: 'uppercase', padding: '6px 14px', borderRadius: 'var(--radius-full)' } }, badge),
    React.createElement('h3', { style: { fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 'var(--text-xl)', color: '#ffffff', letterSpacing: 'var(--tracking-tight)', lineHeight: 'var(--leading-snug)', margin: 0, textWrap: 'balance' } }, title),
    description && React.createElement('p', { style: { fontSize: 'var(--text-base)', color: 'var(--text-on-dark-secondary)', lineHeight: 'var(--leading-relaxed)', margin: 0 } }, description),
    action && React.createElement('div', { style: { marginTop: 8 } }, action)
  );
}

function DarkTestimonial({ quote, name, role, avatarSrc }) {
  return React.createElement(
    'div',
    { style: { background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-on-dark)', borderRadius: 'var(--radius-xl)', padding: 32, display: 'flex', flexDirection: 'column', gap: 20, fontFamily: 'var(--font-body)', minWidth: 280, flex: 1 } },
    React.createElement('span', { style: { fontFamily: 'var(--font-display)', fontSize: 32, lineHeight: 1, color: 'var(--accent-300, #7db4f7)' }, 'aria-hidden': 'true' }, '\u201C'),
    React.createElement('p', { style: { fontSize: 'var(--text-md)', lineHeight: 'var(--leading-relaxed)', color: '#ffffff', margin: 0, textWrap: 'balance' } }, quote),
    React.createElement(
      'div',
      { style: { display: 'flex', alignItems: 'center', gap: 12, marginTop: 'auto' } },
      avatarSrc
        ? React.createElement('img', { src: avatarSrc, alt: name, style: { width: 44, height: 44, borderRadius: 'var(--radius-full)', objectFit: 'cover' } })
        : React.createElement('div', { style: { width: 44, height: 44, borderRadius: 'var(--radius-full)', background: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 'var(--text-sm)', color: '#ffffff' } }, name.charAt(0)),
      React.createElement(
        'div',
        null,
        React.createElement('div', { style: { fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 'var(--text-sm)', color: '#ffffff' } }, name),
        React.createElement('div', { style: { fontSize: 'var(--text-xs)', color: 'var(--text-on-dark-secondary)' } }, role)
      )
    )
  );
}

function PartnerLogoStrip({ logos = [] }) {
  return React.createElement(
    'div',
    { style: { display: 'flex', gap: 16, flexWrap: 'wrap', justifyContent: 'center' } },
    logos.map((l, i) => React.createElement(
      'div',
      { key: i, style: { background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-on-dark)', borderRadius: 'var(--radius-md)', padding: '14px 22px', display: 'flex', alignItems: 'center', justifyContent: 'center', minWidth: 120, height: 56 } },
      React.createElement('img', { src: l.src, alt: l.alt, style: { maxHeight: 22, maxWidth: 110, filter: 'grayscale(1) brightness(4)', opacity: 0.75 } })
    ))
  );
}

window.ElihSeguros = {
  Button, Badge, SectionHeader, PlanCard, Navbar, Input,
  DarkSection, DarkStatCard, DarkChecklistItem, DarkCTACard, DarkTestimonial, PartnerLogoStrip,
};
