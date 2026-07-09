import { useState, useEffect, useCallback } from 'react';
import { SkillsFilter } from '@/services/skillsService/types';

interface UseSkillsFilterReturn {
  filters: SkillsFilter;
  debouncedFilters: SkillsFilter;
  setSeniorityLevel: (level: string | undefined) => void;
}

export const useSkillsFilter = (): UseSkillsFilterReturn => {
  const [filters, setFilters] = useState<SkillsFilter>({});
  const [debouncedFilters, setDebouncedFilters] = useState<SkillsFilter>({});

  const setSeniorityLevel = useCallback((level: string | undefined) => {
    setFilters({ seniority_level: level });
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters(filters);
    }, 300);

    return () => clearTimeout(timer);
  }, [filters]);

  return { filters, debouncedFilters, setSeniorityLevel };
};
