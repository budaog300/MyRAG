import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger, } from "@/components/ui/tooltip";


interface InfoTooltipProps {
    text: string;
}

const InfoTooltip = ({ text }: InfoTooltipProps) => {
    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <span className="inline-flex h-4 w-4 shrink-0 cursor-help items-center justify-center rounded-full border border-border text-[10px] font-semibold leading-none text-muted-foreground"
                        aria-label="Подробнее"
                    > ?
                    </span>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs bg-black text-white">
                    {text}
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
};

export default InfoTooltip;