# 🚀 NBA Props Cloud Deployment Guide

Deploy your NBA Props app to the cloud so it's accessible 24/7 from anywhere, with automatic data updates.

## Architecture
- **Frontend**: Vercel (free, always on)
- **Backend**: Railway ($5 free credit/month, runs 24/7 with scheduled jobs)
- **Database**: Railway PostgreSQL (included with Railway)

## Scheduled Jobs (Automatic)
| Job | Frequency | Description |
|-----|-----------|-------------|
| Odds | Every 5 minutes | Fetches latest prop lines |
| DVP | Daily at 6 AM EST | Defense vs Position data |
| Gamelogs | Every 2 hours | Player game statistics |

---

## Step 1: Set Up Railway (Backend + Database)

### 1.1 Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended)
3. You get $5 free credit per month

### 1.2 Create New Project
1. Click "New Project"
2. Choose "Deploy from GitHub repo"
3. Select your `NBA-UI-Props` repository
4. When asked, select the **`backend`** folder as the root

### 1.3 Add PostgreSQL Database
1. In your project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will auto-provision and connect it

### 1.4 Configure Environment Variables
In Railway, go to your backend service → Variables:

```env
# Required
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<generate with: openssl rand -hex 32>
PRO_USER_EMAIL=cgpropz@gmail.com

# URLs (update after Vercel deploy)
FRONTEND_URL=https://your-app.vercel.app
API_URL=https://your-backend.railway.app

# Optional (leave empty if not using Stripe)
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_ID=

DEBUG=false
```

### 1.5 Deploy
Railway will auto-deploy. Your backend URL will be something like:
`https://nba-ui-props-production.up.railway.app`

---

## Step 2: Set Up Vercel (Frontend)

### 2.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### 2.2 Import Project
1. Click "Add New" → "Project"
2. Import your `NBA-UI-Props` repository
3. **Important**: Set the Root Directory to `frontend`

### 2.3 Configure Build Settings
- Framework: Next.js
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `.next`

### 2.4 Add Environment Variables
Add this variable in Vercel project settings:

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

Replace with your actual Railway backend URL from Step 1.5.

### 2.5 Deploy
Click "Deploy". Your frontend will be live at:
`https://your-app.vercel.app`

---

## Step 3: Create Pro User in Cloud

After both services are deployed, create your pro user:

```bash
# SSH into Railway or use the Railway CLI
railway run python -c "
from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import get_password_hash

Base.metadata.create_all(bind=engine)
db = SessionLocal()
user = User(
    email='cgpropz@gmail.com',
    hashed_password=get_password_hash('YOUR_PASSWORD_HERE'),
    full_name='CG Propz',
    subscription_tier='pro',
    subscription_status='active',
    is_active=True,
    is_verified=True
)
db.add(user)
db.commit()
print('Pro user created!')
"
```

---

## Step 4: Update Frontend URL in Railway

Go back to Railway and update the `FRONTEND_URL` to your Vercel URL.

---

## Quick Verification

### Check Backend Health
```bash
curl https://your-backend.railway.app/api/health
# Should return: {"status": "healthy"}
```

### Check Scheduler Status
```bash
curl https://your-backend.railway.app/api/scheduler/status
# Shows running jobs and next execution times
```

### Trigger Manual Refresh
```bash
curl -X POST https://your-backend.railway.app/api/scheduler/trigger
# Forces immediate data refresh
```

---

## Custom Domain (Optional)

### Vercel (Frontend)
1. Go to Project Settings → Domains
2. Add your domain (e.g., `cgpropz.com`)
3. Update DNS as instructed

### Railway (Backend)
1. Go to Service Settings → Networking
2. Add custom domain (e.g., `api.cgpropz.com`)
3. Update DNS as instructed

---

## Costs

| Service | Free Tier | After Free |
|---------|-----------|------------|
| Vercel | Unlimited (hobby) | N/A |
| Railway | $5/month credit | ~$5-10/month |
| **Total** | **$0** | **~$5/month** |

---

## Troubleshooting

### Backend not starting?
- Check Railway logs for errors
- Ensure `DATABASE_URL` is set correctly
- Verify all dependencies in `requirements.txt`

### Frontend can't connect to API?
- Verify `NEXT_PUBLIC_API_URL` is set in Vercel
- Check CORS settings in backend
- Ensure Railway service is running

### Scheduler not running?
- Check `/api/scheduler/status` endpoint
- Review Railway logs for scheduler errors
- Verify APScheduler is installed

---

## Files Created for Deployment

```
backend/
├── Procfile            # Railway start command
├── railway.json        # Railway config
├── runtime.txt         # Python version
└── app/
    └── cloud_scheduler.py  # Cloud-compatible data fetchers
```

---

## Support

If you need help, check:
1. Railway docs: https://docs.railway.app
2. Vercel docs: https://vercel.com/docs
3. Railway Discord: https://discord.gg/railway
