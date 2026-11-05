import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { listEnrollments, createEnrollment, updateEnrollment } from '../../../api/academicsApi'
import DataTable from '../../../components/shared/DataTable'
import FormDialog from '../../../components/shared/FormDialog'
import PageHeader from '../../../components/shared/PageHeader'

export default function EnrollmentsPage() {
  const [data, setData] = useState({ results: [] }); const [search, setSearch] = useState(''); const [dialog, setDialog] = useState(false); const [selected, setSelected] = useState(null)
  const load = () => listEnrollments({ search }).then(({ data: result }) => setData(result))
  useEffect(() => { load().catch(() => toast.error('Unable to load enrollments.')) }, [search])
  const save = (payload) => (selected ? updateEnrollment(selected.id, payload) : createEnrollment(payload)).then(() => { toast.success('Enrollment saved.'); setDialog(false); load() }).catch((error) => toast.error(error.response?.data?.detail || 'Unable to save enrollment.'))
  return <main className="dashboard"><PageHeader title="Enrollments" description="Enroll students into center batches." actionLabel="New enrollment" onAction={() => { setSelected(null); setDialog(true) }} /><DataTable columns={[{ key: 'student', label: 'Student ID' }, { key: 'batch', label: 'Batch ID' }, { key: 'status', label: 'Status' }, { key: 'enrolled_on', label: 'Enrolled on' }]} rows={data.results || []} search={search} onSearch={setSearch} onEdit={(row) => { setSelected(row); setDialog(true) }} /><FormDialog open={dialog} title={selected ? 'Edit enrollment' : 'New enrollment'} initialValues={selected || {}} fields={[{ name: 'student', label: 'Student ID', type: 'number', rules: { required: 'Student is required.' } }, { name: 'batch', label: 'Batch ID', type: 'number', rules: { required: 'Batch is required.' } }, { name: 'status', label: 'Status' }]} onSubmit={save} onCancel={() => setDialog(false)} /></main>
}
