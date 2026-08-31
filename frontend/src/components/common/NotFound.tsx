import { Link } from "react-router-dom";

const NotFound = () => (
  <div className="grid h-full place-items-center p-6 text-center">
    <div className="space-y-4">
      <p className="text-xs uppercase tracking-[0.4em] text-accent">404</p>
      <h1 className="text-3xl font-semibold text-foreground">Страница не найдена</h1>
      <p className="text-muted-foreground">Вы попали на несуществующий маршрут.</p>
      <Link to="/collections" className="text-sm font-semibold text-primary">
        Вернуться к коллекциям
      </Link>
    </div>
  </div>
);

export default NotFound;
