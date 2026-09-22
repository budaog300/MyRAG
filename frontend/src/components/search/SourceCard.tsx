import { useState } from "react";
import { ChevronDown, FileText } from "lucide-react";
import type { SearchDocument } from "@/types/search";
import { cn } from "@/lib/utils";
import { getBaseName, getFileExtensionLabel } from "@/lib/fileValidation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Markdown from "@/components/markdown/Markdown";

interface SourceCardProps {
  source: SearchDocument;
  index: number;
  maxScore: number;
  delayMs?: number;
}

/** Карточка найденного фрагмента (адаптация SourceCard из landing под реальные данные backend). */
const SourceCard = ({ source, index, maxScore, delayMs = 0 }: SourceCardProps) => {
  const [expanded, setExpanded] = useState(false);

  const documentName = getBaseName(source.source) ?? "Источник";
  const typeLabel = getFileExtensionLabel(documentName);

  // score — это RRF-score (ранговый). Показываем относительную релевантность
  // по сравнению с лучшим фрагментом выдачи.
  const score = source.score;
  const percent =
    score != null && maxScore > 0 ? Math.max(2, Math.round((score / maxScore) * 100)) : null;

  return (
    <li
      className="demo-in rounded-xl border border-slate-200 bg-card p-4 transition-colors duration-200 hover:border-accent-200"
      style={{ animationDelay: `${delayMs}ms` }}
    >
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-accent-50 text-accent-600">
          <FileText className="h-4 w-4" aria-hidden="true" />
        </span>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
            <p className="min-w-0 truncate text-[13px] font-semibold text-slate-900">
              <span className="mr-1.5 text-accent-600">[{index + 1}]</span>
              {documentName}
            </p>
            <span className="flex shrink-0 items-center gap-1.5">
              {typeLabel && (
                <Badge variant="secondary" className="text-[10px]">
                  {typeLabel}
                </Badge>
              )}
            </span>
          </div>

          {percent != null && (
            <div className="mt-2 flex items-center gap-2">
              <div
                className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100"
                role="img"
                aria-label={`Относительная релевантность фрагмента: ${percent} из 100`}
              >
                <div
                  className={cn(
                    "h-full rounded-full transition-[width] duration-700",
                    percent >= 85
                      ? "bg-accent-500"
                      : percent >= 65
                        ? "bg-accent-400"
                        : "bg-accent-300"
                  )}
                  style={{ width: `${percent}%` }}
                />
              </div>
              <span className="w-10 shrink-0 text-right font-mono text-[11px] text-slate-400">
                {percent}%
              </span>
            </div>
          )}

          <div
            className={cn(
              "mt-2.5 text-[13px] leading-relaxed text-slate-600",
              !expanded && "line-clamp-3"
            )}
          >
            {expanded ? (
              <Markdown>{source.content}</Markdown>
            ) : (
              <p className="whitespace-pre-wrap">{source.content}</p>
            )}
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-slate-100 pt-2.5 text-[11px] text-slate-400">
            <Button
              type="button"
              variant="link"
              size="sm"
              onClick={() => setExpanded((prev) => !prev)}
              className="h-auto gap-1 p-0 text-[11px] font-semibold text-accent-700 transition-colors hover:text-accent-600"
              aria-expanded={expanded}
            >
              {expanded ? "Свернуть" : "Показать полностью"}
              <ChevronDown
                className={cn("h-3.5 w-3.5 transition-transform duration-300", expanded && "rotate-180")}
                aria-hidden="true"
              />
            </Button>
            {score != null && (
              <span className="font-mono">
                score: {score.toFixed(4)}
              </span>
            )}
          </div>
        </div>
      </div>
    </li>
  );
};

export default SourceCard;
