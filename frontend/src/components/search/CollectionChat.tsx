import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { MessageSquare, RotateCcw, Send, Settings2, Trash2 } from "lucide-react";
import { useSearch } from "@/hooks/useSearch";
import { chatStore, createMessageId, useChatSession, type ChatMessage } from "@/lib/chatStore";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import Markdown from "@/components/markdown/Markdown";
import SourceCard from "@/components/search/SourceCard";
import InfoTooltip from "@/components/ui/InfoTooltip";
import EmptyState from "@/components/common/EmptyState";

const NEAR_BOTTOM_PX = 140;

const CollectionChat = () => {
  const { collectionId } = useParams<{ collectionId: string }>();
  const session = useChatSession(collectionId);
  const search = useSearch(collectionId ?? "");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [collapsedSources, setCollapsedSources] = useState<Record<string, boolean>>({});
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const isNearBottomRef = useRef(true);

  const { input, settings, messages } = session;
  const isPending = search.isPending;
  const hasMessages = messages.length > 0;

  const handleScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    const distance = el.scrollHeight - el.scrollTop - el.clientHeight;
    isNearBottomRef.current = distance < NEAR_BOTTOM_PX;
  };

  const scrollToBottom = useCallback((behavior: ScrollBehavior = "smooth") => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior });
  }, []);

  useEffect(() => {
    if (isNearBottomRef.current) {
      scrollToBottom();
    }
  }, [messages, scrollToBottom]);

  useEffect(() => {
    if (!hasMessages) {
      textareaRef.current?.focus();
    }
  }, [hasMessages]);

  const setInput = (value: string) => {
    if (!collectionId) return;
    chatStore.setInput(collectionId, value);
  };

  const setSettings = (patch: Partial<typeof settings>) => {
    if (!collectionId) return;
    chatStore.setSettings(collectionId, { ...settings, ...patch });
  };

  const sendQuery = async (queryText: string, pendingId?: string, userMsgId?: string) => {
    if (!collectionId || !queryText.trim() || isPending) return;

    const trimmed = queryText.trim();
    const assistantId = pendingId ?? createMessageId();

    if (!pendingId) {
      const userId = userMsgId ?? createMessageId();
      chatStore.appendMessage(collectionId, { id: userId, role: "user", content: trimmed, status: "done" });
      chatStore.appendMessage(collectionId, { id: assistantId, role: "assistant", content: "", status: "pending" });
    } else {
      chatStore.updateMessage(collectionId, assistantId, { status: "pending", error: undefined });
    }

    isNearBottomRef.current = true;

    try {
      const result = await search.mutateAsync({ ...settings, query: trimmed });
      chatStore.updateMessage(collectionId, assistantId, {
        status: "done",
        content: result.answer ?? "",
        sources: result.documents ?? [],
        responseTimeMs: result.response_time_ms ?? null,
      });
      chatStore.setInput(collectionId, "");
    } catch (error) {
      const message =
        error && typeof error === "object" && "message" in error && typeof error.message === "string"
          ? error.message
          : "Не удалось получить ответ. Попробуйте ещё раз.";
      chatStore.updateMessage(collectionId, assistantId, {
        status: "error",
        error: message,
      });
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    void sendQuery(input);
  };

  const handleRetry = (message: ChatMessage) => {
    if (!collectionId) return;
    const userMessage = [...messages]
      .slice(0, messages.findIndex((m) => m.id === message.id))
      .reverse()
      .find((m) => m.role === "user");
    if (!userMessage) return;
    void sendQuery(userMessage.content, message.id);
  };

  const handleClear = () => {
    if (!collectionId) return;
    chatStore.clearMessages(collectionId);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void sendQuery(input);
    }
  };

  return (
    <div className="flex h-full min-h-0 flex-col gap-4">
      {/* Панель параметров */}
      <div className="rounded-2xl border border-border bg-card shadow-[0_1px_12px_rgba(10,17,32,0.06)]">
        <Button
          type="button"
          variant="ghost"
          onClick={() => setSettingsOpen((prev) => !prev)}
          className="w-full justify-between gap-3 rounded-none px-5 py-3.5 text-left hover:bg-slate-50/70"
          aria-expanded={settingsOpen}
        >
          <span className="flex items-center gap-2 text-sm font-semibold text-slate-800">
            <Settings2 className="h-4 w-4 text-accent-600" aria-hidden="true" />
            Параметры поиска
          </span>
          <span className="flex items-center gap-2 text-xs text-muted-foreground">
            <svg
              className={cn("h-4 w-4 transition-transform duration-300", settingsOpen && "rotate-180")}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              aria-hidden="true"
            >
              <path d="m6 9 6 6 6-6" />
            </svg>
          </span>
        </Button>

        {settingsOpen && (
          <div className="border-t border-border px-5 py-4">
            <div className="grid gap-x-6 gap-y-4 md:grid-cols-2 xl:grid-cols-3">
              <div className="flex min-h-16 flex-col justify-between gap-2">
                <Label className="flex items-center gap-1.5 text-sm text-muted-foreground">
                  Креативность (temperature)
                  <InfoTooltip text="Определяет случайность ответа модели. Низкие значения дают более точные и предсказуемые ответы." />
                </Label>
                <div className="flex items-center gap-3">
                  <Slider
                    min={0}
                    max={1}
                    step={0.01}
                    value={[settings.temperature]}
                    onValueChange={(values) => setSettings({ temperature: values[0] ?? 0.3 })}
                    aria-label="Креативность ответа"
                  />
                  <span className="w-10 text-right font-mono text-xs text-slate-700">
                    {settings.temperature.toFixed(2)}
                  </span>
                </div>
              </div>

              <div className="flex min-h-16 flex-col justify-between gap-2">
                <Label htmlFor="max_tokens" className="flex items-center gap-1.5 text-sm text-muted-foreground">
                  Максимум токенов
                  <InfoTooltip text="Максимальное количество токенов в ответе модели." />
                </Label>
                <Input
                  id="max_tokens"
                  type="number"
                  min={1}
                  max={8192}
                  value={settings.max_tokens}
                  onChange={(event) => setSettings({ max_tokens: Number(event.target.value) })}
                />
              </div>

              <div className="flex min-h-16 items-center justify-between gap-3 rounded-xl border border-border bg-slate-50/70 px-4">
                <div className="flex flex-col gap-0.5">
                  <span className="flex items-center gap-1.5 text-sm font-medium text-slate-800">
                    Только контекст
                    <InfoTooltip text="Система вернёт найденные фрагменты документов без генерации ответа языковой моделью." />
                  </span>
                  <span className="text-xs text-muted-foreground">Без ответа LLM</span>
                </div>
                <Switch
                  checked={settings.only_context}
                  onCheckedChange={(checked) => setSettings({ only_context: checked })}
                  aria-label="Вернуть только контекст"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Лента сообщений */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="thin-scrollbar min-h-0 flex-1 overflow-y-auto rounded-2xl border border-border bg-card shadow-[0_1px_12px_rgba(10,17,32,0.06)]"
      >
        {!hasMessages ? (
          <div className="flex h-full min-h-[320px] items-center justify-center p-6">
            <EmptyState
              icon={MessageSquare}
              title="Задайте вопрос по документам этой базы"
              description="Система найдёт релевантные фрагменты в загруженных документах и сформирует ответ со ссылками на источники."
            />
          </div>
        ) : (
          <div className="flex flex-col gap-5 p-4 sm:p-5">
            {messages.map((message) => {
              if (message.role === "user") {
                return (
                  <div key={message.id} className="flex justify-end">
                    <p className="max-w-[85%] rounded-2xl rounded-br-sm bg-ink-950 px-4 py-2.5 text-[13px] leading-snug font-medium whitespace-pre-wrap text-white">
                      {message.content}
                    </p>
                  </div>
                );
              }

              const sources = message.sources ?? [];
              const maxScore = sources.reduce((max, doc) => (doc.score != null && doc.score > max ? doc.score : max), 0);

              return (
                <article key={message.id} className="flex max-w-full flex-col gap-3">
                  {message.status === "pending" && (
                    <div className="rounded-xl border border-accent-100 bg-accent-50/60 px-4 py-3">
                      <p className="flex items-center gap-2 text-sm font-medium text-accent-700">
                        <span className="flex gap-1" aria-hidden="true">
                          <span className="typing-dot inline-block h-1.5 w-1.5 rounded-full bg-accent-500" />
                          <span className="typing-dot inline-block h-1.5 w-1.5 rounded-full bg-accent-500" />
                          <span className="typing-dot inline-block h-1.5 w-1.5 rounded-full bg-accent-500" />
                        </span>
                        Поиск по базе знаний…
                      </p>
                      <div className="mt-3 flex flex-col gap-2" aria-hidden="true">
                        {[92, 74, 56].map((width) => (
                          <div
                            key={width}
                            className="h-3 animate-pulse rounded-full bg-accent-100"
                            style={{ width: `${width}%` }}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {message.status === "error" && (
                    <div className="rounded-xl border border-red-200 bg-red-50/70 px-4 py-3">
                      <p className="text-sm font-medium text-red-800">
                        {message.error ?? "Не удалось получить ответ"}
                      </p>
                      <Button
                        variant="destructive-outline"
                        size="sm"
                        className="mt-2.5"
                        onClick={() => handleRetry(message)}
                        disabled={isPending}
                      >
                        <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
                        Повторить запрос
                      </Button>
                    </div>
                  )}

                  {message.status === "done" && message.content && (
                    <div className="rounded-xl border border-accent-100 bg-accent-50/50 px-4 py-3.5 sm:px-5 sm:py-4">
                      <p className="mb-2 text-[11px] font-semibold tracking-[0.14em] text-accent-700 uppercase">
                        Ответ
                      </p>
                      <Markdown className="text-sm text-slate-800">{message.content}</Markdown>
                      {message.responseTimeMs != null && (
                        <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-accent-100 pt-2.5 font-mono text-[11px] text-slate-400">
                          <span className="font-semibold tracking-wide text-slate-500 uppercase">
                            {message.responseTimeMs} мс
                          </span>
                          {sources.length > 0 && (
                            <span>
                              {sources.length} фрагмент{sources.length === 1 ? "" : sources.length < 5 ? "а" : "ов"}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {message.status === "done" && sources.length > 0 && (
                    <div>
                      <p className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold tracking-[0.14em] text-slate-500 uppercase">
                        Источники ({sources.length})
                        <InfoTooltip text="Фрагменты документов, найденные по вашему запросу. Релевантность показана относительно лучшего фрагмента выдачи." />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="ml-auto h-auto gap-1 px-1.5 py-0.5 font-sans text-[11px] font-semibold tracking-normal text-accent-700 normal-case transition-colors hover:bg-accent-50 hover:text-accent-600"
                          onClick={() =>
                            setCollapsedSources((prev) => ({
                              ...prev,
                              [message.id]: !prev[message.id],
                            }))
                          }
                          aria-expanded={!collapsedSources[message.id]}
                        >
                          {collapsedSources[message.id] ? "Показать источники" : "Свернуть источники"}
                        </Button>
                      </p>
                      {!collapsedSources[message.id] && (
                        <ul className="flex flex-col gap-2.5">
                          {sources.map((doc, sourceIndex) => (
                            <SourceCard
                              key={doc.id ?? `${message.id}-${sourceIndex}`}
                              source={doc}
                              index={sourceIndex}
                              maxScore={maxScore}
                              delayMs={sourceIndex * 80}
                            />
                          ))}
                        </ul>
                      )}
                    </div>
                  )}

                  {message.status === "done" && !message.content && sources.length === 0 && (
                    <p className="rounded-xl border border-border bg-slate-50 px-4 py-3 text-sm text-muted-foreground">
                      Ответ пуст. Уточните запрос или добавьте документы в коллекцию.
                    </p>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </div>

      {/* Форма отправки */}
      <form onSubmit={handleSubmit} className="rounded-2xl border border-border bg-card p-3 shadow-[0_1px_12px_rgba(10,17,32,0.06)] sm:p-4">
        <div className="flex items-end gap-2">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Введите вопрос…"
            rows={1}
            className="max-h-40 min-h-10 resize-none"
            aria-label="Вопрос"
            disabled={isPending}
          />
          <Button
            type="submit"
            size="icon"
            className="h-10 w-10"
            disabled={isPending || !input.trim()}
            aria-label="Отправить"
          >
            <Send className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
        <div className="mt-2 flex flex-wrap items-center justify-between gap-2 px-1">
          <p className="text-[11px] text-slate-400">
            Enter — отправить · Shift+Enter — новая строка
          </p>
          {hasMessages && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleClear}
              className="h-auto gap-1 px-1.5 py-0.5 text-[11px] font-medium text-slate-400 transition-colors hover:bg-red-50 hover:text-red-600"
            >
              <Trash2 className="h-3 w-3" aria-hidden="true" />
              Очистить диалог
            </Button>
          )}
        </div>
      </form>
    </div>
  );
};

export default CollectionChat;
