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

  return (
    <div className="flex flex-col gap-3 text-xs text-muted-foreground">
      <div className="flex items-center justify-between text-[11px]">
        <div>Всего записей: {total}</div>
        <div className="flex items-center gap-2">
          <span>Размер:</span>
          <select
            className="rounded-full border border-border bg-card px-2 py-1 text-[11px] text-foreground"
            value={size}
            onChange={(event) => onSizeChange(Number(event.target.value))}
          >
            {sizes.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="flex items-center justify-between gap-2">
        <button
          className="rounded-full border border-border px-3 py-1 text-[11px] font-semibold text-muted-foreground disabled:opacity-50"
          disabled={page === 1}
          onClick={() => onPageChange(page - 1)}
        >
          Назад
        </button>
        <span>
          {page} / {pages}
        </span>
        <button
          className="rounded-full border border-border px-3 py-1 text-[11px] font-semibold text-muted-foreground disabled:opacity-50"
          disabled={page >= pages}
          onClick={() => onPageChange(page + 1)}
        >
          Далее
        </button>
      </div>
    </div>
  );
};

export default Pagination;
