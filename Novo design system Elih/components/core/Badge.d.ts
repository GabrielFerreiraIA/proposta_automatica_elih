import React from 'react';

export interface BadgeProps {
  tone?: 'neutral' | 'accent' | 'success' | 'warning' | 'navy';
  surface?: 'dark' | 'light';
  children: React.ReactNode;
  icon?: React.ReactNode;
}

export function Badge(props: BadgeProps): JSX.Element;
