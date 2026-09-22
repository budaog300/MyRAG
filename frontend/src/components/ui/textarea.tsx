import * as React from "react"

import { cn } from "@/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "flex field-sizing-content min-h-16 w-full rounded-lg border border-input bg-card px-3.5 py-2.5 text-sm text-foreground shadow-xs transition-colors duration-200 outline-none",
        "placeholder:text-slate-400 selection:bg-accent-200 selection:text-ink-950",
        "focus-visible:border-accent-500 focus-visible:ring-2 focus-visible:ring-accent-500/25",
        "aria-invalid:border-red-400 aria-invalid:ring-red-500/20",
        "disabled:cursor-not-allowed disabled:bg-muted disabled:text-muted-foreground disabled:opacity-70",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }
