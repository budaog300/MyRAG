import { documentFormats, documentsContent } from '../../data/documents';
import { DocumentTypeCard } from '../ui/DocumentTypeCard';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';
import { SectionHeader } from '../ui/SectionHeader';

export function DocumentsSection() {
  return (
    <Section tone="muted" aria-labelledby="documents-heading" className="border-y border-slate-200/70">
      <SectionHeader
        headingId="documents-heading"
        eyebrow={documentsContent.eyebrow}
        title={documentsContent.title}
        description={documentsContent.description}
      />
      <Reveal className="mt-14">
        <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4">
          {documentFormats.map((format) => (
            <li key={format.id}>
              <DocumentTypeCard
                extension={format.extension}
                name={format.name}
                description={format.description}
              />
            </li>
          ))}
        </ul>
      </Reveal>
    </Section>
  );
}
