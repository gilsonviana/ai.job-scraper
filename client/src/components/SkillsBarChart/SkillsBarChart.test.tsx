import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import SkillsBarChart from './SkillsBarChart';
import { SkillCount } from '@/services/skillsService/types';

describe('SkillsBarChart', () => {
  it('renders pie chart with data', () => {
    const data: SkillCount[] = [
      { name: 'Python', count: 50, percentage: 25.0 },
      { name: 'JavaScript', count: 40, percentage: 20.0 },
    ];

    render(<SkillsBarChart data={data} />);

    const container = screen.getByRole('img');
    expect(container).toBeInTheDocument();
  });

  it('renders empty state when data is empty', () => {
    const data: SkillCount[] = [];
    render(<SkillsBarChart data={data} />);

    const container = screen.getByRole('img');
    expect(container).toBeInTheDocument();
  });
});
