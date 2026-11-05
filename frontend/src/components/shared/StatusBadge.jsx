export default function StatusBadge({ active }) {
  return <span className={`status-badge ${active ? 'active' : 'inactive'}`}>{active ? 'Active' : 'Inactive'}</span>
}
