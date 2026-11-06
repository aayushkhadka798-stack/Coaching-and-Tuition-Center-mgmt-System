import { useEffect, useState } from 'react'
import { Card, Button } from '../../components/ui'
import StudentPageShell from '../../components/student/StudentPageShell'
import { listStudentResults } from '../../api/studentApi'

export default function StudentResultsPage() {
  const [rows, setRows] = useState([])
  useEffect(() => { listStudentResults().then(({ data }) => setRows(data.results || data)).catch(() => {}) }, [])
  return <StudentPageShell activePath="results" title="Results"><header className="profile-header"><div><p className="eyebrow">STUDENT PORTAL</p><h1>Results</h1><p className="muted">Review marks, percentages, and grades.</p></div><Button variant="outline" onClick={() => window.print()}>Print report card</Button></header><Card><div className="student-results-table">{rows.map((row) => <div className="student-list-row" key={row.id}><span>{row.exam}<small>{row.exam_date}</small></span><strong>{row.marks_obtained} / {row.total_marks}</strong><span>{row.percentage}%</span><b>{row.grade}</b></div>)}{!rows.length && <p className="muted">No results yet.</p>}</div></Card></StudentPageShell>
}
