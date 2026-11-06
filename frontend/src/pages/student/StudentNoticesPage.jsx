import { useEffect, useState } from 'react'
import { Card } from '../../components/ui'
import StudentPageShell from '../../components/student/StudentPageShell'
import { listStudentNotices, markStudentNoticeRead } from '../../api/studentApi'

export default function StudentNoticesPage() {
  const [rows, setRows] = useState([])
  const load = () => listStudentNotices().then(({ data }) => setRows(data.results || data)).catch(() => {})
  useEffect(load, [])
  const markRead = (notice) => { if (!notice.is_read) markStudentNoticeRead(notice.id).then(load) }
  return <StudentPageShell activePath="notices" title="Notices"><header className="profile-header"><div><p className="eyebrow">STUDENT PORTAL</p><h1>Notices</h1><p className="muted">Updates from your center and batches.</p></div><span className="ui-badge">{rows.filter((row) => !row.is_read).length} unread</span></header><div className="student-notice-list">{rows.map((notice) => <Card key={notice.id} className={notice.is_read ? '' : 'notice-unread'} onClick={() => markRead(notice)}><div className="notice-meta"><span>{notice.target_role}</span><time>{new Date(notice.created_at).toLocaleDateString()}</time></div><h2>{notice.title}</h2><p>{notice.body}</p></Card>)}{!rows.length && <Card><p className="muted">No notices yet.</p></Card>}</div></StudentPageShell>
}
