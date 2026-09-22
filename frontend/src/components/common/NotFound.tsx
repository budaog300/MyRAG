import { Link } from "react-router-dom";
import { buttonVariants } from "@/components/ui/button";

const NotFound = () => (
  <div className="grid min-h-[50vh] place-items-center p-6 text-center">
    <div className="space-y-4">
      <p className="text-xs font-semibold tracking-[0.2em] text-accent-600 uppercase">404</p>
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Страница не найдена</h1>
      <p className="text-muted-foreground">
        Вы перешли на несуществующий маршрут или страница была удалена.
      </p>
      <Link to="/collections" className={buttonVariants({ className: "mt-2" })}>
        Вернуться к коллекциям
      </Link>
    </div>
  </div>
);

export default NotFound;
