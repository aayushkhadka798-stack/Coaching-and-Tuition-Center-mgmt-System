# Coaching Management System

Auth-first multi-tenant coaching center management system: Django REST Framework + PostgreSQL backend and React/Vite frontend. Each user belongs to one shared-schema `Center`; roles are admin, teacher, and student.

## Structure of the project

- `backend/config`: Django settings and URLs
- `backend/apps/core`: shared permissions and health endpoint
- `backend/apps/accounts`: center, user, profiles, authentication, and user management
- `backend/apps/{academics,attendance,fees,exams,notices}`: reserved domain app space
- `frontend/src`: API client, auth context, role routes, pages, and styling
- `docs/api`: endpoint reference

## Windows PowerShell setup

### PostgreSQL and backend

Create a PostgreSQL database and user, then run:

```powershell
cd backend
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations accounts
python manage.py migrate
python manage.py create_center_admin
python manage.py runserver
```

Set database credentials in `backend/.env`. The Django admin site is `/django-admin/`; the React admin login is `/admin/login`.

Interactive API documentation is available at `http://127.0.0.1:8000/api/docs/` (Swagger UI), with the raw OpenAPI schema at `/api/schema/` and ReDoc at `/api/redoc/`.

### Google sign-in configuration

Create a Web application OAuth client in Google Cloud Console. Add these Authorized JavaScript origins:

- `http://localhost:5173`
- `http://127.0.0.1:5173`

Leave Authorized redirect URIs empty. Put the client ID in both `backend/.env` as `GOOGLE_CLIENT_ID` and `frontend/.env` as `VITE_GOOGLE_CLIENT_ID`. The frontend hides Google sign-in when the Vite variable is missing. While the Google consent screen is in Testing mode, only listed test users can sign in.

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

## Role routes

| Role | Login | Dashboard |
| --- | --- | --- |
| Admin | `/admin/login` | `/admin/dashboard` |
| Teacher | `/login` | `/teacher/dashboard` |
| Student | `/login` or `/register` | `/student/dashboard` |

Wrong-role requests return 403 from the API and redirect to `/unauthorized` in the frontend.
