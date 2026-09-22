import { demoScenarios } from '../data/demo';
import type { DemoScenario } from '../types/demo';

function normalize(value: string): string {
  return value.toLowerCase().replace(/ё/g, 'е').replace(/[^a-zа-м0-9\s]/gi, ' ');
}

/**
 * Локальный «поиск» по подготовленным демо-сценариям:
 * выбирает сценарий с наибольшим пересечением ключевых слов. Реальных запросов нет.
 */
export function matchDemoScenario(input: string): DemoScenario | undefined {
  const query = normalize(input);
  if (query.trim().length === 0) return undefined;

  let best: { scenario: DemoScenario; score: number } | undefined;

  for (const scenario of demoScenarios) {
    const haystack = normalize(`${scenario.question} ${scenario.keywords.join(' ')}`);
    const score = scenario.keywords.reduce(
      (acc, keyword) => acc + (haystack.includes(normalize(keyword)) ? 1 : 0),
      0,
    );
    if (score > 0 && (!best || score > best.score)) {
      best = { scenario, score };
    }
  }

  if (!best) {
    const queryTokens = query.split(/\s+/).filter((token) => token.length > 3);
    for (const scenario of demoScenarios) {
      const haystack = normalize(scenario.question);
      const score = queryTokens.filter((token) => haystack.includes(token)).length;
      if (score > 0 && (!best || score > best.score)) {
        best = { scenario, score };
      }
    }
  }

  return best?.scenario;
}
