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

Student portal pages are available at `/student/dashboard`, `/student/profile`, `/student/batches`, `/student/timetable`, `/student/attendance`, `/student/fees`, `/student/results`, `/student/notices`, and `/student/settings`. These pages show center-scoped data derived from the authenticated student and render empty states until administrators or teachers create the related records.

### eSewa Sandbox payments

Copy the eSewa values into `backend/.env` (the secret is server-only and must never be added to frontend environment files):

```env
ESEWA_FORM_URL=https://rc-epay.esewa.com.np/api/epay/main/v2/form
ESEWA_STATUS_URL=https://rc-epay.esewa.com.np/api/epay/transaction/status/
ESEWA_SECRET_KEY=<sandbox-secret-from-esewa>
ESEWA_PRODUCT_CODE=EPAYTEST
ESEWA_SUCCESS_URL=http://localhost:5173/student/payments/esewa/success
ESEWA_FAILURE_URL=http://localhost:5173/student/payments/esewa/failure
```

Students can pay an unpaid or partial fee from **My fees**. The server signs the required ePay v2 fields, verifies the Base64 success response, calls the eSewa status API, and records an idempotent `eSewa` payment. Administrators can review online transactions from **Payment tracking → Online payments**. Existing cash and bank payment records remain supported.

For sandbox testing, use the test credentials provided by eSewa for the configured sandbox environment. Production requires a merchant account, production product code and secret, and production form/status URLs; do not reuse sandbox credentials.
