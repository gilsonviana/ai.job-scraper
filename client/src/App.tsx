import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from '@/pages/HomePage';
import SkillsSummary from '@/pages/SkillsSummary';
import styles from './App.module.css';

function App() {
  return (
    <BrowserRouter>
      <div className={styles.appContainer}>
        <nav className={styles.nav}>
          <div className={styles.navContent}>
            <h1 className={styles.logo}>Job Scraper</h1>
            <div className={styles.navLinks}>
              <a href="/" className={styles.navLink}>
                Home
              </a>
              <a href="/skills-summary" className={styles.navLink}>
                Skills Summary
              </a>
            </div>
          </div>
        </nav>
        <main className={styles.main}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/skills-summary" element={<SkillsSummary />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
