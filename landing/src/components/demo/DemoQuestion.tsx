import { cn } from '../../lib/cn';

type DemoQuestionProps = {
  question: string;
  active: boolean;
  onSelect: () => void;
};

/** Кнопка-вопрос для интерактивного RAG-демо. */
export function DemoQuestion({ question, active, onSelect }: DemoQuestionProps) {
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={active}
      className={cn(
        'w-full rounded-xl border px-4 py-3 text-left text-sm leading-snug transition-all duration-200',
        active
          ? 'border-accent-400/60 bg-accent-400/10 text-white'
          : 'border-white/10 bg-white/[0.03] text-slate-300 hover:border-white/25 hover:bg-white/[0.07] hover:text-white',
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          'mr-2 inline-block h-1.5 w-1.5 rounded-full align-middle transition-colors duration-200',
          active ? 'bg-accent-400' : 'bg-slate-600',
        )}
      />
      {question}
    </button>
  );
}
