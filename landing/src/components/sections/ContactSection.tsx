import { contactContent } from '../../data/contact';
import { sectionIds } from '../../data/navigation';
import { ContactForm } from '../form/ContactForm';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

export function ContactSection() {
  return (
    <Section id={sectionIds.contact} aria-labelledby="contact-heading">
      <div className="grid gap-10 lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)] lg:gap-16">
        <div>
          <SectionHeader
            headingId="contact-heading"
            eyebrow={contactContent.eyebrow}
            title={contactContent.title}
            description={contactContent.description}
            align="left"
            className="max-w-none"
          />
          <Reveal delay={100}>
            <ul className="mt-8 space-y-4 border-t border-slate-200 pt-8">
              {contactContent.asidePoints.map((point) => (
                <li key={point} className="flex items-start gap-3 text-sm leading-relaxed text-slate-600">
                  <span
                    aria-hidden="true"
                    className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-accent-500"
                  />
                  {point}
                </li>
              ))}
            </ul>
          </Reveal>
        </div>

        <Reveal delay={150} className="min-w-0">
          <ContactForm />
        </Reveal>
      </div>
    </Section>
  );
}
