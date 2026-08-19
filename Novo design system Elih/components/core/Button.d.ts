import React from 'react';

export interface ButtonProps {
  /** visual weight of the button */
  variant?: 'primary' | 'secondary' | 'ghost';
  /** background it will sit on — flips the color scheme */
  surface?: 'dark' | 'light';
  size?: 'sm' | 'md';
  /** show the trailing ↗ arrow (default true, matches brand CTA style) */
  withArrow?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit';
}

export function Button(props: ButtonProps): JSX.Element;
