# Admin implementation checklist

### A1 - Foundation + Teachers
- [x] Install/configure Tailwind + shadcn/ui and all components listed above
- [x] Build shared components (DataTable, FormDialog, ConfirmDialog, PageHeader, StatCard, StatusBadge, EmptyState, ErrorState, toasts)
- [x] Rebuild admin layout with them; logout opens ConfirmDialog in admin, teacher and student layouts
- [x] Backend /api/teachers/ full CRUD (create user role=teacher + TeacherProfile in admin's center), search, active filter
- [x] Teacher extras: reset password, toggle active, block delete if assigned to batches (409)
- [x] Frontend Teachers page: table, add/edit dialog, delete confirm, active toggle, details sheet
- [x] Tests: permissions, tenant isolation, new teacher can log in at /login

### A2 - Courses, Batches, Timetable, Students, Enrollments
- [ ] Course model/API/UI (name, description, fee_amount, is_active); deactivate, block delete if batches exist
- [ ] Batch model/API/UI (course, teacher, name, start/end dates, capacity, is_active); students-in-batch view; reassign teacher
- [ ] BatchSchedule model/API/UI (day, start/end time, room); no overlap for same teacher or room
- [ ] Students API/UI: admin create/edit/deactivate/delete (soft), auto roll_no per center, details with batches summary
- [ ] Enrollment model/API/UI: enroll student in batch (searchable select), capacity check, unique active enrollment, drop/complete status
- [ ] Tests for all rules and tenant isolation

### A3 - Fees & Payments
- [ ] Fee model/API (enrollment, amount_due, due_date, status unpaid/partial/paid, computed paid and balance); auto-create from course fee on enrollment; admin can adjust amount/due date with a note; cancel with reason
- [ ] Payment model/API: record cash/bank payment (amount <= balance, atomic status update), void with reason, receipt endpoint
- [ ] Fees summary endpoint (total due, collected, outstanding, overdue)
- [ ] Frontend Fees page: filters (status, batch, student, overdue), Record payment dialog, payment history sheet, printable receipt, method badge
- [ ] Tests for balance rules, void, tenant isolation

### A4 - Attendance, Exams & Results (admin view and correction)
- [ ] Attendance model/API: records per enrollment+date (unique), bulk mark endpoint, admin correct records, summary endpoint
- [ ] Admin Attendance page: overview by batch/date/student, mark or correct, percentage per student
- [ ] Exam and Result models/API (marks <= total_marks, unique per exam+student), bulk marks endpoint, computed percentage/grade
- [ ] Admin Exams & Results pages: create/edit exam, enter/edit marks, results by exam or student, report card view (printable)
- [ ] Tests

### A5 - Notices + Center settings + My account
- [ ] Notice model/API/UI CRUD (title, body, target all/teachers/students/batch, posted_by)
- [ ] Center settings: view/edit name, contact; regenerate center code (confirm dialog warning that old code stops working)
- [ ] Admin profile edit + change password UI

### A6 - Reports + real Dashboard
- [ ] Report endpoints (enrollment, attendance, fee collection, outstanding, results) with filters and ?format=csv
- [ ] Reports page with tables, filters, export CSV and print
- [ ] /api/admin/dashboard/ with real aggregates (students, active teachers, active batches, fees collected this month in NPR, attendance rate, recent payments and notices, monthly collection and attendance trend)
- [ ] Replace ALL mock numbers/charts on the admin dashboard with real data; real empty states when there is no data

### A7 - Seed, polish, docs
- [ ] `seed_demo_data` management command (idempotent, clearly labeled demo): centers, admin, teachers, students, courses, batches, enrollments, fees, attendance, exams
- [ ] Polish: consistent loading/empty/error states, 401 auto-logout, 403 page, responsive layouts, aria-labels on icon buttons, focus handling in dialogs
- [ ] Update README, docs/api/endpoints.md and the ERD in docs/erd/ (list any differences from the original)
- [ ] Final full test run, npm run build, and a manual test script for the whole admin flow

## Notes / Decisions
- Work is executed one step at a time; A1 is the current step.
- Existing authentication, tenant boundaries, and student/teacher portal behavior must remain compatible.
- Tailwind and the existing shadcn-style UI foundation were already present; A1 completed the shared primitives needed by the admin flow without replacing the current visual system.
- The canonical teacher API is `/api/teachers/`; the legacy `/api/auth/teachers/` routes remain available for compatibility.
