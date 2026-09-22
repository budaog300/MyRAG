import { useEffect, useState } from 'react';

/**
 * Определяет активную секцию для подсветки навигации
 * по самой верхней пересекающейся области под header.
 */
export function useActiveSection(ids: readonly string[]): string | undefined {
  const [active, setActive] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (typeof IntersectionObserver === 'undefined') return;

    const visible = new Map<string, number>();

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          const id = entry.target.id;
          if (entry.isIntersecting) visible.set(id, entry.intersectionRatio);
          else visible.delete(id);
        }
        let bestId: string | undefined;
        let bestRatio = 0;
        for (const [id, ratio] of visible) {
          if (ratio >= bestRatio) {
            bestId = id;
            bestRatio = ratio;
          }
        }
        setActive(bestId);
      },
      { rootMargin: '-96px 0px -55% 0px', threshold: [0.05, 0.25, 0.5, 0.75, 1] },
    );

    for (const id of ids) {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    }

    return () => observer.disconnect();
  }, [ids]);

  return active;
}
