import { useEffect, useState } from 'react'
import { Card } from '../../components/ui'
import StudentPageShell from '../../components/student/StudentPageShell'
import { listStudentEnrollments } from '../../api/studentApi'

export default function StudentBatchesPage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  useEffect(() => { listStudentEnrollments().then(({ data }) => setRows(data.results || data)).catch(() => setError('Unable to load your batches.')) }, [])
  return <StudentPageShell activePath="batches" title="My batches"><header className="profile-header"><div><p className="eyebrow">STUDENT PORTAL</p><h1>My batches</h1><p className="muted">Your enrolled courses, teachers, and schedules.</p></div></header>{error && <p className="error">{error}</p>}<div className="student-card-grid">{rows.map((row) => <Card key={row.id}><span className="ui-badge">{row.status}</span><h2>{row.batch_name}</h2><p>{row.course}</p><p className="muted">Teacher: {row.teacher?.name}</p><p>{row.start_date} {row.end_date ? `– ${row.end_date}` : ''}</p></Card>)}{!rows.length && !error && <Card><p className="muted">No active batch enrollments yet.</p></Card>}</div></StudentPageShell>
}
