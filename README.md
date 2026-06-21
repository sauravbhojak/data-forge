<div align="center">
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Python-Dark.svg" height="40" alt="Python logo"  />
  <img width="12" />
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/FastAPI.svg" height="40" alt="FastAPI logo"  />
  <img width="12" />
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/React-Dark.svg" height="40" alt="React logo"  />
  <img width="12" />
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/TypeScript.svg" height="40" alt="TypeScript logo"  />
  <img width="12" />
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/TailwindCSS-Dark.svg" height="40" alt="TailwindCSS logo"  />
</div>

<h1 align="center">DataForge</h1>
<h3 align="center">Smart Test Data Generation Platform</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active_Development-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" />
</p>

---

**DataForge** is a production-grade, full-stack SaaS platform that generates realistic test datasets for developers, QA engineers, data engineers, and analysts. Generate up to **1,000,000 rows** in CSV, JSON, SQL, and Excel with blazing-fast streaming exports.

---

## 🚧 Status: Currently Working On
> **Note:** I am currently actively working on this project! My immediate focus includes:
> - **Scalability Improvements:** Optimizing server-side generation to handle multi-million row datasets even faster.
> - **New Data Types:** Adding specialized generators for financial, healthcare, and IoT sectors.
> - **Cloud Deployment:** Refining deployment configurations for Vercel and scalable backend infrastructure.
> - **UX Polish:** Enhancing data preview controls and user onboarding flows.

---

## ✨ Features

### 🎯 Pre-Built Templates
| Template | Fields | Use Case |
|---|---|---|
| Employee | 10 fields | HR, payroll, org charts |
| Hospital | 8 fields | Healthcare, billing |
| Sales | 8 fields | BI dashboards, analytics |
| E-Commerce | 8 fields | Retail, transactions |
| VPN | 7 fields | Network monitoring |
| HR | 7 fields | Performance, compensation |

### 🔧 Custom Schema Builder
- **40+ field types**: UUID, names, email, phone, address, GPS, company, dates, integers, floats, booleans, JSON, IP, MAC, and more
- **Advanced options**: unique values, nullable, default, prefix/suffix, regex, sequential, enum, range-based, custom distributions
- **Data Quality Controls**: null rate, duplicate rate, outlier rate, Normal/Uniform/Exponential/Skewed distributions

### 🔗 Relational Data Generation
- Multi-table schemas with FK relationships
- One-to-One, One-to-Many, Many-to-One
- Automatic topological sort (parents first)
- Referential integrity guaranteed

### 📊 Analytics Datasets
| Type | Fields | Pattern |
|---|---|---|
| Revenue | date, revenue, profit, expenses, customer_count | Trend + seasonality + noise |
| Website | date, users, sessions, bounce_rate, conversion_rate | Correlated growth |
| IoT | timestamp, device_id, temperature, humidity, pressure | Diurnal time-series |
| VPN | date, country, active_users, bandwidth, latency | Regional trends |

### 🗄️ SQL Schema Generator
- `CREATE TABLE` statements
- `ALTER TABLE` with `FOREIGN KEY` constraints
- `CREATE INDEX` on FK columns
- `INSERT INTO` sample data
- **4 dialects**: PostgreSQL, MySQL, SQLite, SQL Server

### 📐 ER Diagram Generator
- Mermaid `erDiagram` syntax
- Auto-generated from table schemas
- PK/FK markers on all fields
- Zoom, pan, SVG download

### 📤 Export Formats
| Format | Method | Max Rows |
|---|---|---|
| CSV | Streaming | 1,000,000 |
| JSON | Streaming | 1,000,000 |
| SQL | Streaming (batched) | 1,000,000 |
| Excel | Write-only mode | 100,000 |

---

## 🏗️ Architecture

```
DataForge/
├── backend/                  # Python 3.13 + FastAPI
│   ├── app/
│   │   ├── api/              # Thin route controllers
│   │   ├── services/         # Business logic orchestration
│   │   ├── generators/       # Memory-efficient data generators
│   │   ├── exports/          # Streaming file exporters
│   │   ├── schemas/          # Pydantic v2 request/response models
│   │   ├── core/             # Config, logging, lifespan
│   │   ├── middleware/        # Rate limiter, observability, payload guard
│   │   ├── exceptions/       # Centralized exception handling
│   │   └── main.py           # Application factory
│   └── tests/                # Pytest unit + integration tests
│
└── frontend/                 # React 18 + Vite + TypeScript
    └── src/
        ├── pages/            # 8 pages (lazy loaded)
        ├── components/       # Reusable UI components + AG Grid
        ├── hooks/            # React Query mutations + custom hooks
        ├── services/         # Axios API client + download helpers
        ├── layouts/          # App shell with collapsible sidebar
        └── types/            # TypeScript interfaces
```

