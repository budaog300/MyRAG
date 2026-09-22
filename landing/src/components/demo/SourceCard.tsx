import type { DemoSource } from '../../types/demo';
import { cn } from '../../lib/cn';
import { FileText } from 'lucide-react';

type SourceCardProps = {
  source: DemoSource;
  index: number;
  delayMs?: number;
  relevanceAriaLabel: (percent: number) => string;
};

/** Карточка найденного фрагмента с индикатором релевантности. */
export function SourceCard({ source, index, delayMs = 0, relevanceAriaLabel }: SourceCardProps) {
  const percent = Math.round(source.relevance * 100);

  return (
    <li
      className="demo-in rounded-xl border border-white/10 bg-white/[0.04] p-4"
      style={{ animationDelay: `${delayMs}ms` }}
    >
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/10 text-accent-300">
          <FileText className="h-4 w-4" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
            <p className="truncate text-[13px] font-semibold text-white">
              <span className="mr-1.5 text-accent-300">[{index + 1}]</span>
              {source.document}
            </p>
            <span className="shrink-0 rounded bg-white/10 px-1.5 py-0.5 text-[10px] font-bold tracking-wide text-slate-300">
              {source.type}
            </span>
          </div>
          <p className="mt-0.5 text-xs text-slate-400">{source.location}</p>
          <p className="mt-2 line-clamp-3 text-[13px] leading-relaxed text-slate-300/90">
            «{source.snippet}»
          </p>
          <div className="mt-3 flex items-center gap-2">
            <div
              className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/10"
              role="img"
              aria-label={relevanceAriaLabel(percent)}
            >
              <div
                className={cn(
                  'h-full rounded-full transition-[width] duration-700',
                  source.relevance >= 0.85
                    ? 'bg-accent-400'
                    : source.relevance >= 0.65
                      ? 'bg-accent-400/75'
                      : 'bg-accent-400/45',
                )}
                style={{ width: `${percent}%` }}
              />
            </div>
            <span className="w-10 text-right font-mono text-[11px] text-slate-400">{percent}%</span>
          </div>
        </div>
      </div>
    </li>
  );
}
