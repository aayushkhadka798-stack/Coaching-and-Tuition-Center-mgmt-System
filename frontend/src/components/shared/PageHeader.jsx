import { Plus } from 'lucide-react'

export default function PageHeader({ title, description, actionLabel, onAction }) {
  return <header className="page-header"><div><p className="eyebrow">ADMINISTRATION</p><h1>{title}</h1><p className="muted">{description}</p></div>{onAction && <button className="ui-button" onClick={onAction}><Plus size={17} />{actionLabel}</button>}</header>
}
