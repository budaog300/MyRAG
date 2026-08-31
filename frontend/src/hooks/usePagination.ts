import { useMemo, useState } from "react";

export interface PaginationState {
  page: number;
  size: number;
}

interface UsePaginationOptions {
  initialPage?: number;
  initialSize?: number;
}

export const usePagination = ({
  initialPage = 1,
  initialSize = 10,
}: UsePaginationOptions = {}) => {
  const [page, setPage] = useState(initialPage);
  const [size, setSize] = useState(initialSize);

  const pagination = useMemo(() => ({ page, size }), [page, size]);

  const goNext = () => setPage((prev) => prev + 1);
  const goPrev = () => setPage((prev) => Math.max(1, prev - 1));
  const setPageDirect = (target: number) => setPage(Math.max(1, target));

  const setSizeDirect = (target: number) => {
    setSize(target);
    setPage(1);
  };

  return {
    pagination,
    goNext,
    goPrev,
    setPage: setPageDirect,
    setSize: setSizeDirect,
  };
};
