import { useMemo, useState } from 'react'
import { toast } from 'sonner'
import { resetTeacherPassword } from '../../../api/teacherApi'
import { useTeacherList, useCreateTeacher, useUpdateTeacher, useDeleteTeacher } from '../../../hooks/teachers/useTeachers'
import DataTable from '../../../components/shared/DataTable'
import FormDialog from '../../../components/shared/FormDialog'
import ConfirmDialog from '../../../components/shared/ConfirmDialog'
import PageHeader from '../../../components/shared/PageHeader'
import StatusBadge from '../../../components/shared/StatusBadge'
import { useAuth } from '../../../context/AuthContext'
import { DashboardSidebar, DashboardTopbar, roleNavigation } from '../../../components/dashboard/DashboardNavigation'

const fields = [
  { name: 'first_name', label: 'First name', rules: { required: 'First name is required.' } },
  { name: 'last_name', label: 'Last name', rules: { required: 'Last name is required.' } },
  { name: 'email', label: 'Email', type: 'email', rules: { required: 'Email is required.' } },
  { name: 'phone', label: 'Phone' },
  { name: 'qualification', label: 'Qualification' },
  { name: 'specialization', label: 'Specialization' },
  { name: 'joined_date', label: 'Joined date', type: 'date' },
  { name: 'password', label: 'Temporary password (optional)', type: 'password' },
]

export default function TeachersPage() {
  const { user, logout } = useAuth()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [dialog, setDialog] = useState(null)
  const [selected, setSelected] = useState(null)
  const [confirm, setConfirm] = useState(null)
  const [credentials, setCredentials] = useState(null)
  const [details, setDetails] = useState(null)
  const [mobileOpen, setMobileOpen] = useState(false)
  const params = useMemo(() => ({ search, page }), [search, page])
  const query = useTeacherList(params)
  const create = useCreateTeacher()
  const update = useUpdateTeacher()
  const remove = useDeleteTeacher()
  const rows = query.data?.results || []
  const submit = (payload) => {
    const operation = dialog === 'create' ? create.mutateAsync(payload) : update.mutateAsync({ id: selected.id, payload })
    operation.then((data) => {
      if (dialog === 'create') setCredentials({ email: data.email, password: data.temporary_password })
      else toast.success('Teacher updated.')
      setDialog(null)
    }).catch((error) => toast.error(error.response?.data?.detail || error.response?.data?.email?.[0] || 'Unable to save teacher.'))
  }
  const toggle = (teacher) => update.mutateAsync({ id: teacher.id, payload: { is_active: !teacher.is_active } }).then(() => toast.success(teacher.is_active ? 'Teacher deactivated.' : 'Teacher activated.')).catch(() => toast.error('Unable to update teacher.'))
  const confirmDelete = () => remove.mutateAsync(confirm.id).then(() => { toast.success('Teacher deleted.'); setConfirm(null) }).catch((error) => { toast.error(error.response?.data?.detail || 'Teacher could not be deleted.'); setConfirm(null) })
  const resetPassword = (teacher) => resetTeacherPassword(teacher.id).then(({ data }) => setCredentials({ email: teacher.email, password: data.temporary_password })).catch(() => toast.error('Unable to reset teacher password.'))
  return <div className="dashboard-shell"><DashboardSidebar role="admin" user={user} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} activePath="teachers" onLogout={() => setConfirm({ type: 'logout' })} /><main className="dashboard-main"><DashboardTopbar role="admin" user={user} label={`${roleNavigation.admin.label} · Teachers`} onMenu={() => setMobileOpen(true)} onLogout={() => setConfirm({ type: 'logout' })} /><div className="dashboard-content teachers-content"><PageHeader title="Teachers" description="Create and manage teachers in your center." actionLabel="Add teacher" onAction={() => { setSelected(null); setDialog('create') }} /><DataTable columns={[{ key: 'name', label: 'Teacher', render: (row) => <strong>{row.first_name} {row.last_name}</strong> }, { key: 'email', label: 'Email' }, { key: 'specialization', label: 'Specialization' }, { key: 'is_active', label: 'Status', render: (row) => <StatusBadge active={row.is_active} /> }]} rows={rows} loading={query.isLoading} error={query.isError} search={search} onSearch={(value) => { setPage(1); setSearch(value) }} onView={setDetails} onEdit={(row) => { setSelected(row); setDialog('edit') }} onReset={resetPassword} onToggle={toggle} onDelete={(row) => setConfirm(row)} pagination={{ page, previous: query.data?.previous, next: query.data?.next, go: setPage }} /></div></main>
    <FormDialog open={Boolean(dialog)} title={dialog === 'create' ? 'Add teacher' : 'Edit teacher'} initialValues={selected || {}} fields={dialog === 'edit' ? fields.filter((field) => field.name !== 'password') : fields} onSubmit={submit} onCancel={() => setDialog(null)} saving={create.isPending || update.isPending} />
    {details && <div className="dialog-backdrop" onMouseDown={(event) => event.target === event.currentTarget && setDetails(null)}><section className="dialog-card" role="dialog" aria-modal="true" aria-labelledby="teacher-details-title"><h2 id="teacher-details-title">{details.first_name} {details.last_name}</h2><p>{details.email}</p><p>Phone: {details.phone || 'Not provided'}</p><p>Qualification: {details.qualification || 'Not provided'}</p><p>Specialization: {details.specialization || 'Not provided'}</p><p>Joined: {details.joined_date || 'Not provided'}</p><div className="dialog-actions"><button className="ui-button" onClick={() => setDetails(null)}>Close</button></div></section></div>}
    <ConfirmDialog open={Boolean(confirm)} title={confirm?.type === 'logout' ? 'Sign out?' : `Delete ${confirm?.first_name || ''} ${confirm?.last_name || ''}?`} description={confirm?.type === 'logout' ? 'Are you sure you want to sign out?' : 'This permanently removes the teacher account if it is not assigned to a batch.'} confirmLabel={confirm?.type === 'logout' ? 'Sign out' : 'Delete'} onCancel={() => setConfirm(null)} onConfirm={confirm?.type === 'logout' ? logout : confirmDelete} />
    {credentials && <div className="dialog-backdrop"><section className="dialog-card" role="dialog" aria-modal="true" aria-labelledby="teacher-credentials-title"><div className="dialog-icon">✓</div><h2 id="teacher-credentials-title">Teacher login credentials</h2><p>Share these credentials securely with the teacher. The password is shown only now.</p><div className="credential-box"><strong>Email</strong><span>{credentials.email}</span><strong>Temporary password</strong><span>{credentials.password}</span></div><p className="field-help">Teacher login page: <strong>/login</strong>. Admin accounts must use <strong>/admin/login</strong>.</p><div className="dialog-actions"><button type="button" className="ui-button" onClick={() => setCredentials(null)}>Done</button></div></section></div>}
  </div>
}
