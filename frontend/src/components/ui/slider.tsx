import * as React from "react"
import { Slider as SliderPrimitive } from "radix-ui"

import { cn } from "@/lib/utils"

function Slider({ className, ...props }: React.ComponentProps<typeof SliderPrimitive.Root>) {
  return (
    <SliderPrimitive.Root
      data-slot="slider"
      className={cn(
        "relative flex w-full touch-none select-none items-center data-[disabled]:opacity-50",
        className
      )}
      {...props}
    >
      <SliderPrimitive.Track
        data-slot="slider-track"
        className="relative h-1.5 w-full grow overflow-hidden rounded-full bg-slate-200"
      >
        <SliderPrimitive.Range
          data-slot="slider-range"
          className="absolute h-full bg-accent-500"
        />
      </SliderPrimitive.Track>
      <SliderPrimitive.Thumb
        data-slot="slider-thumb"
        className={cn(
          "block size-4 shrink-0 rounded-full border-2 border-accent-500 bg-white shadow-sm transition-colors",
          "hover:ring-4 hover:ring-accent-500/15",
          "focus-visible:ring-4 focus-visible:ring-accent-500/25 focus-visible:outline-none",
          "disabled:pointer-events-none"
        )}
      />
    </SliderPrimitive.Root>
  )
}

export { Slider }
