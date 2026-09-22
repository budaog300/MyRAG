import {
  BookOpenCheck,
  Building2,
  Cpu,
  FlaskConical,
  ScrollText,
  UsersRound,
} from 'lucide-react';
import type { Scenario } from '../types/content';

export const scenariosContent = {
  eyebrow: 'Сценарии',
  title: 'Где система применима в компании',
  description:
    'Поиск и работа с корпоративными документами в задачах, где сотрудникам регулярно приходится искать конкретную информацию.',
};

export const scenarios: Scenario[] = [
  {
    id: 'regulations',
    icon: ScrollText,
    title: 'Внутренние регламенты и политики',
    description:
      'Быстрый поиск информации о процедурах, правилах, ролях и зонах ответственности.',
    exampleQuestion: 'Кто согласовывает служебную записку?',
  },

  {
    id: 'instructions',
    icon: BookOpenCheck,
    title: 'Инструкции и чек-листы',
    description:
      'Нужный шаг или порядок действий можно найти без чтения документа целиком.',
    exampleQuestion: 'Как оформить доступ к архиву документов?',
  },

  {
    id: 'tech-docs',
    icon: Cpu,
    title: 'Техническая документация',
    description:
      'Поиск параметров оборудования, требований, версий и сведений об интеграциях между системами.',
    exampleQuestion: 'Какие требования указаны для резервного копирования?',
  },

  {
    id: 'operations',
    icon: Building2,
    title: 'Операционные документы',
    description:
      'Поиск информации в приказах, распоряжениях, отчётах и других рабочих документах.',
    exampleQuestion: 'В каком документе указаны новые сроки документооборота?',
  },

  {
    id: 'reference',
    icon: FlaskConical,
    title: 'Нормативные и справочные материалы',
    description:
      'Быстрый поиск нужных положений, требований и справочной информации с указанием источника.',
    exampleQuestion: 'Какой период хранения указан для первичных документов?',
  },

  {
    id: 'departments',
    icon: UsersRound,
    title: 'Документы подразделений',
    description:
      'Отдельные базы знаний для подразделений с документацией, относящейся к их рабочим задачам.',
    exampleQuestion: 'Что указано в регламенте ИТ-отдела о паролях?',
  },
];