import { useCallback, useEffect, useRef, useState } from 'react';
import { ArrowRight, Check, LoaderCircle, Search } from 'lucide-react';
import { demoContent, demoScenarios } from '../../data/demo';
import { matchDemoScenario } from '../../lib/demoMatch';
import type { DemoPhase, DemoScenario } from '../../types/demo';
import { DemoQuestion } from './DemoQuestion';
import { SourceCard } from './SourceCard';

const PHASE_SEARCHING_MS = 700;
const PHASE_SOURCES_MS = 1700;

const SEARCH_STEPS: Record<DemoPhase, string> = {
  idle: '',
  searching: demoContent.searchStatusLabel,
  sources: demoContent.sourcesLabel,
  answer: demoContent.answerLabel,
};

export function RagDemo() {
  const [selectedId, setSelectedId] = useState<string>(demoScenarios[0].id);
  const [scenario, setScenario] = useState<DemoScenario | undefined>(demoScenarios[0]);
  const [phase, setPhase] = useState<DemoPhase>('answer');
  const [input, setInput] = useState('');
  const timersRef = useRef<number[]>([]);

  const clearTimers = useCallback(() => {
    timersRef.current.forEach((id) => window.clearTimeout(id));
    timersRef.current = [];
  }, []);

  const runScenario = useCallback(
    (target: DemoScenario) => {
      clearTimers();
      setScenario(target);
      setSelectedId(target.id);
      setPhase('searching');
      timersRef.current.push(
        window.setTimeout(() => setPhase('sources'), PHASE_SEARCHING_MS),
        window.setTimeout(() => setPhase('answer'), PHASE_SOURCES_MS),
      );
    },
    [clearTimers],
  );

  useEffect(() => clearTimers, [clearTimers]);

  const handleSelect = (target: DemoScenario) => {
    setInput(target.question);
    runScenario(target);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const matched = matchDemoScenario(input);
    if (matched) {
      runScenario(matched);
      return;
    }
    clearTimers();
    setSelectedId('');
    setScenario(undefined);
    setPhase('searching');
    timersRef.current.push(window.setTimeout(() => setPhase('answer'), PHASE_SEARCHING_MS));
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)] lg:gap-8">
      {/* Левая колонка: вопрос и примеры */}
      <div className="flex flex-col gap-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
        <form onSubmit={handleSubmit} className="min-w-0">
          <label
            htmlFor="demo-question-input"
            className="text-xs font-semibold tracking-[0.14em] text-slate-400 uppercase"
          >
            {demoContent.yourQuestionLabel}
          </label>
          <div className="relative mt-3">
            <Search
              className="pointer-events-none absolute top-1/2 left-4 h-4 w-4 -translate-y-1/2 text-slate-500"
              aria-hidden="true"
            />
            <input
              id="demo-question-input"
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder={demoContent.inputPlaceholder}
              autoComplete="off"
              className="w-full rounded-xl border border-white/10 bg-ink-950/60 py-3.5 pr-12 pl-11 text-sm text-white placeholder:text-slate-500 focus:border-accent-400/60 focus:outline-none"
            />
            <button
              type="submit"
              aria-label={demoContent.yourQuestionLabel}
              className="absolute top-1/2 right-2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-lg bg-accent-600 text-white transition-colors duration-200 hover:bg-accent-500"
            >
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
          <p className="mt-2 text-xs text-slate-500">{demoContent.inputHint}</p>
        </form>

        <div>
          <p className="text-xs font-semibold tracking-[0.14em] text-slate-400 uppercase">
            {demoContent.suggestedLabel}
          </p>
          <div className="mt-3 flex flex-col gap-2">
            {demoScenarios.map((item) => (
              <DemoQuestion
                key={item.id}
                question={item.question}
                active={selectedId === item.id}
                onSelect={() => handleSelect(item)}
              />
            ))}
          </div>
        </div>

        <p className="mt-auto text-[11px] leading-relaxed text-slate-500">{demoContent.disclaimer}</p>
      </div>

      {/* Правая колонка: результат поиска */}
      <div
        className="flex min-w-0 flex-col overflow-hidden rounded-2xl border border-white/10 bg-ink-950/80 shadow-2xl shadow-black/40"
        aria-live="polite"
      >
        <div className="flex items-center gap-2 border-b border-white/10 bg-white/[0.03] px-5 py-3.5">
          <span className="h-2.5 w-2.5 rounded-full bg-white/15" aria-hidden="true" />
          <span className="h-2.5 w-2.5 rounded-full bg-white/15" aria-hidden="true" />
          <span className="h-2.5 w-2.5 rounded-full bg-accent-400/70" aria-hidden="true" />
          <p className="ml-2 min-w-0 flex-1 truncate font-mono text-xs text-slate-400">
            {demoContent.yourQuestionLabel}: {input || scenario?.question}
          </p>
        </div>

        <div className="flex flex-1 flex-col gap-5 p-5 sm:p-6">
          <p className="flex items-center gap-2 text-sm font-medium text-accent-300">
            {phase === 'searching' ? (
              <>
                <LoaderCircle className="h-4 w-4 animate-spin" aria-hidden="true" />
                {SEARCH_STEPS.searching}
              </>
            ) : phase === 'sources' ? (
              <>
                <LoaderCircle className="h-4 w-4 animate-spin" aria-hidden="true" />
                {SEARCH_STEPS.sources}
              </>
            ) : (
              <>
                <Check className="h-4 w-4" aria-hidden="true" />
                {SEARCH_STEPS.answer}
              </>
            )}
          </p>

          {phase === 'searching' ? (
            <div className="flex flex-1 flex-col justify-center gap-3 py-10">
              {[0, 1, 2].map((row) => (
                <div
                  key={row}
                  className="h-4 rounded-full bg-white/5"
                  style={{ width: `${92 - row * 18}%` }}
                  aria-hidden="true"
                />
              ))}
            </div>
          ) : (
            <>
              {scenario ? (
                <ul className="demo-in space-y-3">
                  {scenario.sources.map((source, index) => (
                    <SourceCard
                      key={source.id}
                      source={source}
                      index={index}
                      delayMs={index * 120}
                      relevanceAriaLabel={demoContent.relevanceAriaLabel}
                    />
                  ))}
                </ul>
              ) : (
                <p className="demo-in rounded-xl border border-white/10 bg-white/[0.04] p-4 text-sm text-slate-300">
                  {demoContent.noMatchAnswer}
                </p>
              )}

              {phase === 'answer' && scenario ? (
                <div className="demo-in mt-1 rounded-xl border border-accent-400/30 bg-accent-400/[0.07] p-4 sm:p-5">
                  <p className="text-xs font-semibold tracking-[0.14em] text-accent-300 uppercase">
                    {demoContent.answerLabel}
                  </p>
                  <ul className="mt-3 space-y-2.5">
                    {scenario.answer.map((paragraph, index) => (
                      <li key={index} className="text-sm leading-relaxed text-white/90">
                        {paragraph}
                      </li>
                    ))}
                  </ul>
                  <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-white/10 pt-3 text-[11px] text-slate-400">
                    <span className="font-semibold tracking-wide text-slate-300 uppercase">
                      {demoContent.metaLabel}
                    </span>
                    <span>
                      {scenario.meta.method} · {scenario.meta.processedDocuments}{' '}
                      {demoContent.metaDocumentsUnit} · {scenario.meta.matchedFragments}{' '}
                      {demoContent.metaFragmentsUnit}
                    </span>
                  </div>
                </div>
              ) : null}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
