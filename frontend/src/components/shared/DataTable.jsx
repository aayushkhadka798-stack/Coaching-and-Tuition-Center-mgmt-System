import { Eye, MoreHorizontal, Pencil, Search, Trash2 } from 'lucide-react'

export default function DataTable({ columns, rows, loading, error, search, onSearch, onEdit, onView, onDelete, onToggle, onReset, pagination }) {
  return <div className="data-table-shell">
    <div className="table-toolbar"><div className="table-search"><Search size={17} /><input value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Search teachers..." /></div></div>
    <div className="table-scroll"><table className="data-table"><thead><tr>{columns.map((column) => <th key={column.key}>{column.label}</th>)}<th>Actions</th></tr></thead><tbody>
      {loading ? [...Array(5)].map((_, index) => <tr key={index}><td colSpan={columns.length + 1}><div className="skeleton-row" /></td></tr>) : error ? <tr><td colSpan={columns.length + 1} className="table-empty">Unable to load records.</td></tr> : rows.length === 0 ? <tr><td colSpan={columns.length + 1} className="table-empty">No records found.</td></tr> : rows.map((row) => <tr key={row.id}>{columns.map((column) => <td key={column.key}>{column.render ? column.render(row) : row[column.key]}</td>)}<td><div className="row-actions">{onView && <button aria-label="View" onClick={() => onView(row)}><Eye size={16} /></button>}{onEdit && <button aria-label="Edit" onClick={() => onEdit(row)}><Pencil size={16} /></button>}{onReset && <button className="text-action" onClick={() => onReset(row)}>Reset password</button>}{onToggle && <button className="text-action" onClick={() => onToggle(row)}>{row.is_active ? 'Deactivate' : 'Activate'}</button>}{onDelete && <button aria-label="Delete" onClick={() => onDelete(row)}><Trash2 size={16} /></button>}<MoreHorizontal size={16} /></div></td></tr>)}
    </tbody></table></div>
    {pagination && <div className="table-pagination"><span>Page {pagination.page}</span><div><button disabled={!pagination.previous} onClick={() => pagination.go(pagination.page - 1)}>Previous</button><button disabled={!pagination.next} onClick={() => pagination.go(pagination.page + 1)}>Next</button></div></div>}
  </div>
}
