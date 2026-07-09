import { SkillCorrelation } from '@/services/skillsService/types';
import styles from './SkillsHeatmap.module.css';

interface SkillsHeatmapProps {
  correlations: SkillCorrelation[];
}

export const SkillsHeatmap = ({ correlations }: SkillsHeatmapProps) => {
  if (correlations.length === 0) {
    return <div className={styles.empty}>No correlations to display</div>;
  }

  const skills = new Set<string>();
  correlations.forEach((c) => {
    skills.add(c.skill_a);
    skills.add(c.skill_b);
  });

  const skillList = Array.from(skills).sort();
  const corrMap = new Map<string, number>();
  const maxCount = Math.max(...correlations.map((c) => c.count));

  correlations.forEach((c) => {
    corrMap.set(`${c.skill_a}|${c.skill_b}`, c.count);
  });

  const getIntensity = (count: number): string => {
    const normalized = count / maxCount;
    const hue = 200;
    const saturation = 70;
    const lightness = 100 - normalized * 50;
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

  return (
    <div className={styles.container}>
      <div className={styles.scrollWrapper}>
        <table className={styles.heatmap}>
          <thead>
            <tr>
              <th className={styles.headerCell}></th>
              {skillList.map((skill) => (
                <th key={skill} className={styles.headerCell} title={skill}>
                  <div className={styles.verticalText}>{skill}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {skillList.map((skillA) => (
              <tr key={skillA}>
                <th className={styles.rowHeader} title={skillA}>
                  {skillA}
                </th>
                {skillList.map((skillB) => {
                  const pair1 = `${skillA}|${skillB}`;
                  const pair2 = `${skillB}|${skillA}`;
                  const count = corrMap.get(pair1) || corrMap.get(pair2) || 0;
                  const bgColor = count > 0 ? getIntensity(count) : '#f9fafb';

                  return (
                    <td
                      key={`${skillA}-${skillB}`}
                      className={styles.cell}
                      style={{ backgroundColor: bgColor }}
                      title={`${skillA} + ${skillB}: ${count} co-occurrences`}
                    >
                      {count > 0 && count}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div
        className={styles.legend}
        role="img"
        aria-label={`Skill correlation heatmap. Darker blue indicates stronger correlation between skills. Maximum co-occurrence count: ${maxCount}`}
      >
        <span>Darker blue = stronger correlation</span>
      </div>
    </div>
  );
};

export default SkillsHeatmap;
