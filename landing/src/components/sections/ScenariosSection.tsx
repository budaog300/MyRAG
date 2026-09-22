import { scenarios, scenariosContent } from '../../data/scenarios';
import { sectionIds } from '../../data/navigation';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

export function ScenariosSection() {
  return (
    <Section
      id={sectionIds.scenarios}
      tone="muted"
      aria-labelledby="scenarios-heading"
      className="border-y border-slate-200/70"
    >
      <SectionHeader
        headingId="scenarios-heading"
        eyebrow={scenariosContent.eyebrow}
        title={scenariosContent.title}
        description={scenariosContent.description}
      />

      <ul className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {scenarios.map((scenario, index) => (
          <li key={scenario.id} className="min-w-0">
            <Reveal delay={(index % 3) * 70} className="h-full">
              <article className="group flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-6 transition-all duration-300 hover:-translate-y-0.5 hover:border-accent-200 hover:shadow-lg hover:shadow-slate-900/[0.06]">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-500 transition-colors duration-300 group-hover:bg-accent-600 group-hover:text-white">
                  <scenario.icon className="h-5 w-5" aria-hidden="true" />
                </span>
                <h3 className="mt-4 text-[15px] leading-snug font-semibold text-slate-900">
                  {scenario.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-500">
                  {scenario.description}
                </p>
                <p className="mt-4 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2.5 text-[13px] leading-snug text-slate-600 italic">
                  «{scenario.exampleQuestion}»
                </p>
              </article>
            </Reveal>
          </li>
        ))}
      </ul>
    </Section>
  );
}
