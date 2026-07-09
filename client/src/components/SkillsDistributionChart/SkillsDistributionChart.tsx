import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { SkillsDistribution } from '@/services/skillsService/types';
import { theme } from '@/styles/theme';

interface SkillsDistributionChartProps {
  distribution: SkillsDistribution;
}

export const SkillsDistributionChart = ({
  distribution,
}: SkillsDistributionChartProps) => {
  const chartData = [
    { name: 'Required', value: distribution.required_count },
    { name: 'Nice-to-have', value: distribution.nice_to_have_count },
  ];

  return (
    <div
      role="img"
      aria-label={`Skills distribution. Required: ${distribution.required_count}, Nice-to-have: ${distribution.nice_to_have_count}`}
      style={{ width: '100%', height: 400 }}
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={80}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) =>
              `${name} ${(percent * 100).toFixed(0)}%`
            }
          >
            {chartData.map((_, index) => (
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

export default SkillsDistributionChart;
