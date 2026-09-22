import type { NavItem } from '../types/content';

export const brand = {
  name: 'INTEVRUM Group',
  logoAlt: 'INTEVRUM Group',
};

export const navigationLinks: NavItem[] = [
  { id: 'capabilities', label: 'Возможности' },
  { id: 'how-it-works', label: 'Как это работает' },
  { id: 'scenarios', label: 'Сценарии' },
  { id: 'architecture', label: 'Архитектура' },
];

/** Якоря секций, используемые в навигации, CTA и футере. */
export const sectionIds = {
  capabilities: 'capabilities',
  demo: 'demo',
  howItWorks: 'how-it-works',
  scenarios: 'scenarios',
  architecture: 'architecture',
  deployment: 'deployment',
  pilot: 'pilot',
  faq: 'faq',
  contact: 'contact',
} as const;

export const headerCta = {
  label: 'Запросить демонстрацию',
  href: `#${sectionIds.contact}`,
};

export const mobileMenu = {
  openLabel: 'Открыть меню',
  closeLabel: 'Закрыть меню',
};

export const headerLabels = {
  mainNavAria: 'Основная навигация',
  mobileNavAria: 'Мобильная навигация',
  logoHomeAria: (name: string) => `${name} — на главную`,
};

export const skipLink = {
  label: 'Перейти к содержанию',
  href: '#main',
};
