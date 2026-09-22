import { deploymentContent, deploymentPoints, deploymentStack } from '../../data/deployment';
import { sectionIds } from '../../data/navigation';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

export function DeploymentSection() {
  return (
    <Section id={sectionIds.deployment} aria-labelledby="deployment-heading">
      <div className="grid gap-12 lg:grid-cols-2 lg:gap-16">
        <div>
          <SectionHeader
            headingId="deployment-heading"
            eyebrow={deploymentContent.eyebrow}
            title={deploymentContent.title}
            description={deploymentContent.description}
            align="left"
            className="max-w-none"
          />
          <ul className="mt-8 space-y-5">
            {deploymentPoints.map((point, index) => (
              <Reveal key={point.title} delay={index * 80}>
                <li className="flex gap-4">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent-50 text-accent-600">
                    <point.icon className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <div>
                    <h3 className="text-[15px] font-semibold text-slate-900">{point.title}</h3>
                    <p className="mt-1 text-sm leading-relaxed text-slate-500">{point.description}</p>
                  </div>
                </li>
              </Reveal>
            ))}
          </ul>
        </div>

        <Reveal delay={120} className="min-w-0">
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50/60 p-5 sm:p-7">
            <p className="text-xs font-semibold tracking-[0.16em] text-slate-400 uppercase">
              {deploymentContent.environmentLabel}
            </p>

            <div className="mt-4 rounded-2xl border border-accent-200 bg-white p-5 shadow-sm sm:p-6">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold text-slate-900">
                  {deploymentContent.stackLabel}
                </p>
                <span className="rounded-full bg-accent-50 px-2.5 py-1 text-[10px] font-bold tracking-wide text-accent-700 uppercase">
                  isolated
                </span>
              </div>

              <div className="mt-4 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                {deploymentStack.map((node) => (
                  <div
                    key={node.id}
                    className="flex items-start gap-3 rounded-xl border border-slate-200 bg-slate-50/70 p-3.5"
                  >
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white text-accent-600 ring-1 ring-slate-200">
                      <node.icon className="h-4 w-4" aria-hidden="true" />
                    </span>
                    <div className="min-w-0">
                      <p className="text-[13px] leading-tight font-semibold text-slate-800">
                        {node.title}
                      </p>
                      <p className="mt-0.5 text-xs text-slate-500">{node.short}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <p className="mt-4 text-xs leading-relaxed text-slate-400">{deploymentContent.note}</p>
          </div>
        </Reveal>
      </div>
    </Section>
  );
}
