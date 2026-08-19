import React from 'react';

export interface InputProps {
  label?: string;
  placeholder?: string;
  value?: string;
  onChange?: (v: string) => void;
  type?: 'text' | 'email' | 'tel';
  error?: string;
}

export function Input(props: InputProps): JSX.Element;
