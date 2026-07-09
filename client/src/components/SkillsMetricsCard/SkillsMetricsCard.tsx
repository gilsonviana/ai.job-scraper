import { SkillsSummary } from '@/services/skillsService/types';
import styles from './SkillsMetricsCard.module.css';

interface SkillsMetricsCardProps {
  summary: SkillsSummary;
}

export const SkillsMetricsCard = ({ summary }: SkillsMetricsCardProps) => {
  const totalSkills = summary.top_skills.length;
  const topSkill = summary.top_skills[0];
  const totalMentions =
    summary.distribution.required_count +
    summary.distribution.nice_to_have_count;
  const avgSkillsPerJob =
    summary.total_jobs > 0
      ? (totalMentions / summary.total_jobs).toFixed(1)
      : '0';

  return (
    <div className={styles.grid}>
      <div className={styles.card}>
        <div className={styles.value}>{totalSkills}</div>
        <div className={styles.label}>Unique Skills</div>
      </div>
      <div className={styles.card}>
        <div className={styles.value}>{topSkill?.name || 'N/A'}</div>
        <div className={styles.label}>Most Demanded Skill</div>
      </div>
      <div className={styles.card}>
        <div className={styles.value}>{topSkill?.count || 0}</div>
        <div className={styles.label}>
          Mentions ({topSkill?.percentage.toFixed(1) || 0}%)
        </div>
      </div>
      <div className={styles.card}>
        <div className={styles.value}>{avgSkillsPerJob}</div>
        <div className={styles.label}>Avg Skills Per Job</div>
      </div>
    </div>
  );
};

export default SkillsMetricsCard;
