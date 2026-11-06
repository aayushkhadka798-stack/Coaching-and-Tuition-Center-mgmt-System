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
| GET | `/api/fees/` | Authenticated; students see their own fees |
| POST | `/api/fees/<fee_id>/esewa/initiate/` | Student; initiate an eSewa Sandbox payment |
| POST | `/api/payments/esewa/verify/` | Student; verify the Base64 eSewa success response |
| POST | `/api/payments/esewa/failure/` | Student; mark an initiated payment canceled |
| GET | `/api/admin/esewa-transactions/` | Admin; center-scoped online payment tracking |
| GET | `/api/student/dashboard/` | Student's summary metrics |
| GET/PATCH | `/api/student/profile/` | Student's own editable profile fields |
| GET | `/api/student/enrollments/` | Student's own enrolled batches |
| GET | `/api/student/timetable/` | Student's weekly schedule |
| GET | `/api/student/attendance/` | Student's attendance history |
| GET | `/api/student/attendance/summary/` | Student's attendance totals and percentages |
| GET | `/api/student/fees/` | Student's own fees and balances |
| GET | `/api/student/payments/` | Student's own payment history |
| GET | `/api/student/payments/{id}/receipt/` | Student's payment receipt data |
| GET | `/api/student/results/` | Student's marks, percentages, and grades |
| GET | `/api/student/results/report-card/` | Student's report-card results |
| GET | `/api/student/notices/` | Targeted student notices |
| POST | `/api/student/notices/{id}/read/` | Mark an eligible notice as read |
