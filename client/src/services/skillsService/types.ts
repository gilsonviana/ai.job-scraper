export interface SkillCount {
  name: string;
  count: number;
  percentage: number;
}

export interface SkillsDistribution {
  required_count: number;
  nice_to_have_count: number;
}

export interface SkillCorrelation {
  skill_a: string;
  skill_b: string;
  count: number;
}

export interface SkillsSummary {
  top_skills: SkillCount[];
  distribution: SkillsDistribution;
  correlations: SkillCorrelation[];
  total_jobs: number;
  cached_at: string;
}

export interface SkillsFilter {
  seniority_level?: string;
}
