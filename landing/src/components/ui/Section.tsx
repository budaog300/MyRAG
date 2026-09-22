import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../lib/cn';
import { Container } from './Container';

type SectionTone = 'light' | 'muted' | 'dark';

type SectionProps = {
  id?: string;
  tone?: SectionTone;
  className?: string;
  containerClassName?: string;
  'aria-labelledby'?: string;
  children: ReactNode;
};

const toneClasses: Record<SectionTone, string> = {
  light: 'bg-white text-slate-600',
  muted: 'bg-slate-50 text-slate-600',
  dark: 'bg-ink-950 text-slate-300',
};

type SectionElementProps = Omit<
  HTMLAttributes<HTMLElement>,
  'id' | 'className' | 'children'
>;

export function Section({
  id,
  tone = 'light',
  className,
  containerClassName,
  children,
  ...rest
}: SectionProps & SectionElementProps) {
  return (
    <section
      id={id}
      className={cn('py-20 sm:py-24 lg:py-28', toneClasses[tone], className)}
      {...rest}
    >
      <Container className={containerClassName}>{children}</Container>
    </section>
  );
}
