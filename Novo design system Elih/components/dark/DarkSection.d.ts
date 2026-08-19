import React from 'react';

export interface DarkSectionProps {
  children: React.ReactNode;
  /** which navy to use as background */
  tone?: '900' | '950';
  /** render a soft concave white curve overlapping the top edge */
  curveTop?: boolean;
}

export function DarkSection(props: DarkSectionProps): JSX.Element;
