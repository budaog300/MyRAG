export type DemoSource = {
  id: string;
  document: string;
  type: string;
  location: string;
  relevance: number;
  snippet: string;
};

export type DemoScenario = {
  id: string;
  question: string;
  keywords: string[];
  answer: string[];
  sources: DemoSource[];
  meta: {
    processedDocuments: number;
    matchedFragments: number;
    method: string;
  };
};

export type DemoPhase = 'idle' | 'searching' | 'sources' | 'answer';
