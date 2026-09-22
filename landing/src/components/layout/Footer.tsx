import { footerContent } from '../../data/footer';
import { cn } from '../../lib/cn';
import { Container } from '../ui/Container';
import { Logo } from './Logo';

export function Footer() {
  const { contacts, sections, productLinks, navigationLinks } = footerContent;

  const hasContactDetails = Boolean(
    contacts.email ||
    contacts.phone ||
    contacts.address ||
    contacts.links.length > 0,
  );

  return (
    <footer className="bg-ink-950 text-slate-400">
      <Container className="py-16 sm:py-20">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-4">
          <div className="lg:col-span-2">
            <Logo variant="dark" />
            <p className="mt-5 max-w-md text-sm leading-relaxed">
              {footerContent.description}
            </p>
          </div>

          <nav aria-label={sections.navigationTitle}>
            <h2 className="text-sm font-semibold tracking-wide text-white uppercase">
              {sections.navigationTitle}
            </h2>

            <ul className="mt-4 space-y-2.5">
              {navigationLinks.map((item) => (
                <li key={item.id}>
                  <a
                    href={`#${item.id}`}
                    className="text-sm transition-colors duration-200 hover:text-white"
                  >
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          <nav aria-label={sections.companyTitle}>
            <h2 className="text-sm font-semibold tracking-wide text-white uppercase">
              {sections.companyTitle}
            </h2>

            <ul className="mt-4 space-y-2.5">
              {productLinks.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-sm transition-colors duration-200 hover:text-white"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        {hasContactDetails ? (
          <div className="mt-12 grid gap-8 border-t border-white/10 pt-8 sm:grid-cols-2">
            <section aria-label={sections.contactsTitle}>
              <h2 className="text-sm font-semibold tracking-wide text-white uppercase">
                {sections.contactsTitle}
              </h2>

              <ul className="mt-4 space-y-2 text-sm">
                {contacts.email ? <li>{contacts.email}</li> : null}
                {contacts.phone ? <li>{contacts.phone}</li> : null}
                {contacts.address ? <li>{contacts.address}</li> : null}

                {contacts.links.map((link) => (
                  <li key={link.href}>
                    <a href={link.href} className="hover:text-white">
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </section>

            <p className={cn('text-sm sm:text-right')}>
              {footerContent.copyright}
            </p>
          </div>
        ) : (
          <div className="mt-12 border-t border-white/10 pt-8">
            <p className="text-sm">{footerContent.copyright}</p>
          </div>
        )}
      </Container>
    </footer>
  );
}