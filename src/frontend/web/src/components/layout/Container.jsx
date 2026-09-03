import React from 'react';
import { cn } from '../ui';

export function Container({ as: Component = 'div', size = 'xl', className, children, ...props }) {
  const sizes = {
    md: 'max-w-4xl',
    lg: 'max-w-6xl',
    xl: 'max-w-7xl',
  };
  return (
    <Component className={cn('mx-auto w-full px-4 sm:px-6 lg:px-8', sizes[size], className)} {...props}>
      {children}
    </Component>
  );
}

export function PageShell({ children, className }) {
  return <div className={cn('min-h-[70vh] py-6 sm:py-8 lg:py-10', className)}>{children}</div>;
}
