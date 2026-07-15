# CheckMate API

Backend for remote sales team tracking. Companies register, add their sales team and product catalogue, then send salesmen into the field. Every sale gets logged in real time with the salesman's location tagged automatically.

Built with FastAPI, deployed on Render, backed by PostgreSQL on Neon.

Live API docs: https://checkmate-lvnc.onrender.com/docs

## What it does

A company signs up and gets its own isolated space for its sales operation. From there they add salesmen, define what those salesmen are selling, and get a live feed of field sales as they happen, each one timestamped and geotagged to where the sale was made. Company admins and salesmen authenticate separately through the same JWT-secured API.

## Stack

FastAPI, PostgreSQL, SQLAlchemy, JWT auth, rate limiting, pagination. Deployed on Render with Neon for the database.

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/company/register` | Register a new company |
| POST | `/auth/login` | Login as company admin or salesman |
| POST | `/salesmen` | Add a salesman to your team |
| GET | `/salesmen` | List all salesmen in your company |
| POST | `/products` | Add a product to your catalogue |
| POST | `/sales` | Capture a field sale, auto-tags location |
| GET | `/sales` | View all captured sales records |
| GET | `/sales/{salesman_id}` | View sales by a specific salesman |

Full interactive docs are at the live link above.

## Running locally

```bash
git clone https://github.com/b100mBUG/checkmate.git
cd checkmate
pip install -r requirements.txt
cp .env.example .env
# fill in DATABASE_URL and SECRET_KEY
uvicorn main:app --reload
```

## Environment variables

| Variable | Description |
|----------|--------------|
| `DATABASE_URL` | PostgreSQL connection string (Neon) |
| `SECRET_KEY` | JWT signing secret |

## Author

Were Fidel Castro. [GitHub](https://github.com/b100mBUG). [Portfolio](https://werefidelcastro.onrender.com).
