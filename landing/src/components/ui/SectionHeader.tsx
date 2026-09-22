import { cn } from '../../lib/cn';
import { Reveal } from './Reveal';

type SectionHeaderProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: 'left' | 'center';
  tone?: 'light' | 'dark';
  headingId?: string;
  /** h2 — по умолчанию; на странице ровно один h1 (в Hero). */
  as?: 'h2' | 'h3';
  className?: string;
};

export function SectionHeader({
  eyebrow,
  title,
  description,
  align = 'center',
  tone = 'light',
  headingId,
  as: Heading = 'h2',
  className,
}: SectionHeaderProps) {
  return (
    <Reveal
      className={cn(
        'max-w-3xl',
        align === 'center' ? 'mx-auto text-center' : 'text-left',
        className,
      )}
    >
      {eyebrow ? (
        <p
          className={cn(
            'text-xs font-semibold tracking-[0.2em] uppercase',
            tone === 'dark' ? 'text-accent-300' : 'text-accent-600',
          )}
        >
          {eyebrow}
        </p>
      ) : null}
      <Heading
        id={headingId}
        className={cn(
          'mt-3 text-balance text-3xl font-bold tracking-tight sm:text-4xl',
          tone === 'dark' ? 'text-white' : 'text-slate-900',
        )}
      >
        {title}
      </Heading>
      {description ? (
        <p
          className={cn(
            'mt-4 text-base leading-relaxed sm:text-lg',
            tone === 'dark' ? 'text-slate-400' : 'text-slate-500',
          )}
        >
          {description}
        </p>
      ) : null}
    </Reveal>
  );
}
