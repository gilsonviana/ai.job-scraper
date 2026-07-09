import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import SkillsDistributionChart from './SkillsDistributionChart';
import { SkillsDistribution } from '@/services/skillsService/types';

describe('SkillsDistributionChart', () => {
  it('renders distribution chart', () => {
    const distribution: SkillsDistribution = {
      required_count: 100,
      nice_to_have_count: 50,
    };

    render(<SkillsDistributionChart distribution={distribution} />);

    const container = screen.getByRole('img');
    expect(container).toBeInTheDocument();
  });

  it('handles zero counts', () => {
    const distribution: SkillsDistribution = {
      required_count: 0,
      nice_to_have_count: 0,
    };

    render(<SkillsDistributionChart distribution={distribution} />);

    const container = screen.getByRole('img');
    expect(container).toBeInTheDocument();
  });
});
