import { pilotContent, pilotSteps } from '../../data/pilot';
import { sectionIds } from '../../data/navigation';
import { Button } from '../ui/Button';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

export function PilotSection() {
  return (
    <Section
      id={sectionIds.pilot}
      tone="muted"
      aria-labelledby="pilot-heading"
      className="border-y border-slate-200/70"
    >
      <SectionHeader
        headingId="pilot-heading"
        eyebrow={pilotContent.eyebrow}
        title={pilotContent.title}
        description={pilotContent.description}
      />

      <ol className="mt-14 grid gap-4 md:grid-cols-5 md:gap-3">
        {pilotSteps.map((step, index) => (
          <li key={step.id}>
            <Reveal delay={index * 80} className="h-full">
              <div className="relative flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-5">
                <div className="flex items-center gap-3">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ink-950 text-xs font-bold text-accent-300">
                    {index + 1}
                  </span>
                  <span
                    aria-hidden="true"
                    className={
                      index < pilotSteps.length - 1
                        ? 'hidden h-px flex-1 bg-slate-200 md:block'
                        : 'hidden md:block md:flex-1'
                    }
                  />
                </div>
                <h3 className="mt-4 text-[15px] leading-snug font-semibold text-slate-900">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-500">{step.description}</p>
              </div>
            </Reveal>
          </li>
        ))}
      </ol>

      <Reveal className="mt-10 flex justify-center">
        <Button href={pilotContent.cta.href} variant="secondary" size="lg">
          {pilotContent.cta.label}
        </Button>
      </Reveal>
    </Section>
  );
}
