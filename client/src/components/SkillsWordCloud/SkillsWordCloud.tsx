import { SkillCount } from '@/services/skillsService/types';
import { theme } from '@/styles/theme';
import styles from './SkillsWordCloud.module.css';

interface SkillsWordCloudProps {
  data: SkillCount[];
}

export const SkillsWordCloud = ({ data }: SkillsWordCloudProps) => {
  if (data.length === 0) {
    return <div className={styles.empty}>No skills to display</div>;
  }

  const counts = data.map((s) => s.count);
  const minCount = Math.min(...counts);
  const maxCount = Math.max(...counts);

  const minSize = 12;
  const maxSize = 32;

  const scale = (count: number) => {
    if (maxCount === minCount) return (minSize + maxSize) / 2;
    return minSize + ((count - minCount) / (maxCount - minCount)) * (maxSize - minSize);
  };

  return (
    <div
      className={styles.container}
      role="img"
      aria-label={`Word cloud of skills. Larger words indicate higher frequency. ${data.map((s) => `${s.name}: ${s.count}`).join(', ')}`}
    >
      {data.map((skill, index) => (
        <span
          key={skill.name}
          className={styles.word}
          style={{
            fontSize: `${scale(skill.count)}px`,
            color: theme.chartColors[index % theme.chartColors.length],
          }}
          title={`${skill.name}: ${skill.count} mentions (${skill.percentage.toFixed(1)}%)`}
        >
          {skill.name}
        </span>
      ))}
    </div>
  );
};

export default SkillsWordCloud;
