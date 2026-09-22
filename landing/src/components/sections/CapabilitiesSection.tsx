import { capabilities, capabilitiesContent } from '../../data/capabilities';
import { sectionIds } from '../../data/navigation';
import { FeatureCard } from '../ui/FeatureCard';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

export function CapabilitiesSection() {
  return (
    <Section id={sectionIds.capabilities} tone="muted" aria-labelledby="capabilities-heading">
      <SectionHeader
        headingId="capabilities-heading"
        eyebrow={capabilitiesContent.eyebrow}
        title={capabilitiesContent.title}
        description={capabilitiesContent.description}
      />

      <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {capabilities.map((capability, index) => (
          <Reveal key={capability.id} delay={index * 60}>
            <FeatureCard
              icon={capability.icon}
              title={capability.title}
              description={capability.description}
              className="h-full"
            />
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
