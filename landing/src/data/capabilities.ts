import {
  Boxes,
  Gauge,
  Layers,
  Network,
  Quote,
  ScanSearch,
} from 'lucide-react';
import type { Capability } from '../types/content';

export const capabilitiesContent = {
  eyebrow: 'Возможности',
  title: 'Что система делает с вашими документами',
  description:
    'Полный цикл: от загрузки разнородных файлов до ответа, построенного на релевантных фрагментах корпоративной базы знаний.',
};

export const capabilities: Capability[] = [
  {
    id: 'hybrid-search',
    icon: Network,
    title: 'Гибридный поиск',
    description:
      'Семантический и полнотекстовый поиск работают вместе: система учитывает и смысл запроса, и точные совпадения терминов, номеров и цитат.',
  },
  {
    id: 'reranking',
    icon: Gauge,
    title: 'Ранжирование результатов',
    description:
      'Найденные фрагменты повторно оцениваются относительно исходного вопроса — в контекст ответа попадают наиболее релевантные.',
  },
  {
    id: 'formats',
    icon: Layers,
    title: 'Разные форматы документов',
    description:
      'PDF, DOCX, XLSX, PPTX, Markdown, HTML, TXT и изображения.',
  },
  {
    id: 'grounded-answers',
    icon: Quote,
    title: 'Ответы с указанием источников',
    description:
      'Ответ формируется на основе найденных фрагментов и сопровождается ссылками на документы, из которых взята информация.',
  },
  {
    id: 'large-corpus',
    icon: ScanSearch,
    title: 'Работа с большими массивами',
    description:
      'База знаний растёт вместе с вашими документами — без простоев и пересборки.',
  },
  {
    id: 'isolated-deploy',
    icon: Boxes,
    title: 'Изолированное развёртывание',
    description:
      'Для каждого заказчика разворачивается отдельный контур с собственными документами, индексами и хранилищем.',
  },
];
