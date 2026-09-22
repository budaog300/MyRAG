import type { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/cn';

type ArchitectureNodeProps = {
  icon: LucideIcon;
  title: string;
  short: string;
  active: boolean;
  onClick: () => void;
};

export function ArchitectureNode({ icon: Icon, title, active, onClick }: ArchitectureNodeProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      onMouseEnter={onClick}
      aria-pressed={active}
      className={cn(
        'flex w-full flex-col items-center gap-2 rounded-xl border px-3 py-4 text-center transition-all duration-200',
        active
          ? 'border-accent-400/60 bg-accent-400/10 shadow-[0_0_0_1px_rgba(62,195,168,0.25)]'
          : 'border-white/10 bg-white/[0.03] hover:border-white/25 hover:bg-white/[0.06]',
      )}
    >
      <span
        className={cn(
          'flex h-10 w-10 items-center justify-center rounded-lg transition-colors duration-200',
          active ? 'bg-accent-400 text-ink-950' : 'bg-white/10 text-accent-300',
        )}
      >
        <Icon className="h-5 w-5" aria-hidden="true" />
      </span>
      <span className="text-[13px] leading-tight font-semibold text-white">{title}</span>
    </button>
  );
}
