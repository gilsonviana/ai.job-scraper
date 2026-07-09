import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import SkillsSummary from './SkillsSummary';
import * as skillsHook from '@/hooks/useSkillsSummary';
import { SkillsSummary as SkillsSummaryType } from '@/services/skillsService/types';

vi.mock('@/hooks/useSkillsSummary');

const mockSummary: SkillsSummaryType = {
  top_skills: [
    { name: 'Python', count: 50, percentage: 25.0 },
    { name: 'JavaScript', count: 40, percentage: 20.0 },
  ],
  distribution: { required_count: 100, nice_to_have_count: 50 },
  correlations: [],
  total_jobs: 10,
  cached_at: new Date().toISOString(),
};

const renderPage = () => {
  return render(
    <BrowserRouter>
      <SkillsSummary />
    </BrowserRouter>
  );
};

describe('SkillsSummary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    vi.mocked(skillsHook.useSkillsSummary).mockReturnValue({
      loading: true,
      error: null,
      data: null,
      retry: vi.fn(),
    });

    renderPage();
    expect(screen.getByText(/Loading skills summary/i)).toBeInTheDocument();
  });

  it('renders dashboard with data', () => {
    vi.mocked(skillsHook.useSkillsSummary).mockReturnValue({
      loading: false,
      error: null,
      data: mockSummary,
      retry: vi.fn(),
    });

    renderPage();

    expect(screen.getByText('Skills Summary Dashboard')).toBeInTheDocument();
    expect(screen.getByText(/10 job postings/i)).toBeInTheDocument();
  });

  it('renders empty state when no jobs', () => {
    vi.mocked(skillsHook.useSkillsSummary).mockReturnValue({
      loading: false,
      error: null,
      data: {
        ...mockSummary,
        total_jobs: 0,
        top_skills: [],
      },
      retry: vi.fn(),
    });

    renderPage();

    expect(screen.getByText(/No Job Data Available/i)).toBeInTheDocument();
  });

  it('shows error state', () => {
    const mockError = { code: 'ERROR', message: 'Test error', details: {} };
    vi.mocked(skillsHook.useSkillsSummary).mockReturnValue({
      loading: false,
      error: mockError,
      data: null,
      retry: vi.fn(),
    });

    renderPage();

    expect(screen.getByText(/Error Loading Skills/i)).toBeInTheDocument();
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });
});
