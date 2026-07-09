import apiClient from '@/services/apiClient';
import { SkillsSummary, SkillsFilter } from '@/services/skillsService/types';

export async function fetchSkillsSummary(
  filters: SkillsFilter
): Promise<SkillsSummary> {
  const response = await apiClient.get<{ data: SkillsSummary }>(
    '/skills/summary',
    { params: filters }
  );

  if (response.data.data) {
    return response.data.data;
  }

  throw new Error('Invalid response from skills API');
}

export function exportSkillsData(
  summary: SkillsSummary,
  format: 'json' | 'csv'
): void {
  let content: string;
  let filename: string;
  let mimeType: string;

  if (format === 'json') {
    content = JSON.stringify(summary, null, 2);
    filename = 'skills-summary.json';
    mimeType = 'application/json';
  } else {
    const headers = ['Skill', 'Count', 'Percentage (%)'];
    const rows = summary.top_skills.map((skill) => [
      `"${skill.name.replace(/"/g, '""')}"`,
      skill.count.toString(),
      skill.percentage.toFixed(2),
    ]);
    content = [headers, ...rows].map((row) => row.join(',')).join('\n');
    filename = 'skills-summary.csv';
    mimeType = 'text/csv';
  }

  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
