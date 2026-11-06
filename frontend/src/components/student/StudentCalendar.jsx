import { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

export default function StudentCalendar({ value, onChange, markedDays = [] }) {
  const [month, setMonth] = useState(new Date(value.getFullYear(), value.getMonth(), 1))
  const firstDay = new Date(month.getFullYear(), month.getMonth(), 1).getDay()
  const totalDays = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate()
  const selected = value.toDateString()
  const cells = Array.from({ length: firstDay + totalDays }, (_, index) => index < firstDay ? null : index - firstDay + 1)
  const select = (day) => onChange(new Date(month.getFullYear(), month.getMonth(), day))
  return <div className="student-calendar"><div className="calendar-caption"><button onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() - 1, 1))} aria-label="Previous month"><ChevronLeft size={17} /></button><strong>{monthNames[month.getMonth()]} {month.getFullYear()}</strong><button onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() + 1, 1))} aria-label="Next month"><ChevronRight size={17} /></button></div><div className="calendar-weekdays">{weekdays.map((day) => <span key={day}>{day}</span>)}</div><div className="calendar-grid">{cells.map((day, index) => day ? <button className={new Date(month.getFullYear(), month.getMonth(), day).toDateString() === selected ? 'selected' : ''} key={day} onClick={() => select(day)}>{day}{markedDays.includes(new Date(month.getFullYear(), month.getMonth(), day).getDay()) && <i />}</button> : <span key={`empty-${index}`} />)}</div></div>
}
