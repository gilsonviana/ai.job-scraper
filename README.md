# Job Scraper

AI-powered tool to extract structured information from job descriptions (HTML/PDF). Built with Python/FastAPI backend and React/TypeScript frontend.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ / pnpm 8+

### Backend Setup

```bash
cd server
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python main.py
```

Server runs on `http://localhost:8000`

### Seed Test Data (Optional)

Populate the database with 220 test job records from the fixture CSV:

```bash
cd server
python scripts/seed_jobs.py
```

This parses job titles, salaries, tech stacks, and responsibilities into the database.

### Frontend Setup

```bash
cd client
pnpm install
pnpm dev
```

Client runs on `http://localhost:5173`

### Environment

Copy `.env.example` to `.env` in both server and client directories and update as needed.

```bash
cp server/.env.example server/.env
cp client/.env.example client/.env
```

## Project Structure

```
├── CLAUDE.md              # Project constitution & conventions
├── README.md              # This file
├── pnpm-workspace.yaml    # Monorepo config
├── specs/                 # API, architecture, data model specs
├── server/                # FastAPI backend
│   ├── app/
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic validation models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic (NLP, extraction)
│   │   ├── utils/         # Helpers (PDF parsing, etc)
│   │   ├── config.py      # Settings
│   │   └── database.py    # DB connection
│   ├── scripts/           # Utility scripts (seeding, etc)
│   ├── fixtures/          # Test data (CSV files)
│   ├── tests/             # pytest test suite
│   ├── main.py            # FastAPI app entry point
│   └── requirements.txt    # Python dependencies
└── client/                # React frontend
    ├── src/
    │   ├── components/    # Headless UI components
    │   ├── pages/         # Page layouts
    │   ├── hooks/         # Custom React hooks
    │   ├── services/      # API client & services
    │   ├── styles/        # TailwindCSS & theme
    │   ├── utils/         # Helper functions
    │   ├── App.tsx        # Root component
    │   ├── main.tsx       # Entry point
    │   └── index.html     # HTML template
    ├── package.json       # Dependencies & scripts
    ├── vite.config.ts     # Build config
    ├── vitest.config.ts   # Test config
    └── tsconfig.json      # TypeScript config
```

## Development Workflow

### Running Tests

**Server:**
```bash
cd server
pytest --cov=app tests/
```

**Client:**
```bash
cd client
pnpm test --coverage
```

### Code Quality

**Server:**
```bash
black . && isort .
```

**Client:**
```bash
pnpm lint
pnpm format
pnpm type-check
```

## Key Decisions

See [CLAUDE.md](./CLAUDE.md) for:
- Architecture & core rules
- Code conventions
- Security & validation
- Testing requirements
- Non-negotiables

## API Documentation

See [specs/api.md](./specs/api.md) for endpoint specifications.

## Contributing

Follow conventions in [CLAUDE.md](./CLAUDE.md) before committing:

- [ ] Tests pass with coverage targets met
- [ ] Code formatted & linted
- [ ] TypeScript strict mode passes
- [ ] Specifications updated if behavior changed

## License

TBD
