import { useEffect, useState } from 'react';
import { Menu, X } from 'lucide-react';
import { cn } from '../../lib/cn';
import { brand, headerCta, headerLabels, mobileMenu, navigationLinks } from '../../data/navigation';
import { useActiveSection } from '../../hooks/useActiveSection';
import { useScrolled } from '../../hooks/useScrolled';
import { Button } from '../ui/Button';
import { Logo } from './Logo';

const NAV_IDS = navigationLinks.map((item) => item.id);

export function Header() {
  const scrolled = useScrolled();
  const active = useActiveSection(NAV_IDS);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (!menuOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMenuOpen(false);
    };
    document.addEventListener('keydown', onKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = '';
    };
  }, [menuOpen]);

  return (
    <header
      className={cn(
        'fixed inset-x-0 top-0 z-50 transition-all duration-300',
        scrolled || menuOpen
          ? 'border-b border-slate-200/80 bg-white/85 shadow-[0_1px_12px_rgba(10,17,32,0.06)] backdrop-blur-md'
          : 'border-b border-transparent bg-transparent',
      )}
    >
      <div
        className={cn(
          'mx-auto flex w-full max-w-6xl items-center justify-between px-4 transition-all duration-300 sm:px-6 lg:px-8',
          scrolled ? 'py-2.5' : 'py-4 sm:py-5',
        )}
      >
        <a
          href="#top"
          className="rounded-lg"
          aria-label={headerLabels.logoHomeAria(brand.name)}
        >
          <Logo compact={scrolled} />
        </a>

        <nav aria-label={headerLabels.mainNavAria} className="hidden items-center gap-1 lg:flex">
          {navigationLinks.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              aria-current={active === item.id ? 'true' : undefined}
              className={cn(
                'rounded-md px-3.5 py-2 text-sm font-medium transition-colors duration-200',
                active === item.id
                  ? 'bg-accent-50 text-accent-700'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
              )}
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="hidden lg:block">
          <Button href={headerCta.href} size="md">
            {headerCta.label}
          </Button>
        </div>

        <button
          type="button"
          className="rounded-lg p-2 text-slate-700 hover:bg-slate-100 lg:hidden"
          aria-expanded={menuOpen}
          aria-controls="mobile-menu"
          aria-label={menuOpen ? mobileMenu.closeLabel : mobileMenu.openLabel}
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      <div
        id="mobile-menu"
        className={cn(
          'overflow-hidden border-t border-slate-200/80 bg-white transition-[max-height] duration-300 lg:hidden',
          menuOpen ? 'max-h-[420px]' : 'max-h-0 border-t-transparent',
        )}
        aria-hidden={!menuOpen}
      >
        <nav aria-label={headerLabels.mobileNavAria} className="flex flex-col gap-1 px-4 py-4 sm:px-6">
          {navigationLinks.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              tabIndex={menuOpen ? 0 : -1}
              onClick={() => setMenuOpen(false)}
              className={cn(
                'rounded-lg px-3 py-2.5 text-base font-medium',
                active === item.id ? 'bg-accent-50 text-accent-700' : 'text-slate-700 hover:bg-slate-100',
              )}
            >
              {item.label}
            </a>
          ))}
          <div className="mt-2">
            <Button href={headerCta.href} size="lg" className="w-full">
              {headerCta.label}
            </Button>
          </div>
        </nav>
      </div>
    </header>
  );
}
