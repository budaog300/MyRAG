import { useHealth } from "@/hooks/useHealth";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  onMenuClick?: () => void;
}

const Header = ({ onMenuClick }: HeaderProps) => {
  const healthQuery = useHealth();

  const status = healthQuery.data?.status;
  const healthy = status === "healthy";
  const isChecking = healthQuery.isPending;

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/85 backdrop-blur-md">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex min-w-0 items-center gap-3">
          {onMenuClick && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={onMenuClick}
              aria-label="Открыть меню"
              className="shrink-0 text-slate-700 transition-colors hover:bg-slate-100 lg:hidden"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
                <path d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </Button>
          )}
          <div className="min-w-0">
            <p className="text-[10px] font-semibold tracking-[0.2em] text-accent-600 uppercase">
              INTEVRUM Group
            </p>
            <h1 className="truncate text-lg font-bold leading-tight tracking-tight text-slate-900">
              RAG Workspace
            </h1>
          </div>
        </div>

        <div
          className="flex shrink-0 items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold"
          aria-live="polite"
          title="Состояние backend-сервисов"
        >
          {isChecking ? (
            <>
              <span className="h-2 w-2 rounded-full bg-slate-300 pulse-dot" aria-hidden="true" />
              <span className="text-muted-foreground">Проверка сервисов…</span>
            </>
          ) : healthy ? (
            <>
              <span className="h-2 w-2 rounded-full bg-accent-500 pulse-dot" aria-hidden="true" />
              <span className="text-accent-700">Сервисы работают</span>
            </>
          ) : (
            <>
              <span className="h-2 w-2 rounded-full bg-red-500" aria-hidden="true" />
              <span className="text-red-700">Сервисы недоступны</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
