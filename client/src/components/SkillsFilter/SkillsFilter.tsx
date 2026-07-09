import { Listbox } from '@headlessui/react';
import styles from './SkillsFilter.module.css';

interface SkillsFilterProps {
  value: string | undefined;
  onChange: (value: string | undefined) => void;
}

const SENIORITY_LEVELS = [
  { value: undefined, label: 'All Levels' },
  { value: 'Junior', label: 'Junior' },
  { value: 'Mid', label: 'Mid-Level' },
  { value: 'Senior', label: 'Senior' },
  { value: 'Lead', label: 'Lead' },
];

export const SkillsFilter = ({ value, onChange }: SkillsFilterProps) => {
  return (
    <div className={styles.container}>
      <label htmlFor="seniority-filter" className={styles.label}>
        Filter by Seniority
      </label>
      <Listbox value={value} onChange={onChange}>
        <Listbox.Button
          id="seniority-filter"
          className={styles.button}
        >
          {SENIORITY_LEVELS.find((l) => l.value === value)?.label ||
            'All Levels'}
        </Listbox.Button>
        <Listbox.Options className={styles.options}>
          {SENIORITY_LEVELS.map((level) => (
            <Listbox.Option key={level.value || 'all'} value={level.value}>
              {({ selected }) => (
                <div
                  className={`${styles.option} ${
                    selected ? styles.selected : ''
                  }`}
                >
                  {level.label}
                </div>
              )}
            </Listbox.Option>
          ))}
        </Listbox.Options>
      </Listbox>
    </div>
  );
};

export default SkillsFilter;
