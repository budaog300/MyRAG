import { cn } from '../../lib/cn';
import { brand } from '../../data/navigation';
import logo from '../../assets/logo.svg';

type LogoProps = {
  variant?: 'light' | 'dark';
  className?: string;
  compact?: boolean;
};

export function Logo({
  variant = 'light',
  className,
  compact = false,
}: LogoProps) {
  const isDark = variant === 'dark';

  return (
    <span className={cn('inline-flex items-center gap-2.5', className)}>
      <img
        src={logo}
        alt=""
        aria-hidden="true"
        className="h-8 w-8 shrink-0"
      />

      <span
        className={cn(
          'text-[17px] leading-none font-bold tracking-tight',
          isDark ? 'text-white' : 'text-slate-900',
        )}
      >
        INTEVRUM

        <span
          className={cn(
            'ml-1.5 font-medium',
            isDark ? 'text-slate-400' : 'text-slate-500',
            compact && 'hidden sm:inline',
          )}
        >
          Group
        </span>
      </span>

      <span className="sr-only">{brand.logoAlt}</span>
    </span>
  );
}