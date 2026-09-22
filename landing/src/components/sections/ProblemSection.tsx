import { Check, X } from 'lucide-react';
import { problemContent } from '../../data/landing';
import { cn } from '../../lib/cn';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

function ComparisonPanel({
  title,
  badge,
  items,
  positive,
}: {
  title: string;
  badge: string;
  items: readonly string[];
  positive: boolean;
}) {
  return (
    <div
      className={cn(
        'flex h-full flex-col rounded-2xl border p-6 sm:p-7',
        positive ? 'border-accent-200 bg-accent-50/50' : 'border-slate-200 bg-white',
      )}
    >
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-base font-semibold text-slate-900">{title}</h3>
        <span
          className={cn(
            'rounded-full px-2.5 py-1 text-[11px] font-bold tracking-wide uppercase',
            positive ? 'bg-accent-600 text-white' : 'bg-slate-100 text-slate-500',
          )}
        >
          {badge}
        </span>
      </div>
      <ul className="mt-5 space-y-3.5">
        {items.map((item) => (
          <li key={item} className="flex items-start gap-3 text-sm leading-relaxed">
            <span
              className={cn(
                'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full',
                positive ? 'bg-accent-100 text-accent-700' : 'bg-slate-100 text-slate-400',
              )}
              aria-hidden="true"
            >
              {positive ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
            </span>
            <span className={positive ? 'text-slate-700' : 'text-slate-500'}>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ProblemSection() {
  const { comparison } = problemContent;

  return (
    <Section
      tone="muted"
      aria-labelledby="problem-heading"
      className="border-y border-slate-200/70"
    >
      <SectionHeader
        headingId="problem-heading"
        eyebrow={problemContent.eyebrow}
        title={problemContent.title}
        description={problemContent.description}
      />

      <div className="mt-14 grid gap-x-10 gap-y-8 sm:grid-cols-2">
        {problemContent.pains.map((pain, index) => (
          <Reveal
            key={pain.title}
            delay={index * 80}
            className="flex gap-4 border-l border-slate-300/70 pl-5"
          >
            <div>
              <h3 className="text-[15px] font-semibold text-slate-900">{pain.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-500">{pain.description}</p>
            </div>
          </Reveal>
        ))}
      </div>

      <Reveal className="mt-14 grid gap-5 lg:grid-cols-2 lg:gap-6">
        <ComparisonPanel
          title={comparison.beforeTitle}
          badge={comparison.beforeLabel}
          items={comparison.beforeItems}
          positive={false}
        />
        <ComparisonPanel
          title={comparison.afterTitle}
          badge={comparison.afterLabel}
          items={comparison.afterItems}
          positive
        />
      </Reveal>
    </Section>
  );
}
