# Feature: Skills Summary Dashboard

## Goal

Enable users to visualize aggregate demand for skills and key capabilities across all job postings in the database. This feature provides market insights by displaying which technologies, languages, and soft skills are most frequently required across job descriptions, along with visual analytics showing skill distribution, seniority correlations, and regional trends. Users can identify high-demand skill combinations and make data-driven decisions about upskilling priorities.

## Acceptance Criteria

- **Skills Aggregation:** API endpoint aggregates `required_stack` and `nice_to_have` fields from all `JobExtraction` records, counts frequency, and returns sorted by demand
- **Visual Dashboard:** Frontend displays:
  - Top 20 most required skills as a pie chart with percentages.
  - Skill distribution pie/donut chart showing Required vs. Nice-to-have breakdown
  - Word cloud visualization of all skills (sized by frequency)
  - Skill heatmap correlating skills that appear together in job postings
- **Filtering Options:**
  - Filter by seniority level (Junior, Mid, Senior, Lead)
- **Responsive Design:** Dashboard is fully responsive (mobile, tablet, desktop) with proper breakpoints and touch-friendly interactions
- **Performance:** Skills summary API returns results in <200ms for up to 10,000 jobs
- **Color Scheme:** Use a cohesive, visually appealing color palette (defined in theme.ts)
- **Accessibility:** Charts have ARIA labels; colors are colorblind-friendly; proper keyboard navigation supported

## Technical Approach

### Backend (Python/FastAPI)

1. **New API Endpoint:** `GET /api/skills/summary`
   - Query parameters: `seniority_level`
   - Returns aggregated skill data with frequency counts and correlation data
   - Implements caching (Redis or in-memory) to optimize repeated queries (very important)

2. **New Service:** `/server/app/services/skills_analytics.py`
   - Function: `get_skills_summary(filters: SkillsFilter) -> SkillsSummary`
   - Function: `calculate_skill_correlations(skills_list: list[str]) -> dict`
   - Function: `get_skill_distribution(filters: SkillsFilter) -> SkillsDistribution`

3. **New Schema:** `/server/app/schemas/skills.py`
   - `SkillsFilter` — query filter parameters
   - `SkillCount` — skill name + frequency + percentage
   - `SkillsSummary` — top skills, distribution, correlations
   - `SkillsDistribution` — required vs. nice-to-have breakdown

4. **New Database Query:**
   - Aggregation query in SQLAlchemy using `func.count()` and grouping on JSON array elements
   - Optimize with indexed queries on `created_at` and `seniority_level`

### Frontend (React/TypeScript)

1. **New Page:** `/client/src/pages/SkillsSummary.tsx`
   - Layout: Header with filters + metrics cards + chart grid
   - Uses custom hooks to fetch and manage skills data

2. **New Components:**
   - `SkillsFilter` — filter panel with seniority
   - `SkillsBarChart` — horizontal bar chart (using Recharts or Chart.js)
   - `SkillsDistributionChart` — pie/donut chart for Required vs. Nice-to-have
   - `SkillsWordCloud` — word cloud visualization (using `react-d3-library` or similar)
   - `SkillsHeatmap` — correlation heatmap (using `react-heatmap-grid` or custom SVG)
   - `SkillsMetricsCard` — summary cards (total skills, top skill, avg skills per job)
   - `ExportButton` — export as JSON/CSV

3. **New Hooks:** `/client/src/hooks/useSkillsSummary.ts`
   - Fetches skills data from API
   - Handles loading, error, and retry logic
   - Manages filter state

4. **New Service:** `/client/src/services/skillsService.ts`
   - API client functions: `fetchSkillsSummary()`, `exportSkillsData()`

5. **Styling:**
   - Use TailwindCSS + custom theme colors from `/client/src/styles/theme.ts`
   - Responsive grid layout using CSS Grid for chart positioning
   - Animation for chart rendering using CSS transitions

## Edge Cases / Constraints

- **Empty Database:** If no job extractions exist, display empty state with call-to-action to add job data
- **Large Datasets:** For >100k jobs, implement pagination/sampling for heatmap to avoid performance degradation
- **Filtering Results:** If filters eliminate all data, show appropriate empty state message
- **Skill Name Normalization:** Handle duplicates (e.g., "python", "Python", "PYTHON") via case-insensitive grouping or preprocessing
- **Special Characters:** Skills with punctuation/spacing (e.g., "C++", "Node.js", "Machine Learning") must be handled correctly
- **Concurrent Filter Updates:** Debounce filter changes (300ms) to avoid excessive API calls
- **Browser Compatibility:** Charts must render correctly on IE11+, modern browsers (Chrome, Safari, Firefox)
- **Mobile Constraints:** Heatmap may be scrollable horizontally; word cloud should reflow on small screens
- **Data Staleness:** Cache API responses for 5 minutes; show cache timestamp in UI
- **Export Size Limits:** CSV export limited to top 100 skills to avoid massive files

## Files to Modify

### Server

- `server/app/routes/skills.py` (create) — Route handlers
- `server/app/services/skills_analytics.py` (create) — Business logic for aggregation
- `server/app/schemas/skills.py` (create) — Pydantic models
- `server/app/models/job.py` (modify) — May add index on `created_at` if not present
- `server/main.py` (modify) — Register new skills router

### Client

- `client/src/pages/SkillsSummary.tsx` (create) — Main page component
- `client/src/components/SkillsFilter/SkillsFilter.tsx` (create)
- `client/src/components/SkillsFilter/types.ts` (create)
- `client/src/components/SkillsFilter/index.ts` (create)
- `client/src/components/SkillsBarChart/SkillsBarChart.tsx` (create)
- `client/src/components/SkillsBarChart/index.ts` (create)
- `client/src/components/SkillsDistributionChart/SkillsDistributionChart.tsx` (create)
- `client/src/components/SkillsDistributionChart/index.ts` (create)
- `client/src/components/SkillsWordCloud/SkillsWordCloud.tsx` (create)
- `client/src/components/SkillsWordCloud/index.ts` (create)
- `client/src/components/SkillsHeatmap/SkillsHeatmap.tsx` (create)
- `client/src/components/SkillsHeatmap/index.ts` (create)
- `client/src/components/SkillsMetricsCard/SkillsMetricsCard.tsx` (create)
- `client/src/components/SkillsMetricsCard/index.ts` (create)
- `client/src/components/ExportButton/ExportButton.tsx` (create)
- `client/src/components/ExportButton/index.ts` (create)
- `client/src/hooks/useSkillsSummary.ts` (create)
- `client/src/hooks/useSkillsFilter.ts` (create)
- `client/src/services/skillsService.ts` (create)
- `client/src/services/skillsService/types.ts` (create)
- `client/src/App.tsx` (modify) — Add route to /skills-summary
- `client/src/styles/theme.ts` (modify) — Add chart color palette

### Testing

- `server/tests/test_routes/test_skills.py` (create) — Route tests
- `server/tests/test_services/test_skills_analytics.py` (create) — Service tests
- `client/src/components/SkillsBarChart/SkillsBarChart.test.tsx` (create)
- `client/src/components/SkillsDistributionChart/SkillsDistributionChart.test.tsx` (create)
- `client/src/hooks/useSkillsSummary.test.ts` (create)
- `client/src/pages/SkillsSummary.test.tsx` (create)

### Documentation

- `specs/skills-summary.md` (this file) — Feature specification

## Test Plan

### Backend Testing (pytest)

- **Unit Tests:**
  - `test_get_skills_summary_empty_database` — Returns empty state correctly
  - `test_get_skills_summary_with_data` — Aggregates skills correctly and sorts by frequency
  - `test_get_skills_summary_with_filters` — Applies seniority, location, remote_policy filters correctly
  - `test_calculate_skill_correlations` — Returns correct co-occurrence matrix
  - `test_skill_normalization` — Handles case-insensitive skill names (Python, python, PYTHON)
  - `test_api_response_format` — Validates Pydantic schema compliance
  - `test_api_performance` — Response time <200ms for 10k jobs

- **Integration Tests:**
  - `test_skills_endpoint_with_sample_data` — Full flow with seeded test jobs
  - `test_skills_export_json` — Export endpoint returns valid JSON
  - `test_skills_export_csv` — Export endpoint returns valid CSV

### Frontend Testing (Vitest + React Testing Library)

- **Component Tests:**
  - `SkillsFilter` — Filter options render; user can select and apply filters
  - `SkillsBarChart` — Chart renders with data; bars have correct heights
  - `SkillsDistributionChart` — Pie chart renders; slices are correctly proportioned
  - `SkillsWordCloud` — Word cloud renders; word sizes correlate to frequency
  - `SkillsHeatmap` — Heatmap renders; colors indicate correlation strength
  - `ExportButton` — Click triggers download; file format is correct

- **Hook Tests:**
  - `useSkillsSummary` — Fetches data on mount; handles loading/error states
  - `useSkillsFilter` — Filter state updates correctly; debounces API calls

- **Page Tests:**
  - `SkillsSummary` — Full page renders with all components
  - `SkillsSummary` with empty data — Empty state displays correctly
  - `SkillsSummary` with filters — Filtered data displays correctly

- **Manual Testing:**
  - Filter combinations (e.g., Senior + Remote + San Francisco)
  - Export as JSON and CSV; verify file contents
  - Responsive design on mobile, tablet, desktop
  - Chart interactions (hover tooltips, legend clicks)
  - Accessibility: keyboard navigation, screen reader compatibility

### Performance Testing

- Load skills endpoint with 10k, 100k, 1M job records; measure response time
- Cache invalidation: verify stale cache is refreshed after 5 minutes
- Browser profiling: verify chart rendering doesn't block main thread

### Visual Regression Testing (Optional)

- Screenshot comparison for chart renders on different screen sizes
- Color contrast verification for accessibility
