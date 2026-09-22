import { ChevronDown } from 'lucide-react';
import { faqContent, faqItems } from '../../data/faq';
import { sectionIds } from '../../data/navigation';
import { cn } from '../../lib/cn';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

export function FaqSchema() {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqItems.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: { '@type': 'Answer', text: item.answer },
    })),
  };

  return (
    <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />
  );
}

export function FaqSection() {
  return (
    <Section id={sectionIds.faq} aria-labelledby="faq-heading">
      <SectionHeader
        headingId="faq-heading"
        eyebrow={faqContent.eyebrow}
        title={faqContent.title}
        description={faqContent.description}
      />

      <Reveal className="mx-auto mt-12 max-w-3xl">
        <div className="divide-y divide-slate-200 border-y border-slate-200">
          {faqItems.map((item) => (
            <details key={item.id} className="group py-1">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 rounded-lg py-4 text-[15px] font-semibold text-slate-900 transition-colors duration-200 hover:text-accent-700 [&::-webkit-details-marker]:hidden">
                <h3>{item.question}</h3>
                <ChevronDown
                  aria-hidden="true"
                  className={cn(
                    'h-4 w-4 shrink-0 text-slate-400 transition-transform duration-300',
                    'group-open:rotate-180',
                  )}
                />
              </summary>
              <p className="pr-8 pb-4 text-sm leading-relaxed text-slate-500">{item.answer}</p>
            </details>
          ))}
        </div>
      </Reveal>
    </Section>
  );
}
