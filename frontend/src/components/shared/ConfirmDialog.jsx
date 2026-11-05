import { AlertTriangle, Trash2 } from 'lucide-react'

export default function ConfirmDialog({ open, title, description, confirmLabel = 'Confirm', variant = 'danger', onConfirm, onCancel }) {
  if (!open) return null
  return <div className="dialog-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onCancel()}>
    <section className="dialog-card" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title">
      <div className={`dialog-icon ${variant}`}>{variant === 'danger' ? <Trash2 size={20} /> : <AlertTriangle size={20} />}</div>
      <h2 id="confirm-title">{title}</h2>
      <p>{description}</p>
      <div className="dialog-actions">
        <button type="button" className="ui-button ui-button-outline" onClick={onCancel}>Cancel</button>
        <button type="button" className={`ui-button ${variant === 'danger' ? 'ui-button-danger' : ''}`} onClick={onConfirm}>{confirmLabel}</button>
      </div>
    </section>
  </div>
}
