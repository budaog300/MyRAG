import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface PageHeaderProps {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
  className?: string;
}

/** Заголовок страницы в визуальном языке landing (eyebrow + title + actions). */
const PageHeader = ({ eyebrow, title, description, actions, className }: PageHeaderProps) => {
  return (
    <header
      className={cn(
        "flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between",
        className
      )}
    >
      <div className="min-w-0">
        {eyebrow && (
          <p className="text-xs font-semibold tracking-[0.16em] text-accent-600 uppercase">{eyebrow}</p>
        )}
        <h2 className="mt-1.5 truncate text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          {title}
        </h2>
        {description && (
          <div className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{description}</div>
        )}
      </div>
      {actions && <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div>}
    </header>
  );
};

export default PageHeader;
