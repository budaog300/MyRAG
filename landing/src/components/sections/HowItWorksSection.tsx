import { useState } from 'react';
import { pipelineContent, pipelineSteps } from '../../data/pipeline';
import { sectionIds } from '../../data/navigation';
import { ProcessStepCard } from '../ui/ProcessStepCard';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

export function HowItWorksSection() {
  const [activeId, setActiveId] = useState<string>(pipelineSteps[0].id);
  const activeStep = pipelineSteps.find((step) => step.id === activeId) ?? pipelineSteps[0];
  const activeIndex = pipelineSteps.indexOf(activeStep);

  return (
    <Section id={sectionIds.howItWorks} aria-labelledby="how-it-works-heading">
      <SectionHeader
        headingId="how-it-works-heading"
        eyebrow={pipelineContent.eyebrow}
        title={pipelineContent.title}
        description={pipelineContent.description}
      />

      <div className="mt-14 grid gap-6 lg:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] lg:gap-10">
        <Reveal>
          <ol className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-2 xl:grid-cols-3" aria-label={pipelineContent.title}>
            {pipelineSteps.map((step, index) => (
              <li key={step.id} className="min-w-0">
                <ProcessStepCard
                  step={step}
                  index={index}
                  active={step.id === activeId}
                  onSelect={setActiveId}
                />
              </li>
            ))}
          </ol>
        </Reveal>

        <Reveal delay={100}>
          <div
            className="sticky top-28 h-full min-w-0 rounded-2xl border border-slate-200 bg-slate-50 p-6 sm:p-8"
            aria-live="polite"
          >
            <span className="font-mono text-xs font-bold tracking-widest text-accent-600 uppercase">
              {pipelineContent.stepLabel} {activeIndex + 1} / {pipelineSteps.length}
            </span>
            <h3 className="mt-3 text-xl font-semibold text-slate-900">{activeStep.title}</h3>
            <p className="mt-3 text-sm leading-relaxed text-slate-600 sm:text-[15px]">
              {activeStep.description}
            </p>
            <div className="mt-6 flex gap-1.5" aria-hidden="true">
              {pipelineSteps.map((step) => (
                <span
                  key={step.id}
                  className={
                    pipelineSteps.indexOf(step) <= activeIndex
                      ? 'h-1 w-full rounded-full bg-accent-500'
                      : 'h-1 w-full rounded-full bg-slate-200'
                  }
                />
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </Section>
  );
}
