import React from 'react';

export interface DarkCTACardProps {
  badge?: string;
  title: React.ReactNode;
  description?: string;
  action?: React.ReactNode;
}

export function DarkCTACard(props: DarkCTACardProps): JSX.Element;
