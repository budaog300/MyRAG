import { ArrowRight } from 'lucide-react';
import { solutionContent } from '../../data/landing';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

export function SolutionSection() {
  return (
    <Section aria-labelledby="solution-heading">
      <SectionHeader
        headingId="solution-heading"
        eyebrow={solutionContent.eyebrow}
        title={solutionContent.title}
        description={solutionContent.description}
      />

      <Reveal className="mt-12">
        <ul
          aria-label={solutionContent.title}
          className="flex flex-wrap items-center justify-center gap-x-2 gap-y-3 sm:gap-x-3"
        >
          {solutionContent.steps.map((step, index) => (
            <li key={step} className="flex items-center gap-2 sm:gap-3">
              <span
                className={
                  index === solutionContent.steps.length - 1
                    ? 'rounded-lg bg-accent-600 px-4 py-2.5 text-sm font-semibold whitespace-nowrap text-white shadow-sm'
                    : 'rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold whitespace-nowrap text-slate-700 shadow-sm'
                }
              >
                {step}
              </span>
              {index < solutionContent.steps.length - 1 ? (
                <ArrowRight className="h-4 w-4 shrink-0 text-slate-300" aria-hidden="true" />
              ) : null}
            </li>
          ))}
        </ul>
      </Reveal>

      <div className="mt-14 grid gap-6 md:grid-cols-3">
        {solutionContent.points.map((point, index) => (
          <Reveal key={point.title} delay={index * 90}>
            <article className="rounded-2xl bg-slate-50 p-6 ring-1 ring-slate-200/70 sm:p-7">
              <span
                aria-hidden="true"
                className="font-mono text-sm font-bold text-accent-600"
              >
                {`0${index + 1}`}
              </span>
              <h3 className="mt-3 text-base font-semibold text-slate-900">{point.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-500">{point.description}</p>
            </article>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
