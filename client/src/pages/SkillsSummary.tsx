import { Link } from 'react-router-dom';
import SkillsFilter from '@/components/SkillsFilter';
import SkillsBarChart from '@/components/SkillsBarChart';
import SkillsDistributionChart from '@/components/SkillsDistributionChart';
import SkillsWordCloud from '@/components/SkillsWordCloud';
import SkillsHeatmap from '@/components/SkillsHeatmap';
import SkillsMetricsCard from '@/components/SkillsMetricsCard';
import ExportButton from '@/components/ExportButton';
import { useSkillsFilter } from '@/hooks/useSkillsFilter';
import { useSkillsSummary } from '@/hooks/useSkillsSummary';
import styles from './SkillsSummary.module.css';

export const SkillsSummary = () => {
  const { filters, debouncedFilters, setSeniorityLevel } = useSkillsFilter();
  const { loading, error, data, retry } = useSkillsSummary(debouncedFilters);

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loader}>Loading skills summary...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Error Loading Skills</h2>
          <p>{error.message}</p>
          <button onClick={retry} className={styles.retryButton}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>No Data</h2>
          <p>Unable to load skills summary</p>
        </div>
      </div>
    );
  }

  if (data.total_jobs === 0) {
    return (
      <div className={styles.container}>
        <header className={styles.header}>
          <h1>Skills Summary Dashboard</h1>
        </header>
        <div className={styles.emptyState}>
          <h2>No Job Data Available</h2>
          <p>
            Start by adding job postings to see skills insights and trends.
          </p>
          <Link to="/" className={styles.ctaButton}>
            Add Job Postings
          </Link>
        </div>
      </div>
    );
  }

  const hasFilters = filters.seniority_level !== undefined;
  const hasResults = data.top_skills.length > 0;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Skills Summary Dashboard</h1>
        <p className={styles.subtitle}>
          Market insights from {data.total_jobs} job postings
        </p>
      </header>

      <div className={styles.controls}>
        <SkillsFilter
          value={filters.seniority_level}
          onChange={setSeniorityLevel}
        />
        {data && <ExportButton summary={data} />}
      </div>

      {hasFilters && !hasResults ? (
        <div className={styles.noResults}>
          <p>No skills found for the selected filters.</p>
        </div>
      ) : (
        <>
          {data && <SkillsMetricsCard summary={data} />}

          <div className={styles.chartsGrid}>
            <section className={styles.chartSection}>
              <h2>Top 20 Skills</h2>
              <SkillsBarChart data={data.top_skills} />
            </section>

            <section className={styles.chartSection}>
              <h2>Required vs Nice-to-Have</h2>
              <SkillsDistributionChart distribution={data.distribution} />
            </section>

            <section className={`${styles.chartSection} ${styles.fullWidth}`}>
              <h2>Skill Frequency Cloud</h2>
              <SkillsWordCloud data={data.top_skills} />
            </section>

            <section className={`${styles.chartSection} ${styles.fullWidth}`}>
              <h2>Skill Correlations</h2>
              <SkillsHeatmap correlations={data.correlations} />
            </section>
          </div>

          <footer className={styles.footer}>
            <p className={styles.cacheInfo}>
              Data cached at: {new Date(data.cached_at).toLocaleString()}
            </p>
          </footer>
        </>
      )}
    </div>
  );
};

export default SkillsSummary;
