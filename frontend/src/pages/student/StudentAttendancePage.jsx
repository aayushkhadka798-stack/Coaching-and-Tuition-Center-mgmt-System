import { useEffect, useState } from 'react'
import { Card } from '../../components/ui'
import StudentPageShell from '../../components/student/StudentPageShell'
import { getStudentAttendanceSummary, listStudentAttendance } from '../../api/studentApi'

export default function StudentAttendancePage() {
  const [summary, setSummary] = useState([])
  const [records, setRecords] = useState([])
  useEffect(() => { Promise.all([getStudentAttendanceSummary(), listStudentAttendance()]).then(([a, b]) => { setSummary(a.data.results || a.data); setRecords(b.data.results || b.data) }).catch(() => {}) }, [])
  return <StudentPageShell activePath="attendance" title="Attendance"><header className="profile-header"><div><p className="eyebrow">STUDENT PORTAL</p><h1>Attendance</h1><p className="muted">Track your attendance by batch and date.</p></div></header><div className="student-card-grid">{summary.map((row) => <Card key={row.batch_id}><h2>{row.batch}</h2><strong>{row.percentage}%</strong><p className="muted">{row.present} present · {row.late} late · {row.absent} absent</p><div className="progress-track"><span style={{ width: `${row.percentage}%` }} /></div></Card>)}{!summary.length && <Card><p className="muted">No attendance records yet.</p></Card>}</div><Card><h2>Attendance history</h2>{records.map((row) => <div className="student-list-row" key={row.id}><span>{row.date}</span><strong>{row.batch}</strong><span className={`payment-status ${row.status}`}>{row.status}</span></div>)}</Card></StudentPageShell>
}