### Key Design Decisions

- **Generator pattern**: All data generation uses Python iterators — only one row is live in memory at a time
- **Streaming exports**: FastAPI `StreamingResponse` + chunked transfer encoding — 1M rows without OOM
- **Topological sort**: Parent tables always generated before children for FK integrity
- **NumPy vectorization**: Analytics datasets use NumPy arrays for fast correlated data
- **AG Grid**: Frontend never loads full dataset — virtualized rows + server-side pagination

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/yourorg/dataforge.git
cd dataforge

# Start everything with one command
docker compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy env file
cp .env.example .env

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies /api to localhost:8000)
npm run dev

# Open http://localhost:3000
```

---

## 📖 API Documentation

Interactive docs available at: `http://localhost:8000/docs`

### Core Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/ready` | Readiness check |
| `GET` | `/templates` | List all pre-built templates |
| `POST` | `/preview` | Preview first 50 rows |
| `POST` | `/generate` | Generate data (returns metrics) |
| `POST` | `/generate-schema` | Generate SQL DDL |
| `POST` | `/generate-relations` | Generate relational multi-table data |
| `POST` | `/generate-erd` | Generate Mermaid ER diagram |
| `POST` | `/export/csv` | Stream CSV file |
| `POST` | `/export/json` | Stream JSON file |
| `POST` | `/export/sql` | Stream SQL INSERT file |
| `POST` | `/export/excel` | Download Excel file |
| `POST` | `/analytics/preview` | Preview analytics dataset |
| `POST` | `/export/analytics/csv` | Stream analytics CSV |
| `POST` | `/export/analytics/json` | Stream analytics JSON |

### Example: Preview Employee Data

```bash
curl -X POST http://localhost:8000/preview \
  -H "Content-Type: application/json" \
  -d '{
    "table": {
      "name": "employee",
      "fields": [
        {"name": "id", "field_type": "uuid", "unique": true},
        {"name": "name", "field_type": "full_name"},
        {"name": "email", "field_type": "email", "unique": true},
        {"name": "salary", "field_type": "salary", "min_value": 50000, "max_value": 200000}
      ],
      "row_count": 1000
    }
  }'
```

### Example: Export 100K CSV Rows

```bash
curl -X POST http://localhost:8000/export/csv \
  -H "Content-Type: application/json" \
  -d '{"table": {"name": "sales", "fields": [...], "row_count": 100000}}' \
  --output sales_data.csv
```

---

## 🧪 Testing

**Backend:**
```bash
cd backend
pip install -e ".[dev]"
pytest tests/ -v --tb=short

# Code quality
ruff check app/
black --check app/
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run type-check
npm test
```

---

## 🐳 Docker Details

### Build individual images:
```bash
# Backend only
docker build -t dataforge-backend ./backend

# Frontend only
docker build -t dataforge-frontend ./frontend
```

### Environment variables (backend):
```env
MAX_ROWS=1000000
RATE_LIMIT_GENERATE=30/minute
RATE_LIMIT_EXPORT=10/minute
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

---

## 📸 Screenshots

> _Screenshots placeholder — run the app and visit http://localhost:3000_

| Dashboard | Schema Builder | ER Diagram |
|---|---|---|
| [Screenshot] | [Screenshot] | [Screenshot] |

| Template Generator | Analytics | Export |
|---|---|---|
| [Screenshot] | [Screenshot] | [Screenshot] |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'feat: add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

### Code Standards
- **Backend**: Black (line length 100) + Ruff linting + type annotations required
- **Frontend**: ESLint + Prettier + TypeScript strict mode
- **Tests**: Required for all new features — pytest (backend) + Vitest (frontend)
- **Commits**: Conventional commits format (`feat:`, `fix:`, `docs:`, etc.)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">Built with ❤️ using FastAPI + React + TailwindCSS</p>
