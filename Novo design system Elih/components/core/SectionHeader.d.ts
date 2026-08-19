import React from 'react';

export interface SectionHeaderProps {
  overline: string;
  title: React.ReactNode;
  description?: React.ReactNode;
  surface?: 'dark' | 'light';
  align?: 'left' | 'center';
  /** trailing control, e.g. carousel arrows or a filter button */
  action?: React.ReactNode;
}

export function SectionHeader(props: SectionHeaderProps): JSX.Element;
