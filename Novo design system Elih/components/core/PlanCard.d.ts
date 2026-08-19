import React from 'react';

export interface PlanCardProps {
  category: string;
  tag?: string;
  title: string;
  description: string;
  features?: string[];
  priceLabel?: string;
  price: string;
  priceNote?: string;
  onDetails?: () => void;
}

export function PlanCard(props: PlanCardProps): JSX.Element;
