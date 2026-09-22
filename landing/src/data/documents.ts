import type { DocumentFormat } from '../types/content';

export const documentsContent = {
  eyebrow: 'Форматы',
  title: 'Документы, с которыми работает система',
  description:
    'Единый конвейер обработки приводит разнородные файлы к индексируемому виду с сохранением привязки фрагментов к месту в исходном документе.',
};

export const documentFormats: DocumentFormat[] = [
  {
    id: 'pdf',
    extension: 'PDF',
    name: 'PDF-документы',
    description: 'Регламенты, приказы и сканы: текст извлекается с привязкой к страницам.',
  },
  {
    id: 'docx',
    extension: 'DOCX',
    name: 'Word-документы',
    description: 'Текст, структура разделов и заголовков сохраняются при разбиении на фрагменты.',
  },
  {
    id: 'xlsx',
    extension: 'XLSX',
    name: 'Excel-таблицы',
    description: 'Листы и табличные данные индексируются как содержательно, так и по значениям.',
  },
  {
    id: 'pptx',
    extension: 'PPTX',
    name: 'PowerPoint',
    description: 'Содержимое слайдов и заметки докладчиков становятся частью базы знаний.',
  },
  {
    id: 'md',
    extension: 'MD',
    name: 'Markdown',
    description: 'Структурированная разметка: заголовки и разделы учитываются при разбиении.',
  },
  {
    id: 'html',
    extension: 'HTML',
    name: 'HTML-страницы',
    description: 'Внутренние вики, выгрузки и веб-страницы обрабатываются без ручной конвертации.',
  },
  {
    id: 'txt',
    extension: 'TXT',
    name: 'Текстовые файлы',
    description: 'Простой текст индексируется напрямую — без дополнительных конвертаций.',
  },
  {
    id: 'img',
    extension: 'IMG',
    name: 'Изображения',
    description: 'Схемы, фотографии документов и диаграммы: используется извлечённый текстовый контент.',
  },
];
