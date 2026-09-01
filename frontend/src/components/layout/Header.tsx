import { useHealth } from "@/hooks/useHealth";

const Header = () => {
  const healthQuery = useHealth();

  const status = healthQuery.data?.status;
  const healthy = status === "healthy";

  return (
    <header className="flex flex-col gap-2 border-b border-border pb-4">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.4em] text-accent">intevra group</p>
          <h1 className="text-2xl font-semibold text-foreground">RAG Ops</h1>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-sm text-muted-foreground">
            <span className={`h-2 w-2 rounded-full ${healthy ? "bg-emerald-400" : "bg-rose-500"}`} />
            <span>{healthy ? "Backend online" : "Backend offline"}</span>
          </div>
        </div>
      </div>
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        {healthQuery.isError && <span>Ошибка связи с бекендом</span>}
      </div>
    </header>
  );
};

export default Header;
