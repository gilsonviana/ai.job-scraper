import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { SkillCount } from '@/services/skillsService/types';
import { theme } from '@/styles/theme';

interface SkillsBarChartProps {
  data: SkillCount[];
}

export const SkillsBarChart = ({ data }: SkillsBarChartProps) => {
  const chartData = data.map((skill) => ({
    name: skill.name,
    value: skill.count,
  }));

  return (
    <div
      role="img"
      aria-label={`Top 20 skills by frequency. ${data.map((s) => `${s.name}: ${s.count}`).join(', ')}`}
      style={{ width: '100%', height: 400 }}
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) =>
              `${name} ${(percent * 100).toFixed(0)}%`
            }
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={theme.chartColors[index % theme.chartColors.length]}
              />
            ))}
          </Pie>
          <Tooltip formatter={(value) => value.toString()} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SkillsBarChart;
