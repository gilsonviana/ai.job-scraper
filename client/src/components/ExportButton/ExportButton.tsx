import { Menu } from '@headlessui/react';
import { SkillsSummary } from '@/services/skillsService/types';
import { exportSkillsData } from '@/services/skillsService';
import styles from './ExportButton.module.css';

interface ExportButtonProps {
  summary: SkillsSummary;
}

export const ExportButton = ({ summary }: ExportButtonProps) => {
  const handleExport = (format: 'json' | 'csv') => {
    exportSkillsData(summary, format);
  };

  return (
    <Menu as="div" className={styles.container}>
      <Menu.Button className={styles.button}>
        Export
      </Menu.Button>
      <Menu.Items className={styles.items}>
        <Menu.Item>
          {({ active }) => (
            <button
              className={`${styles.item} ${active ? styles.itemActive : ''}`}
              onClick={() => handleExport('json')}
            >
              Export as JSON
            </button>
          )}
        </Menu.Item>
        <Menu.Item>
          {({ active }) => (
            <button
              className={`${styles.item} ${active ? styles.itemActive : ''}`}
              onClick={() => handleExport('csv')}
            >
              Export as CSV
            </button>
          )}
        </Menu.Item>
      </Menu.Items>
    </Menu>
  );
};

export default ExportButton;
