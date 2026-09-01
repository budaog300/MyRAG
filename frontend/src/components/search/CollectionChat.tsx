import { useState } from "react";
import { useParams } from "react-router-dom";
import { useSearch } from "@/hooks/useSearch";
import Spinner from "@/components/ui/Spinner";
import type { SearchRequest } from "@/types/search";

const DEFAULT_SETTINGS: SearchRequest = {
  query: "",
  retrieve_limit: 30,
  merge_limit: 10,
  top_k: 5,
  temperature: 0.3,
  max_tokens: 512,
  only_context: false,
};

const CollectionChat = () => {
  const { collectionId } = useParams<{ collectionId: string }>();
  const [input, setInput] = useState("");
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const search = useSearch(collectionId ?? "");

  const isOnlyContext = settings.only_context;

  const handleSearch = async () => {
    if (!collectionId || !input.trim()) {
      return;
    }

    await search.mutateAsync({
      ...settings,
      query: input.trim(),
    });
  };

  const documents = search.data?.documents ?? [];
  const showAnswer = !isOnlyContext && Boolean(search.data?.answer);

  return (
    <div className="space-y-6">
      <div className="space-y-3 rounded-2xl border border-border bg-card p-4">
        <div className="flex flex-col gap-3 md:flex-row">
          <input
            className="flex-1 rounded-2xl border border-border bg-muted/20 px-3 py-2 text-sm text-foreground"
            placeholder="Задайте вопрос"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            disabled={search.isPending}
          />
          <button
            className="rounded-2xl bg-secondary px-4 py-2 text-sm font-semibold text-secondary-foreground disabled:opacity-50"
            onClick={handleSearch}
            disabled={search.isPending || !input.trim()}
          >
            {search.isPending ? "Выполняем" : "Отправить"}
          </button>
        </div>
        <div className="grid gap-2 md:grid-cols-3">
          <label className="text-[11px] text-muted-foreground">
            <span className="block uppercase tracking-[0.3em]">retrieve_limit</span>
            <input
              type="number"
              value={settings.retrieve_limit}
              min={1}
              onChange={(event) =>
                setSettings((prev) => ({ ...prev, retrieve_limit: Number(event.target.value) }))
              }
              className="w-full rounded-xl border border-border bg-card px-2 py-1 text-xs text-foreground"
            />
          </label>
          <label className="text-[11px] text-muted-foreground">
            <span className="block uppercase tracking-[0.3em]">merge_limit</span>
            <input
              type="number"
              value={settings.merge_limit}
              min={1}
              onChange={(event) =>
                setSettings((prev) => ({ ...prev, merge_limit: Number(event.target.value) }))
              }
              className="w-full rounded-xl border border-border bg-card px-2 py-1 text-xs text-foreground"
            />
          </label>
          <label className="text-[11px] text-muted-foreground">
            <span className="block uppercase tracking-[0.3em]">top_k</span>
            <input
              type="number"
              value={settings.top_k}
              min={1}
              max={10}
              onChange={(event) =>
                setSettings((prev) => ({ ...prev, top_k: Number(event.target.value) }))
              }
              className="w-full rounded-xl border border-border bg-card px-2 py-1 text-xs text-foreground"
            />
          </label>
          <label className="text-[11px] text-muted-foreground">
            <span className="block uppercase tracking-[0.3em]">temperature</span>
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={settings.temperature}
              onChange={(event) =>
                setSettings((prev) => ({ ...prev, temperature: Number(event.target.value) }))
              }
              className="w-full"
            />
          </label>
          <label className="flex items-center gap-2 text-xs text-muted-foreground">
            <input
              type="checkbox"
              checked={settings.only_context}
              onChange={(event) =>
                setSettings((prev) => ({ ...prev, only_context: event.target.checked }))
              }
            />
            <span>Вернуть только контекст</span>
          </label>
        </div>
      </div>

      {search.isPending && (
        <div className="rounded-2xl border border-border bg-card p-6 text-center">
          <Spinner />
        </div>
      )}

      {search.isError && (
        <div className="rounded-2xl border border-border bg-card p-6 text-center text-sm text-destructive">
          Ошибка запроса. Попробуйте позже.
        </div>
      )}

      {showAnswer && search.data?.answer && (
        <div className="rounded-2xl border border-border bg-card p-6 text-sm text-foreground">
          <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Ответ LLM</p>
          <p className="mt-2 text-base leading-relaxed">{search.data.answer}</p>
        </div>
      )}

      {(documents.length > 0 || (!documents.length && !search.isPending && !search.isError && search.isSuccess)) && (
        <div className="rounded-2xl border border-border bg-card p-4 space-y-3">
          <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Источники</p>
          {documents.length === 0 ? (
            <p className="text-sm text-muted-foreground">Источники не найдены.</p>
          ) : (
            documents.map((doc) => (
              <article key={doc.id ?? doc.source} className="rounded-2xl border border-border bg-muted/20 p-3 text-sm">
                <div className="flex items-center justify-between text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
                  <span>{doc.source || "Источник"}</span>
                  <span>Score: {doc.score?.toFixed(4) ?? "~"}</span>
                </div>
                <p className="mt-2 text-xs text-muted-foreground">{doc.content}</p>
              </article>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default CollectionChat;
