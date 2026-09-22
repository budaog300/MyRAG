import { useEffect, useState } from 'react';
import { heroMockup } from '../../data/landing';
import { demoScenarios } from '../../data/demo';
import { FileText, Search } from 'lucide-react';

const ROTATE_MS = 7000;

/**
 * Декоративный mockup RAG-интерфейса в hero: автоматически перебирает
 * демо-сценарии. Для скринридеров скрыт (интерактивное демо — в секции #demo).
 */
export function HeroDemoMockup() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const id = window.setInterval(() => {
      setIndex((current) => (current + 1) % demoScenarios.length);
    }, ROTATE_MS);
    return () => window.clearInterval(id);
  }, []);

  const scenario = demoScenarios[index];

  return (
    <div
      aria-hidden="true"
      className="relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-[0_24px_70px_-30px_rgba(10,17,32,0.35)]"
    >
      <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50/80 px-4 py-3">
        <span className="h-2.5 w-2.5 rounded-full bg-slate-200" />
        <span className="h-2.5 w-2.5 rounded-full bg-slate-200" />
        <span className="h-2.5 w-2.5 rounded-full bg-accent-300" />
        <p className="ml-2 truncate font-mono text-[11px] text-slate-400">{heroMockup.windowTitle}</p>
      </div>

      <div key={scenario.id} className="demo-in flex flex-col gap-4 p-4 sm:p-6">
        <div className="flex justify-end">
          <p className="max-w-[85%] rounded-2xl rounded-br-sm bg-ink-950 px-4 py-2.5 text-[13px] leading-snug font-medium text-white">
            {scenario.question}
          </p>
        </div>

        <div className="flex items-center gap-2 text-[11px] font-medium text-accent-600">
          <Search className="h-3.5 w-3.5" />
          {heroMockup.statusLine}
        </div>

        <div>
          <p className="mb-2 text-[10px] font-semibold tracking-[0.16em] text-slate-400 uppercase">
            {heroMockup.sourcesLabel}
          </p>
          <div className="space-y-2">
            {scenario.sources.slice(0, 2).map((source) => (
              <div
                key={source.id}
                className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50/60 px-3.5 py-2.5"
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-white text-accent-600 ring-1 ring-slate-200">
                  <FileText className="h-3.5 w-3.5" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-semibold text-slate-700">{source.document}</p>
                  <p className="truncate text-[11px] text-slate-400">{source.location}</p>
                </div>
                <span className="font-mono text-[10px] text-slate-400">
                  {Math.round(source.relevance * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-accent-100 bg-accent-50/70 px-4 py-3">
          <p className="mb-1.5 text-[10px] font-semibold tracking-[0.16em] text-accent-700 uppercase">
            {heroMockup.answerLabel}
          </p>
          <p className="line-clamp-4 text-[13px] leading-relaxed text-slate-700">
            {scenario.answer.join(' ')}
          </p>
        </div>

        <div className="mt-1 flex justify-end gap-1.5">
          {demoScenarios.map((item, dotIndex) => (
            <span
              key={item.id}
              className={
                dotIndex === index
                  ? 'h-1.5 w-4 rounded-full bg-accent-500'
                  : 'h-1.5 w-1.5 rounded-full bg-slate-200'
              }
            />
          ))}
        </div>
      </div>
    </div>
  );
}
