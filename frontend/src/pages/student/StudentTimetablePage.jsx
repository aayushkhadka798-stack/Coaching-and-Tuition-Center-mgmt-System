import { useEffect, useMemo, useState } from 'react'
import { Card } from '../../components/ui'
import StudentPageShell from '../../components/student/StudentPageShell'
import StudentCalendar from '../../components/student/StudentCalendar'
import { listStudentTimetable } from '../../api/studentApi'

const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
export default function StudentTimetablePage() {
  const [rows, setRows] = useState([])
  const [selectedDate, setSelectedDate] = useState(new Date())
  useEffect(() => { listStudentTimetable().then(({ data }) => setRows(data.results || data)).catch(() => {}) }, [])
  const selectedSlots = rows.filter((row) => row.day_of_week === selectedDate.getDay())
  const markedDays = useMemo(() => rows.map((row) => row.day_of_week), [rows])
  return <StudentPageShell activePath="timetable" title="Timetable"><header className="profile-header"><div><p className="eyebrow">STUDENT PORTAL</p><h1>Weekly timetable</h1><p className="muted">Choose a day to see your scheduled classes.</p></div></header><div className="timetable-layout"><Card><StudentCalendar value={selectedDate} onChange={setSelectedDate} markedDays={markedDays} /></Card><Card className="schedule-card"><div className="schedule-heading"><div><p className="eyebrow">{days[selectedDate.getDay()]}</p><h2>{selectedDate.toLocaleDateString(undefined, { month: 'long', day: 'numeric' })}</h2></div><span className="ui-badge">{selectedSlots.length} {selectedSlots.length === 1 ? 'class' : 'classes'}</span></div>{selectedSlots.map((row) => <div className="timetable-slot" key={row.id}><strong>{row.start_time} – {row.end_time}</strong><span>{row.course_name || row.batch_name || `Batch #${row.batch}`} · {row.teacher_name || 'Teacher not set'} · {row.room || 'Room not set'}</span></div>)}{!selectedSlots.length && <div className="empty-summary"><p>No class scheduled for this day.</p></div>}</Card></div></StudentPageShell>
}
