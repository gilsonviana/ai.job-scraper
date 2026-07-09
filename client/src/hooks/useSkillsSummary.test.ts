import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useSkillsSummary } from './useSkillsSummary';
import * as skillsService from '@/services/skillsService';
import { SkillsSummary } from '@/services/skillsService/types';

vi.mock('@/services/skillsService');

const mockSummary: SkillsSummary = {
  top_skills: [
    { name: 'Python', count: 50, percentage: 25.0 },
    { name: 'JavaScript', count: 40, percentage: 20.0 },
  ],
  distribution: { required_count: 100, nice_to_have_count: 50 },
  correlations: [],
  total_jobs: 10,
  cached_at: new Date().toISOString(),
};

describe('useSkillsSummary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns expected shape', () => {
    vi.mocked(skillsService.fetchSkillsSummary).mockResolvedValue(mockSummary);

    const { result } = renderHook(() => useSkillsSummary({}));

    expect(result.current).toHaveProperty('loading');
    expect(result.current).toHaveProperty('error');
    expect(result.current).toHaveProperty('data');
    expect(result.current).toHaveProperty('retry');
  });

  it('calls fetchSkillsSummary', () => {
    vi.mocked(skillsService.fetchSkillsSummary).mockResolvedValue(mockSummary);

    renderHook(() => useSkillsSummary({}));

    expect(skillsService.fetchSkillsSummary).toHaveBeenCalled();
  });

  it('calls fetchSkillsSummary with filters', () => {
    vi.mocked(skillsService.fetchSkillsSummary).mockResolvedValue(mockSummary);

    renderHook(() => useSkillsSummary({ seniority_level: 'Senior' }));

    expect(skillsService.fetchSkillsSummary).toHaveBeenCalledWith({
      seniority_level: 'Senior',
    });
  });
});
