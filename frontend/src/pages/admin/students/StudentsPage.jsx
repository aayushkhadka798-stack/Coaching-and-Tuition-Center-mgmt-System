import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { listStudents, createStudent, updateStudent, deleteStudent } from '../../../api/studentApi'
import DataTable from '../../../components/shared/DataTable'
import FormDialog from '../../../components/shared/FormDialog'
import ConfirmDialog from '../../../components/shared/ConfirmDialog'
import PageHeader from '../../../components/shared/PageHeader'
import StatusBadge from '../../../components/shared/StatusBadge'

export default function StudentsPage() {
  const [data, setData] = useState({ results: [] }); const [search, setSearch] = useState(''); const [dialog, setDialog] = useState(false); const [selected, setSelected] = useState(null); const [confirm, setConfirm] = useState(null)
  const load = () => listStudents({ search }).then(({ data: result }) => setData(result))
  useEffect(() => { load().catch(() => toast.error('Unable to load students.')) }, [search])
  const save = (payload) => (selected ? updateStudent(selected.id, payload) : createStudent(payload)).then(() => { toast.success('Student saved.'); setDialog(false); load() }).catch((error) => toast.error(error.response?.data?.detail || 'Unable to save student.'))
  const remove = () => deleteStudent(confirm.id).then(() => { toast.success('Student deleted.'); setConfirm(null); load() }).catch(() => toast.error('Unable to delete student.'))
  const fields = [{ name: 'first_name', label: 'First name', rules: { required: 'First name is required.' } }, { name: 'last_name', label: 'Last name', rules: { required: 'Last name is required.' } }, { name: 'email', label: 'Email', type: 'email', rules: { required: 'Email is required.' } }, { name: 'phone', label: 'Phone' }]
  return <main className="dashboard"><PageHeader title="Students" description="Manage students in your center." actionLabel="Add student" onAction={() => { setSelected(null); setDialog(true) }} /><DataTable columns={[{ key: 'name', label: 'Student', render: (row) => <strong>{row.first_name} {row.last_name}</strong> }, { key: 'email', label: 'Email' }, { key: 'roll_no', label: 'Roll no.' }, { key: 'is_active', label: 'Status', render: (row) => <StatusBadge active={row.is_active} /> }]} rows={data.results || []} search={search} onSearch={setSearch} onEdit={(row) => { setSelected(row); setDialog(true) }} onDelete={setConfirm} /><FormDialog open={dialog} title={`${selected ? 'Edit' : 'Add'} student`} initialValues={selected || {}} fields={fields} onSubmit={save} onCancel={() => setDialog(false)} /><ConfirmDialog open={Boolean(confirm)} title="Delete student?" description="This removes the student account." onCancel={() => setConfirm(null)} onConfirm={remove} /></main>
}
