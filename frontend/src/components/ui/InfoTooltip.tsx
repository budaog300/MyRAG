import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface InfoTooltipProps {
    text: string;
}

const InfoTooltip = ({ text }: InfoTooltipProps) => {
    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <span
                        className="inline-flex h-4 w-4 shrink-0 cursor-help items-center justify-center rounded-full border border-border bg-card text-[10px] font-semibold leading-none text-muted-foreground transition-colors hover:border-accent-300 hover:text-accent-700"
                        aria-label="Подробнее"
                    >
                        ?
                    </span>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                    {text}
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
};

export default InfoTooltip;
