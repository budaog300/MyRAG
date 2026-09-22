import type { MouseEvent, ReactNode } from 'react';
import { cn } from '../../lib/cn';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'dark';
type ButtonSize = 'md' | 'lg';

type BaseProps = {
  children: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  className?: string;
};

type ButtonAsButton = BaseProps & {
  href?: undefined;
  type?: 'button' | 'submit';
  disabled?: boolean;
  onClick?: (event: MouseEvent<HTMLButtonElement>) => void;
  'aria-busy'?: boolean;
};

type ButtonAsLink = BaseProps & {
  href: string;
  'aria-label'?: string;
};

const base =
  'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-all duration-200 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-60';

const variants: Record<ButtonVariant, string> = {
  primary:
    'bg-accent-600 text-white shadow-sm hover:bg-accent-700 hover:shadow-md active:scale-[0.99]',
  secondary:
    'border border-slate-200 bg-white text-slate-800 hover:border-slate-300 hover:bg-slate-50',
  ghost: 'text-slate-700 hover:bg-slate-100',
  dark: 'bg-white text-ink-950 shadow-sm hover:bg-accent-50 hover:shadow-md active:scale-[0.99]',
};

const sizes: Record<ButtonSize, string> = {
  md: 'px-4 py-2.5 text-sm sm:px-5',
  lg: 'px-5 py-3 text-sm sm:text-base sm:px-6',
};

export function Button(props: ButtonAsButton | ButtonAsLink) {
  const { children, variant = 'primary', size = 'md', className } = props;
  const classes = cn(base, variants[variant], sizes[size], className);

  if ('href' in props && props.href !== undefined) {
    return (
      <a href={props.href} className={classes} aria-label={props['aria-label']}>
        {children}
      </a>
    );
  }

  return (
    <button
      type={props.type ?? 'button'}
      className={classes}
      disabled={props.disabled}
      onClick={props.onClick}
      aria-busy={props['aria-busy']}
    >
      {children}
    </button>
  );
}
