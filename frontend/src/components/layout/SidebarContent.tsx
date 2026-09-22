import { NavLink, useParams } from "react-router-dom";
import { Library } from "lucide-react";
import { useCollections } from "@/hooks/useCollections";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";

const SidebarContent = ({ onNavigate }: { onNavigate?: () => void }) => {
  const { data, isLoading, isError, refetch } = useCollections();
  const { collectionId } = useParams<{ collectionId: string }>();

  return (
    <div className="flex h-full flex-col">
      <div className="mb-4 flex items-center gap-2 px-2">
        <Library className="h-4 w-4 text-accent-600" aria-hidden="true" />
        <p className="text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase">
          Базы знаний
        </p>
      </div>

      <NavLink
        to="/collections"
        end
        onClick={onNavigate}
        className={({ isActive }) =>
          cn(
            "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
            isActive
              ? "bg-accent-50 text-accent-700"
              : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
          )
        }
      >
        Все коллекции
      </NavLink>

      <div className="mt-4 flex min-h-0 flex-1 flex-col gap-1 overflow-y-auto thin-scrollbar pb-2">
        {isLoading && (
          <div className="space-y-1.5 px-1">
            {[0, 1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-9 w-full rounded-lg" />
            ))}
          </div>
        )}

        {isError && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => refetch()}
            className="mx-1 w-full justify-start rounded-lg px-3 py-2 text-left text-xs font-medium text-red-700 hover:bg-red-50"
          >
            Не удалось загрузить коллекции.
            <span className="font-semibold underline"> Повторить</span>
          </Button>
        )}

        {!isLoading && !isError && data && data.length > 0 && (
          <p className="px-3 pb-1 text-[11px] font-medium tracking-wide text-slate-400 uppercase">
            {data.length} шт.
          </p>
        )}

        {!isLoading &&
          !isError &&
          data?.map((collection) => (
            <NavLink
              key={collection.id}
              to={`/collections/${collection.id}`}
              title={collection.description || collection.name}
              onClick={onNavigate}
              className={() =>
                cn(
                  "truncate rounded-lg px-3 py-2 text-sm transition-colors",
                  collectionId === collection.id
                    ? "bg-accent-50 font-semibold text-accent-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                )
              }
            >
              {collection.name}
            </NavLink>
          ))}

        {!isLoading && !isError && data?.length === 0 && (
          <p className="px-3 text-xs leading-relaxed text-slate-400">
            Баз знаний пока нет. Создайте первую на странице «Все коллекции».
          </p>
        )}
      </div>
    </div>
  );
};

export default SidebarContent;
