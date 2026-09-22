import type { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/cn';

type FeatureCardProps = {
  icon: LucideIcon;
  title: string;
  description: string;
  tone?: 'light' | 'dark';
  className?: string;
};

/** Универсальная карточка «иконка + заголовок + описание». */
export function FeatureCard({ icon: Icon, title, description, tone = 'light', className }: FeatureCardProps) {
  return (
    <div
      className={cn(
        'group rounded-2xl border p-6 transition-all duration-300 hover:-translate-y-0.5 sm:p-7',
        tone === 'light'
          ? 'border-slate-200 bg-white hover:border-accent-200 hover:shadow-lg hover:shadow-slate-900/[0.06]'
          : 'border-white/10 bg-white/[0.04] hover:border-accent-400/40 hover:bg-white/[0.07]',
        className,
      )}
    >
      <span
        className={cn(
          'inline-flex h-11 w-11 items-center justify-center rounded-xl transition-colors duration-300',
          tone === 'light'
            ? 'bg-accent-50 text-accent-600 group-hover:bg-accent-600 group-hover:text-white'
            : 'bg-accent-400/10 text-accent-300 group-hover:bg-accent-400 group-hover:text-ink-950',
        )}
      >
        <Icon className="h-5 w-5" aria-hidden="true" />
      </span>
      <h3
        className={cn(
          'mt-5 text-base font-semibold sm:text-lg',
          tone === 'light' ? 'text-slate-900' : 'text-white',
        )}
      >
        {title}
      </h3>
      <p className={cn('mt-2 text-sm leading-relaxed', tone === 'light' ? 'text-slate-500' : 'text-slate-400')}>
        {description}
      </p>
    </div>
  );
}
