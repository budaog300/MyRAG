import { Outlet, Link, useLocation } from "react-router-dom";
import Header from "./Header";

const navLinks = [
  { path: "/collections", label: "Коллекции" },
];

const Layout = () => {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-6 lg:px-0">
        <Header />
        <div className="flex flex-1 gap-6">
          <aside className="hidden w-64 flex-col gap-3 rounded-2xl border border-border bg-card p-4 shadow-xl lg:flex">
            <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Навигация</p>
            <nav className="flex flex-col gap-2">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`rounded-xl px-3 py-2 text-sm font-semibold transition ${
                    location.pathname.startsWith(link.path)
                      ? "bg-secondary text-secondary-foreground"
                      : "text-muted-foreground hover:bg-border"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </aside>
          <main className="flex flex-1 flex-col gap-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};

export default Layout;
