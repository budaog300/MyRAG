import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface PaginationProps {
  page: number;
  size: number;
  total: number;
  onPageChange: (page: number) => void;
  onSizeChange: (size: number) => void;
}

const sizes = [5, 10, 20, 50];

const Pagination = ({ page, size, total, onPageChange, onSizeChange }: PaginationProps) => {
  const pages = Math.max(1, Math.ceil(total / size));

  if (total === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-3 border-t border-border px-1 pt-4 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-wrap items-center gap-4">
        <span>
          Всего записей: <span className="font-semibold text-slate-700">{total}</span>
        </span>
        <div className="flex items-center gap-2">
          <span>На странице:</span>
          <Select value={String(size)} onValueChange={(value) => onSizeChange(Number(value))}>
            <SelectTrigger size="sm" className="h-8 w-16 text-xs" aria-label="Количество записей на странице">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {sizes.map((option) => (
                <SelectItem key={option} value={String(option)}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          aria-label="Предыдущая страница"
        >
          <ChevronLeft className="h-3.5 w-3.5" aria-hidden="true" />
          Назад
        </Button>
        <span className="font-mono text-xs whitespace-nowrap">
          {page} / {pages}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={page >= pages}
          onClick={() => onPageChange(page + 1)}
          aria-label="Следующая страница"
        >
          Далее
          <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
        </Button>
      </div>
    </div>
  );
};

export default Pagination;
