import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { listCourses, createCourse, updateCourse, deleteCourse, listBatches, createBatch, updateBatch, deleteBatch } from '../../../api/academicsApi'
import { listTeachers } from '../../../api/teacherApi'
import DataTable from '../../../components/shared/DataTable'
import FormDialog from '../../../components/shared/FormDialog'
import ConfirmDialog from '../../../components/shared/ConfirmDialog'
import PageHeader from '../../../components/shared/PageHeader'

export default function ResourceListPage({ type }) {
  const courses = type === 'courses'
  const [data, setData] = useState({ results: [] })
  const [search, setSearch] = useState('')
  const [dialog, setDialog] = useState(false)
  const [selected, setSelected] = useState(null)
  const [confirm, setConfirm] = useState(null)
  const [courseOptions, setCourseOptions] = useState([])
  const [teacherOptions, setTeacherOptions] = useState([])
  const load = () => (courses ? listCourses({ search }) : listBatches({ search })).then(({ data: result }) => setData(result))
  useEffect(() => { load().catch(() => toast.error(`Unable to load ${type}.`)) }, [search, type])
  useEffect(() => {
    if (!courses) {
      Promise.all([listCourses({ is_active: true, page_size: 100 }), listTeachers({ is_active: true, page_size: 100 })])
        .then(([courseResponse, teacherResponse]) => {
          const courseData = courseResponse.data.results || courseResponse.data
          const teacherData = teacherResponse.data.results || teacherResponse.data
          setCourseOptions(courseData.map((item) => ({ value: item.id, label: `${item.name} · Rs. ${item.fee_amount}` })))
          setTeacherOptions(teacherData.map((item) => ({ value: item.id, label: `${item.first_name} ${item.last_name}`.trim() || item.email })))
        })
        .catch(() => toast.error('Unable to load course and teacher options.'))
    }
  }, [courses])
  const save = (payload) => {
    const request = selected
      ? (courses ? updateCourse(selected.id, payload) : updateBatch(selected.id, payload))
      : (courses ? createCourse(payload) : createBatch(payload))
    request.then(() => { toast.success(`${courses ? 'Course' : 'Batch'} saved.`); setDialog(false); load() }).catch((error) => {
      const response = error.response?.data || {}
      const fieldError = Object.entries(response).find(([, value]) => Array.isArray(value) && value.length)
      toast.error(fieldError ? `${fieldError[0]}: ${fieldError[1][0]}` : response.detail || 'Unable to save.')
    })
  }
  const remove = () => (courses ? deleteCourse(confirm.id) : deleteBatch(confirm.id)).then(() => { toast.success('Deleted.'); setConfirm(null); load() }).catch(() => toast.error('Cannot delete this record.'))
  const fields = courses ? [{ name: 'name', label: 'Name', rules: { required: 'Name is required.' } }, { name: 'description', label: 'Description' }, { name: 'fee_amount', label: 'Fee amount (NPR)', type: 'number' }] : [{ name: 'name', label: 'Name', rules: { required: 'Name is required.' } }, { name: 'course', label: 'Course', type: 'select', options: courseOptions, rules: { required: 'Course is required.' } }, { name: 'teacher', label: 'Teacher', type: 'select', options: teacherOptions, rules: { required: 'Teacher is required.' } }, { name: 'start_date', label: 'Start date', type: 'date', rules: { required: 'Start date is required.' } }, { name: 'end_date', label: 'End date', type: 'date' }, { name: 'capacity', label: 'Capacity', type: 'number', rules: { min: { value: 1, message: 'Capacity must be at least 1.' } } }]
  return <main className="dashboard"><PageHeader title={courses ? 'Courses' : 'Batches'} description={`Manage ${type} in your center.`} actionLabel={`Add ${courses ? 'course' : 'batch'}`} onAction={() => { setSelected(null); setDialog(true) }} /><DataTable columns={courses ? [{ key: 'name', label: 'Name' }, { key: 'fee_amount', label: 'Fee (NPR)', render: (row) => `Rs. ${row.fee_amount}` }, { key: 'is_active', label: 'Status' }] : [{ key: 'name', label: 'Name' }, { key: 'course', label: 'Course' }, { key: 'teacher', label: 'Teacher' }, { key: 'capacity', label: 'Capacity' }]} rows={data.results || []} search={search} onSearch={setSearch} onEdit={(row) => { setSelected(row); setDialog(true) }} onDelete={setConfirm} /><FormDialog open={dialog} title={`${selected ? 'Edit' : 'Add'} ${courses ? 'course' : 'batch'}`} initialValues={selected || {}} fields={fields} onSubmit={save} onCancel={() => setDialog(false)} /><ConfirmDialog open={Boolean(confirm)} title="Delete record?" description="This action cannot be undone." onCancel={() => setConfirm(null)} onConfirm={remove} /></main>
}
