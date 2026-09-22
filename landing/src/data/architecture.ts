import {
  Blocks,
  Database,
  FileText,
  Layers3,
  ListOrdered,
  MessagesSquare,
  ScanSearch,
  Sparkles,
  Wrench,
} from 'lucide-react';
import type { ArchitectureNode } from '../types/content';

export const architectureContent = {
  eyebrow: 'Архитектура',
  title: 'Как система находит информацию и формирует ответ',
  description:
    'Запрос проходит через несколько компонентов системы: от поиска нужной информации до формирования ответа на основе корпоративных документов.',
  flowLabel: 'Работа с запросом',
  infraLabel: 'Компоненты системы',
};

export const queryFlow: ArchitectureNode[] = [
  {
    id: 'query',
    icon: MessagesSquare,
    title: 'Вопрос пользователя',
    short: 'Запрос',
    description:
      'Сотрудник задаёт вопрос на естественном языке.',
  },

  {
    id: 'retrieval',
    icon: ScanSearch,
    title: 'Поиск информации',
    short: 'Поиск',
    description:
      'Система ищет подходящую информацию среди документов, учитывая содержание запроса и точные совпадения.',
  },

  {
    id: 'rerank',
    icon: ListOrdered,
    title: 'Отбор результатов',
    short: 'Релевантность',
    description:
      'Найденная информация дополнительно оценивается, чтобы выбрать наиболее подходящие фрагменты для ответа.',
  },

  {
    id: 'context',
    icon: Blocks,
    title: 'Подготовка данных',
    short: 'Контекст',
    description:
      'Выбранные фрагменты и сведения об их источниках передаются для формирования ответа.',
  },

  {
    id: 'llm',
    icon: Sparkles,
    title: 'Формирование ответа',
    short: 'Генерация',
    description:
      'Языковая модель формулирует ответ на основе найденной информации и данных из корпоративных документов.',
  },

  {
    id: 'answer',
    icon: FileText,
    title: 'Ответ с источниками',
    short: 'Результат',
    description:
      'Пользователь получает ответ вместе с фрагментами документов, которые позволяют проверить использованную информацию.',
  },
];

export const infrastructureNodes: ArchitectureNode[] = [
  {
    id: 'storage',
    icon: Database,
    title: 'Хранилище документов',
    short: 'Файлы',
    description:
      'Оригинальные документы хранятся отдельно от поисковых данных и остаются доступны для просмотра.',
  },

  {
    id: 'indexes',
    icon: Layers3,
    title: 'Поисковая база',
    short: 'Индекс данных',
    description:
      'Подготовленная информация организована так, чтобы система могла быстро находить нужные фрагменты документов.',
  },

  {
    id: 'workers',
    icon: Wrench,
    title: 'Фоновая обработка',
    short: 'Задачи',
    description:
      'Тяжёлые операции с документами выполняются в фоне, поэтому загрузка и обработка файлов не блокируют основной интерфейс.',
  },
];