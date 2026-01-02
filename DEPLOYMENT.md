# NBA Props - Full-Stack Subscription App

A full-stack NBA player props analysis application with subscription-based access.

## 🏗️ Architecture

```
NBA-UI-Props/
├── backend/           # FastAPI Python backend
│   ├── app/
│   │   ├── main.py    # FastAPI application
│   │   ├── models.py  # SQLAlchemy models
│   │   ├── schemas.py # Pydantic schemas
│   │   ├── auth.py    # JWT authentication
│   │   └── routers/   # API routes
│   └── Dockerfile
├── frontend/          # Next.js React frontend
│   ├── src/
│   │   ├── app/       # Next.js app router pages
│   │   ├── components/# React components
│   │   └── lib/       # API client & state
│   └── Dockerfile
├── docker-compose.yml # Full stack orchestration
└── *.json             # Data files (props, odds, DVP)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (or Docker)
- Stripe account

### 1. Clone and Setup Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

### 2. Run with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Manual Development Setup

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env

# Run database migrations (first time)
alembic upgrade head

# Start server
python run.py
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔐 Authentication

The app uses JWT tokens for authentication:

- **Register**: `POST /api/auth/register`
- **Login**: `POST /api/auth/login`
- **Get User**: `GET /api/auth/me` (requires token)

## 💳 Stripe Subscription Setup

1. Create a Stripe account at https://stripe.com
2. Create a Product and Price in the Stripe Dashboard
3. Set up webhook endpoint: `https://your-api.com/api/payments/webhook`
4. Configure webhook events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`

5. Add Stripe keys to `.env`:
```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
```

## 📊 API Endpoints

### Public Endpoints
- `GET /api/props/teams` - List all teams
- `GET /api/props/prop-types` - List prop types
- `GET /api/props/cards` - Get props (limited for free users)

### Authenticated Endpoints
- `GET /api/props/cards/top` - Top-rated props (Basic+)
- `GET /api/props/odds` - Live odds data (Basic+)
- `GET /api/props/dvp` - DVP analysis (Pro only)

### Payment Endpoints
- `POST /api/payments/create-checkout-session` - Start subscription
- `POST /api/payments/create-portal-session` - Manage billing
- `GET /api/payments/subscription` - Get subscription status

## 🌐 Deployment Options

### Option 1: Railway (Easiest)
1. Connect GitHub repo to Railway
2. Add PostgreSQL database
3. Set environment variables
4. Deploy!

### Option 2: Vercel + Render
- Frontend: Deploy to Vercel
- Backend: Deploy to Render
- Database: Supabase or Neon

### Option 3: DigitalOcean App Platform
- Full docker-compose support
- Managed PostgreSQL

### Option 4: AWS/GCP
- ECS/Cloud Run for containers
- RDS/Cloud SQL for database

## 📱 Features by Tier

| Feature | Free | Basic ($9.99) | Pro ($19.99) |
|---------|------|---------------|--------------|
| Top 10 props | ✅ | ✅ | ✅ |
| All props | ❌ | ✅ | ✅ |
| Projections | ❌ | ✅ | ✅ |
| Odds comparison | ❌ | ✅ | ✅ |
| DVP analysis | ❌ | ❌ | ✅ |
| API access | ❌ | ❌ | ✅ |

## 🔄 Data Updates

Run your existing data scripts to update prop data:

```bash
# Update player cards
python update_all_cards.py

# Fetch latest odds
python fetch_nba_props_cash_odds.py

# Update DVP data
python dvp_fetch.py
```

## 🛠️ Development

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 📄 License

MIT License - feel free to use for your own projects!
