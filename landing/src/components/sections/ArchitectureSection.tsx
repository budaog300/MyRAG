import { useState } from 'react';
import { architectureContent, infrastructureNodes, queryFlow } from '../../data/architecture';
import { sectionIds } from '../../data/navigation';
import { ArchitectureNode } from '../ui/ArchitectureNode';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

const ALL_NODES = [...queryFlow, ...infrastructureNodes];

export function ArchitectureSection() {
  const [activeId, setActiveId] = useState<string>(queryFlow[0].id);
  const activeNode = ALL_NODES.find((node) => node.id === activeId) ?? queryFlow[0];

  return (
    <Section
      id={sectionIds.architecture}
      tone="dark"
      aria-labelledby="architecture-heading"
      className="relative overflow-hidden"
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 [background-image:linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] [background-size:48px_48px] [mask-image:radial-gradient(ellipse_80%_70%_at_50%_0%,black,transparent)]"
      />
      <div className="relative">
        <SectionHeader
          headingId="architecture-heading"
          eyebrow={architectureContent.eyebrow}
          title={architectureContent.title}
          description={architectureContent.description}
          tone="dark"
        />

        <Reveal className="mt-14">
          <p className="mb-4 text-xs font-semibold tracking-[0.16em] text-slate-500 uppercase">
            {architectureContent.flowLabel}
          </p>
          <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3 lg:grid-cols-6" aria-label={architectureContent.flowLabel}>
            {queryFlow.map((node) => (
              <div key={node.id} className="min-w-0">
                <ArchitectureNode
                  icon={node.icon}
                  title={node.title}
                  short={node.short}
                  active={node.id === activeId}
                  onClick={() => setActiveId(node.id)}
                />
              </div>
            ))}
          </div>
        </Reveal>

        <Reveal delay={80} className="mt-6">
          <p className="mb-4 text-xs font-semibold tracking-[0.16em] text-slate-500 uppercase">
            {architectureContent.infraLabel}
          </p>
          <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
            {infrastructureNodes.map((node) => (
              <div key={node.id} className="min-w-0">
                <ArchitectureNode
                  icon={node.icon}
                  title={node.title}
                  short={node.short}
                  active={node.id === activeId}
                  onClick={() => setActiveId(node.id)}
                />
              </div>
            ))}
          </div>
        </Reveal>

        <Reveal delay={120}>
          <div
            className="mt-6 rounded-2xl border border-white/10 bg-white/[0.04] p-5 sm:p-6"
            aria-live="polite"
          >
            <h3 className="text-base font-semibold text-white">{activeNode.title}</h3>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-300">
              {activeNode.description}
            </p>
          </div>
        </Reveal>
      </div>
    </Section>
  );
}
