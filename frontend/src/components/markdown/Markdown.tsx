import type { ComponentPropsWithoutRef, ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";

type MarkdownProps = {
  children: string;
  className?: string;
};

/* react-markdown передаёт служебный проп node — отделяем его, чтобы не попадал в DOM. */
type MdProps<T extends keyof React.JSX.IntrinsicElements> = Omit<ComponentPropsWithoutRef<T>, "node"> & {
  node?: unknown;
  children?: ReactNode;
};

const Markdown = ({ children, className }: MarkdownProps) => {
  return (
    <div className={cn("markdown-body max-w-none", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ node: _node, children: heading, ...props }: MdProps<"h1">) => (
            <h1 {...props} className="mt-5 mb-3 text-xl font-bold tracking-tight first:mt-0">{heading}</h1>
          ),
          h2: ({ node: _node, children: heading, ...props }: MdProps<"h2">) => (
            <h2 {...props} className="mt-5 mb-2.5 text-lg font-bold tracking-tight first:mt-0">{heading}</h2>
          ),
          h3: ({ node: _node, children: heading, ...props }: MdProps<"h3">) => (
            <h3 {...props} className="mt-4 mb-2 text-[15px] font-semibold first:mt-0">{heading}</h3>
          ),
          h4: ({ node: _node, children: heading, ...props }: MdProps<"h4">) => (
            <h4 {...props} className="mt-3 mb-1.5 text-sm font-semibold first:mt-0">{heading}</h4>
          ),
          a: ({ node: _node, children: link, href, ...props }: MdProps<"a">) => (
            <a {...props} href={href} target="_blank" rel="noopener noreferrer" className="font-medium text-accent-700 underline decoration-accent-300 underline-offset-2 hover:text-accent-600">{link}</a>
          ),
          ul: ({ node: _node, children: list, ...props }: MdProps<"ul">) => (
            <ul {...props} className="my-2.5 list-disc space-y-1 pl-5 marker:text-accent-500 first:mt-0 last:mb-0">{list}</ul>
          ),
          ol: ({ node: _node, children: list, ...props }: MdProps<"ol">) => (
            <ol {...props} className="my-2.5 list-decimal space-y-1 pl-5 marker:font-semibold marker:text-accent-600 first:mt-0 last:mb-0">{list}</ol>
          ),
          blockquote: ({ node: _node, children: quote, ...props }: MdProps<"blockquote">) => (
            <blockquote {...props} className="my-3 border-l-2 border-accent-400 pl-3.5 text-muted-foreground italic first:mt-0 last:mb-0">{quote}</blockquote>
          ),
          hr: ({ node: _node, ...props }: MdProps<"hr">) => (
            <hr {...props} className="my-4 border-border" />
          ),
          table: ({ node: _node, children: table, ...props }: MdProps<"table">) => (
            <div className="my-3 w-full overflow-x-auto thin-scrollbar first:mt-0 last:mb-0">
              <table {...props} className="w-full min-w-max border-collapse text-left text-[13px]">{table}</table>
            </div>
          ),
          thead: ({ node: _node, children: head, ...props }: MdProps<"thead">) => (
            <thead {...props} className="border-b border-slate-200 bg-slate-50">{head}</thead>
          ),
          th: ({ node: _node, children: cell, ...props }: MdProps<"th">) => (
            <th {...props} className="px-3 py-2 text-left text-xs font-semibold tracking-wide whitespace-nowrap text-slate-600 uppercase">{cell}</th>
          ),
          td: ({ node: _node, children: cell, ...props }: MdProps<"td">) => (
            <td {...props} className="border-b border-slate-100 px-3 py-2 align-top">{cell}</td>
          ),
          code: ({ node: _node, children: code, className: codeClassName, ...props }: MdProps<"code">) => {
            const isBlock = /language-/.test(codeClassName ?? "");
            if (isBlock) {
              return (
                <code {...props} className={cn("block overflow-x-auto thin-scrollbar rounded-lg border border-slate-200 bg-slate-50 p-3 font-mono text-xs leading-relaxed text-slate-800", codeClassName)}>
                  {code}
                </code>
              );
            }
            return (
              <code {...props} className="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-[0.85em] font-medium text-slate-800">
                {code}
              </code>
            );
          },
          pre: ({ node: _node, children: pre, ...props }: MdProps<"pre">) => (
            <pre {...props} className="my-3 first:mt-0 last:mb-0">{pre}</pre>
          ),
          p: ({ node: _node, children: paragraph, ...props }: MdProps<"p">) => (
            <p {...props} className="my-2.5 leading-relaxed first:mt-0 last:mb-0">{paragraph}</p>
          ),
          strong: ({ node: _node, children: strong, ...props }: MdProps<"span">) => (
            <strong {...props} className="font-semibold text-slate-900">{strong}</strong>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
};

export default Markdown;
