# Authentication API

| Method | Endpoint | Access |
| --- | --- | --- |
| POST | `/api/auth/register/` | Public student registration |
| POST | `/api/auth/login/` | Teacher/student |
| POST | `/api/auth/google/` | Teacher/student Google ID token; new students may provide `center_code` |
| POST | `/api/auth/admin/login/` | Admin |
| POST | `/api/auth/token/refresh/` | Public with refresh token |
| POST | `/api/auth/logout/` | Authenticated |
| GET | `/api/auth/me/` | Authenticated |
| GET/PATCH | `/api/auth/profile/` | Authenticated profile and photo update |
| POST | `/api/auth/change-password/` | Authenticated |
| GET/POST | `/api/teachers/` | Admin |
| GET | `/api/students/` | Admin |
| GET | `/api/{role}/dashboard/` | Matching role |
| GET | `/api/health/` | Public |
