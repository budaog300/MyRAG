import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Header from "./Header";
import SidebarContent from "./SidebarContent";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const Layout = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header onMenuClick={() => setMenuOpen(true)} />

      {/* Мобильный drawer */}
      <div
        className={cn(
          "fixed inset-0 z-50 transition-opacity duration-300 lg:hidden",
          menuOpen ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"
        )}
        aria-hidden={!menuOpen}
      >
        <div
          className="absolute inset-0 bg-ink-950/50"
          onClick={() => setMenuOpen(false)}
        />
        <aside
          className={cn(
            "absolute inset-y-0 left-0 flex w-72 max-w-[85vw] flex-col border-r border-border bg-card p-4 shadow-2xl transition-transform duration-300",
            menuOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          <div className="mb-3 flex justify-end">
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              aria-label="Закрыть меню"
              onClick={() => setMenuOpen(false)}
              className="text-slate-500 hover:bg-slate-100 hover:text-slate-700"
            >
              ✕
            </Button>
          </div>
          <SidebarContent onNavigate={() => setMenuOpen(false)} />
        </aside>
      </div>

      <div className="mx-auto flex w-full max-w-7xl flex-1 gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <aside className="sticky top-[4.5rem] hidden h-[calc(100vh-6rem)] w-60 shrink-0 self-start overflow-hidden rounded-2xl border border-border bg-card p-4 shadow-[0_1px_12px_rgba(10,17,32,0.06)] lg:block">
          <SidebarContent />
        </aside>

        <main className="flex min-w-0 flex-1 flex-col gap-6" key={location.pathname}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
