import { demoContent } from '../../data/demo';
import { sectionIds } from '../../data/navigation';
import { RagDemo } from '../demo/RagDemo';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

export function RagDemoSection() {
  return (
    <Section id={sectionIds.demo} tone="dark" aria-labelledby="demo-heading" className="relative overflow-hidden">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-64 bg-gradient-to-b from-accent-400/[0.06] to-transparent"
      />
      <div className="relative">
        <SectionHeader
          headingId="demo-heading"
          eyebrow={demoContent.eyebrow}
          title={demoContent.title}
          description={demoContent.description}
          tone="dark"
        />
        <div className="mt-14">
          <RagDemo />
        </div>
      </div>
    </Section>
  );
}
