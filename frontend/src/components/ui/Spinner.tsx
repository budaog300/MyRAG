import { cn } from "@/lib/utils"

const Spinner = ({ className }: { className?: string }) => (
  <div className={cn("flex items-center justify-center", className)} role="status" aria-label="Загрузка">
    <div className="h-6 w-6 animate-spin rounded-full border-[3px] border-accent-500 border-t-transparent" />
  </div>
);

export default Spinner;
