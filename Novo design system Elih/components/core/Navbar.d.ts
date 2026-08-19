import React from 'react';

export interface NavLink {
  label: string;
  href?: string;
}

export interface NavbarProps {
  logo: React.ReactNode;
  links?: NavLink[];
  /** usually a primary Button */
  cta?: React.ReactNode;
}

export function Navbar(props: NavbarProps): JSX.Element;
