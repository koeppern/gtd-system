# GTD System - Getting Things Done

A comprehensive productivity management system built with FastAPI (Python backend) and Next.js (React frontend), integrated with Supabase for cloud database management.

## 🚀 Features

- **Complete GTD Workflow**: Capture, clarify, organize, reflect, and engage with your tasks and projects
- **Multi-User Support**: User management with data isolation
- **Project & Task Management**: Hierarchical organization with field categorization
- **Real-time Sync**: Supabase integration for instant data synchronization
- **Modern Tech Stack**: FastAPI backend with Next.js frontend
- **RESTful API**: Comprehensive API endpoints for all GTD operations

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database with real-time capabilities
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Data fetching and caching

### Database
- **PostgreSQL** (via Supabase) - Primary database
- **Row Level Security** - Multi-tenant data isolation

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase account

### 1. Clone Repository
```bash
git clone https://github.com/koeppern/gtd-system.git
cd gtd-system
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Supabase
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Copy `.env.example` to `.env`
3. Update with your Supabase credentials:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DEFAULT_USER_ID=00000000-0000-0000-0000-000000000001
```

#### Setup Database Schema
```bash
# Run the SQL schema files in your Supabase SQL Editor:
# 1. sql/create_normalized_schema.sql
# 2. sql/create_gtd_tasks_table.sql
```

#### Configure Backend
```bash
# Copy config template
cp src/backend/config.example.yaml src/backend/config.yaml

# Update with your Supabase credentials
# Edit src/backend/config.yaml
```

### 3. Frontend Setup
```bash
cd src/frontend-prototype
npm install
cp .env.example .env.local
# Update .env.local with your API endpoint
```

## 🚀 Running the Application

### Start Backend (Terminal 1)
```bash
source .venv/bin/activate
cd src/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend (Terminal 2)
```bash
cd src/frontend-prototype
npm run dev
```

### Using Start Scripts
```bash
# Start both backend and frontend
./start-all.sh

# Start backend only
./start-backend.sh

# Start frontend only
./start-frontend.sh
```

## 📊 Database Schema

The system uses a normalized PostgreSQL schema with the following main tables:

- **gtd_users** - User management and preferences
- **gtd_fields** - Context/area classification (Work, Personal, etc.)
- **gtd_projects** - Project management with GTD workflow states
- **gtd_tasks** - Task management with completion tracking

## 🔧 Development

### Testing Backend
```bash
source .venv/bin/activate
python src/test_scripts/test_backend_supabase.py
```

### API Documentation
- Backend API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Project Structure
```
gtd-system/
├── src/
│   ├── backend/           # FastAPI backend
│   │   ├── app/          # Application code
│   │   ├── config.yaml   # Backend configuration (not tracked)
│   │   └── tests/        # Backend tests
│   ├── frontend-prototype/ # Next.js frontend
│   ├── etl_projects.py   # Data import utilities
│   ├── etl_tasks.py      # Task import utilities
│   └── test_scripts/     # Development test scripts
├── sql/                  # Database schema
├── config/               # YAML configurations
├── docs/                 # Documentation
└── requirements.txt      # Python dependencies
```

## 📝 GTD Methodology

This system implements the complete GTD workflow:

1. **Capture** - Quick task and project creation
2. **Clarify** - Process and categorize items
3. **Organize** - Sort into projects, contexts, and priorities
4. **Reflect** - Weekly reviews and planning
5. **Engage** - Execute with confidence

## 🔒 Security

- Environment variables for sensitive data
- Row Level Security (RLS) for multi-tenant isolation
- Service role authentication for backend operations
- No sensitive data committed to repository

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Check the [documentation](docs/) for detailed guides
- Open an issue for bug reports or feature requests
- Review API documentation at `/docs` endpoint

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Offline synchronization
- [ ] Advanced analytics and reporting
- [ ] Email integration
- [ ] Calendar synchronization
- [ ] Team collaboration features