import React from 'react';

export interface DarkTestimonialProps {
  quote: string;
  name: string;
  /** e.g. "RH, Empresa XPTO" or "Associada SEESP" */
  role: string;
  avatarSrc?: string;
}

export function DarkTestimonial(props: DarkTestimonialProps): JSX.Element;
