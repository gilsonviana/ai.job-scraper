import { useState, useEffect, useCallback } from 'react';
import { fetchSkillsSummary } from '@/services/skillsService';
import { SkillsSummary, SkillsFilter } from '@/services/skillsService/types';
import { ErrorDetail } from '@/services/types';

interface UseSkillsSummaryReturn {
  loading: boolean;
  error: ErrorDetail | null;
  data: SkillsSummary | null;
  retry: () => Promise<void>;
}

export const useSkillsSummary = (
  filters: SkillsFilter
): UseSkillsSummaryReturn => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ErrorDetail | null>(null);
  const [data, setData] = useState<SkillsSummary | null>(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await fetchSkillsSummary(filters);
      setData(result);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError({
          code: 'FETCH_ERROR',
          message: err.message || 'Failed to fetch skills summary',
          details: {},
        });
      }
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetch();
  }, [filters, fetch]);

  const retry = useCallback(async () => {
    await fetch();
  }, [fetch]);

  return { loading, error, data, retry };
};
