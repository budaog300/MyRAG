import type { ReactNode } from 'react';
import { skipLink } from '../../data/navigation';
import { Header } from './Header';
import { Footer } from './Footer';

/** Каркас страниц: skip-link, sticky header, main, footer. */
export function SiteLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <a
        href={skipLink.href}
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-[60] focus:rounded-lg focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-slate-900 focus:shadow-lg"
      >
        {skipLink.label}
      </a>
      <Header />
      <main id="main">{children}</main>
      <Footer />
    </>
  );
}
