import { useEffect } from 'react'
import { Pencil } from 'lucide-react'
import { useForm } from 'react-hook-form'

export default function FormDialog({ open, title, initialValues, fields, onSubmit, onCancel, saving = false }) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm({ defaultValues: initialValues })
  useEffect(() => { if (open) reset(initialValues) }, [open, initialValues, reset])
  if (!open) return null
  return <div className="dialog-backdrop">
    <section className="dialog-card form-dialog" role="dialog" aria-modal="true" aria-labelledby="form-title">
      <div className="dialog-icon"><Pencil size={20} /></div>
      <h2 id="form-title">{title}</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="dialog-form">
        {fields.map((field) => <label key={field.name}><span>{field.label}</span>{field.type === 'select' ? <select className="ui-input" {...register(field.name, field.rules)}><option value="">Select {field.label.toLowerCase()}</option>{field.options?.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select> : <input type={field.type || 'text'} {...register(field.name, field.rules)} />}{errors[field.name] && <small className="error">{errors[field.name].message || 'This field is required.'}</small>}</label>)}
        <div className="dialog-actions"><button type="button" className="ui-button ui-button-outline" onClick={onCancel}>Cancel</button><button type="submit" className="ui-button" disabled={saving}>{saving ? 'Saving...' : 'Save changes'}</button></div>
      </form>
    </section>
  </div>
}
