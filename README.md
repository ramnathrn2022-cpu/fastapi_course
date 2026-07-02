# FastAPI Course Project
A social-media–style REST API built with FastAPI, PostgreSQL, and SQLAlchemy. Users can register, log in (JWT auth), create posts, and vote on posts.

🌐 Live demo: https://fastapi-course-1-mqho.onrender.com/docs

## Features
* 🔐 **JWT authentication** with hashed passwords (bcrypt/passlib)
* 📝 **Posts CRUD** — create, read, update, delete (owner-only for update/delete)
* 👍 **Voting** — one vote per user per post
* 👤 **Users** — registration and lookup
* 🗄️ **PostgreSQL** via SQLAlchemy ORM
* 🔀 **Alembic** database migrations
* ⚙️ **Environment-based config** (pydantic-settings)
* ✅ **27 automated tests** (pytest) against an isolated test database
* 🐳 **Docker + docker-compose** for local development
* 🔄 **CI via GitHub Actions** (tests + Docker build on every push)

## Tech Stack
| Layer | Tech |
| :--- | :--- |
| **Framework** | FastAPI |
| **Server** | Uvicorn |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Migrations** | Alembic |
| **Auth** | OAuth2 password flow + JWT (python-jose) |
| **Validation/Settings** | Pydantic v2 / pydantic-settings |
| **Tests** | pytest |
| **Containers** | Docker / docker-compose |
| **CI** | GitHub Actions |

## Project Structure
```text
app/
  main.py            # FastAPI app + router registration
  config.py          # Settings loaded from environment
  database.py        # SQLAlchemy engine/session
  models.py          # ORM models (User, Post, Vote)
  schemas.py         # Pydantic request/response schemas
  oauth2.py          # JWT creation/verification
  utils.py           # Password hashing helpers
  routers/
    auth.py          # /login
    user.py          # /users
    post.py          # /posts
    vote.py          # /vote
alembic/             # Migrations
tests/               # pytest suite
Dockerfile
docker-compose.yml
.github/workflows/   # CI
```

## Environment Variables
The app reads config from environment variables (or a local `.env` file). Required keys:

| Key | Example |
| :--- | :--- |
| **DATABASE_HOSTNAME** | localhost |
| **DATABASE_PORT** | 5432 |
| **DATABASE_NAME** | fastapi |
| **DATABASE_USERNAME** | postgres |
| **DATABASE_PASSWORD** | postgres123 |
| **SECRET_KEY** | (long random hex string) |
| **ALGORITHM** | HS256 |
| **ACCESS_TOKEN_EXPIRE_MINUTES** | 30 |

`.env` is git-ignored — never commit real secrets. Generate a secret key with:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Running Locally (without Docker)
Prerequisites: Python 3.10+, PostgreSQL running locally, a database created (e.g. `fastapi`).

1. **Create & activate a virtual environment**:
   ```powershell
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** with the variables listed above.

4. **Apply migrations**:
   ```powershell
   alembic upgrade head
   ```

5. **Run the server**:
   ```powershell
   uvicorn app.main:app --reload
   ```
Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

---

## Running with Docker
Spins up the API and a Postgres database together:
```powershell
docker compose up --build
```
The API is available at `http://localhost:8000/docs`. Postgres data persists in a named volume.

---

## Running the Tests
Tests use a separate database named `<DATABASE_NAME>_test` (e.g. `fastapi_test`). Create it once:
```sql
CREATE DATABASE fastapi_test;
```
Then run:
```powershell
$env:PYTHONPATH="c:\fastapi"; pytest -v
```
The suite recreates the schema for each test, so tests are fully isolated and never touch your dev data.

---

## Database Migrations (Alembic)
Whenever you change a model:
```powershell
$env:PYTHONPATH="c:\fastapi"; alembic revision --autogenerate -m "describe the change"
$env:PYTHONPATH="c:\fastapi"; alembic upgrade head
```

---

## API Endpoints
| Method | Path | Auth | Description |
| :--- | :--- | :---: | :--- |
| **GET** | `/` | – | Health/welcome message |
| **POST** | `/users/` | – | Register a new user |
| **GET** | `/users/{id}` | – | Get a user by id |
| **POST** | `/login` | – | Log in (form data: username, password) → JWT |
| **GET** | `/posts/` | ✅ | List posts (with vote counts); supports limit, skip, search |
| **POST** | `/posts/` | ✅ | Create a post |
| **GET** | `/posts/{id}` | ✅ | Get one post (with vote count) |
| **PUT** | `/posts/{id}` | ✅ (owner) | Update a post |
| **DELETE** | `/posts/{id}` | ✅ (owner) | Delete a post |
| **POST** | `/vote/` | ✅ | Vote (dir: 1) or un-vote (dir: 0) on a post |

*Auth: send `Authorization: Bearer <access_token>` (obtained from `/login`).*

---

## Deployment
Deployed on Render (free tier) with a managed PostgreSQL instance. Environment variables are configured in the Render dashboard; every push to main triggers an automatic redeploy.

> [!NOTE]
> The Render free tier spins down services after ~15 minutes of inactivity. The first request after a period of inactivity may take a few seconds to boot up.