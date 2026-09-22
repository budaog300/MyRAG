import { cn } from '../../lib/cn';

type DocumentTypeCardProps = {
  extension: string;
  name: string;
  description: string;
};

/**
 * Карточка формата документа. Описание видно всегда (доступность без hover);
 * при hover/focus карточка слегка приподнимается и подсвечивается.
 */
export function DocumentTypeCard({ extension, name, description }: DocumentTypeCardProps) {
  return (
    <div
      className={cn(
        'group relative flex min-h-[132px] flex-col justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all duration-300',
        'hover:-translate-y-0.5 hover:border-accent-300 hover:bg-accent-50/60 hover:shadow-md hover:shadow-accent-900/5',
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          'inline-flex h-9 w-auto items-center justify-center self-start rounded-md px-2.5 text-xs font-bold tracking-wide',
          'bg-slate-100 text-slate-600 transition-colors duration-300 group-hover:bg-accent-600 group-hover:text-white',
        )}
      >
        {extension}
      </span>
      <div>
        <p className="text-sm font-semibold text-slate-900">{name}</p>
        <p className="mt-1 text-xs leading-relaxed text-slate-500 sm:text-[13px]">{description}</p>
      </div>
    </div>
  );
}
