import { useCallback, type ReactNode } from 'react';
import { cn } from '../../lib/cn';

type RevealProps = {
  children: ReactNode;
  className?: string;
  delay?: number;
};

/**
 * Плавное появление при попадании в viewport (IntersectionObserver).
 * При prefers-reduced-motion анимация отключается в index.css.
 */
export function Reveal({ children, className, delay = 0 }: RevealProps) {
  const ref = useCallback((node: HTMLDivElement | null) => {
    if (!node) return;
    if (typeof IntersectionObserver === 'undefined') {
      node.classList.add('reveal-visible');
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add('reveal-visible');
            observer.disconnect();
          }
        }
      },
      { threshold: 0.12, rootMargin: '0px 0px -8% 0px' },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className={cn('reveal', className)} style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>
  );
}
