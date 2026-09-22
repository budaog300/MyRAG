import { brand, navigationLinks, sectionIds } from './navigation';

export const footerContent = {
  brandName: brand.name,
  description:
    'INTEVRUM Group — корпоративные решения в области AI и работы с данными: интеллектуальный поиск по документам, RAG-системы и внедрение на инфраструктуре заказчика.',
  sections: {
    navigationTitle: 'Разделы',
    companyTitle: 'Компания',
    contactsTitle: 'Контакты',
  },
  productLinks: [
    { label: 'Интерактивное демо', href: `#${sectionIds.demo}` },
    { label: 'Как проходит пилот', href: `#${sectionIds.pilot}` },
    { label: 'Частые вопросы', href: `#${sectionIds.faq}` },
    { label: 'Запросить демонстрацию', href: `#${sectionIds.contact}` },
  ],
  navigationLinks,
  contacts: {
    email: 'intevrum_group@mail.ru',
    phone: '+7 (964) 859-69-68',
    address: '',
    links: [] as Array<{ label: string; href: string }>,
  },
  copyright: `© ${new Date().getFullYear()} ${brand.name}. Все права защищены.`,
};
