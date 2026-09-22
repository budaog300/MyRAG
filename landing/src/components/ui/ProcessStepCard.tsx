import { cn } from '../../lib/cn';
import type { ProcessStep } from '../../types/content';

type ProcessStepCardProps = {
  step: ProcessStep;
  index: number;
  active: boolean;
  onSelect: (id: string) => void;
  orientation?: 'horizontal' | 'vertical';
};

/** Универсальный элемент pipeline-шага: клик/hover активирует пояснение. */
export function ProcessStepCard({
  step,
  index,
  active,
  onSelect,
  orientation = 'horizontal',
}: ProcessStepCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(step.id)}
      onMouseEnter={() => onSelect(step.id)}
      aria-pressed={active}
      className={cn(
        'group relative flex w-full items-center gap-3 rounded-xl border px-3.5 py-3 text-left transition-all duration-200',
        orientation === 'vertical' && 'flex-col items-stretch gap-0',
        active
          ? 'border-accent-500/60 bg-accent-50 shadow-sm'
          : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50',
      )}
    >
      <span
        className={cn(
          'flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold transition-colors duration-200',
          active ? 'bg-accent-600 text-white' : 'bg-slate-100 text-slate-500 group-hover:bg-slate-200',
        )}
      >
        {index + 1}
      </span>
      <span className="text-sm leading-tight font-semibold text-slate-800">{step.title}</span>
    </button>
  );
}
