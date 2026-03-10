# CheckMate API

A backend for remote sales data collection. Companies register their teams, assign products, and send salesmen to the field — where they capture real sales details in real time, complete with automatic geolocation tagging.

Built with **FastAPI**, deployed live on **Render**, and powered by **PostgreSQL on Neon**.

📖 **Live API Docs:** [https://checkmate-lvnc.onrender.com/docs](https://checkmate-lvnc.onrender.com/docs)

---

## Features

- **Company accounts** — companies register and manage their entire sales operation from one place
- **Salesman management** — add and manage your field sales team
- **Product catalogue** — define the products your team sells
- **Field sales capture** — salesmen log sale details directly from the field
- **Automatic geolocation** — every sales record is automatically tagged with the salesman's location at the time of capture
- **JWT authentication** — secured endpoints for both company admins and salesmen

---

## Tech Stack

FastAPI · PostgreSQL · SQLAlchemy · Geolocation · JWT · Rate Limiting · Pagination · Render · Neon DB

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/company/register` | Register a new company |
| POST | `/auth/login` | Login as company admin or salesman |
| POST | `/salesmen` | Add a salesman to your team |
| GET | `/salesmen` | List all salesmen in your company |
| POST | `/products` | Add a product to your catalogue |
| POST | `/sales` | Capture a field sale (auto-tags location) |
| GET | `/sales` | View all captured sales records |
| GET | `/sales/{salesman_id}` | View sales by a specific salesman |

> Full interactive documentation available at the live docs link above.

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/b100mBUG/checkmate.git
cd checkmate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Fill in: DATABASE_URL, SECRET_KEY

# Run the server
uvicorn main:app --reload
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (Neon) |
| `SECRET_KEY` | JWT signing secret |

---

## Author

**Were Fidel Castro** — [github.com/b100mBUG](https://github.com/b100mBUG) · [Portfolio](https://werefidelcastro.onrender.com)
