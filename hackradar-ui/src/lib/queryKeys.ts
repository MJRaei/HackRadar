export const queryKeys = {
  projects: {
    all: ['projects'] as const,
    list: (offset: number, limit: number) => ['projects', 'list', offset, limit] as const,
    detail: (id: string) => ['projects', id] as const,
    scores: (id: string) => ['projects', id, 'scores'] as const,
  },
  criteria: {
    all: ['criteria'] as const,
    list: () => ['criteria', 'list'] as const,
    detail: (id: string) => ['criteria', id] as const,
  },
  rankings: (criteriaSetId: string) => ['rankings', criteriaSetId] as const,
}
