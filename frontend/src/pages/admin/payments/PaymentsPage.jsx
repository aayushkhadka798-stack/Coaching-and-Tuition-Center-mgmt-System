import { useEffect, useMemo, useState } from 'react'
import { toast } from 'sonner'
import { Card } from '../../../components/ui'
import { listEsewaTransactions, listPayments } from '../../../api/feesApi'
import AdminPageShell from '../../../components/dashboard/AdminPageShell'
import PageHeader from '../../../components/shared/PageHeader'
import EmptyState from '../../../components/shared/EmptyState'

export default function PaymentsPage() {
  const [payments, setPayments] = useState([])
  const [online, setOnline] = useState([])
  const [tab, setTab] = useState('history')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  useEffect(() => {
    Promise.all([listPayments(), listEsewaTransactions()]).then(([paymentResult, onlineResult]) => { setPayments(paymentResult.data); setOnline(onlineResult.data) }).catch(() => toast.error('Unable to load payment tracking.'))
  }, [])
  const filteredPayments = useMemo(() => payments.filter((payment) => {
    const text = `${payment.student?.name || ''} ${payment.student?.email || ''} ${payment.fee?.id || ''} ${payment.method || ''} ${payment.transaction_reference || ''}`.toLowerCase()
    return (!search || text.includes(search.toLowerCase())) && (statusFilter === 'all' || payment.status === statusFilter)
  }), [payments, search, statusFilter])
  const filteredOnline = useMemo(() => online.filter((item) => {
    const text = `${item.student?.name || ''} ${item.student?.email || ''} ${item.fee?.id || ''} ${item.transaction_uuid || ''}`.toLowerCase()
    return (!search || text.includes(search.toLowerCase())) && (statusFilter === 'all' || item.status === statusFilter.toUpperCase())
  }), [online, search, statusFilter])
  const confirmed = payments.filter((payment) => payment.status === 'confirmed').reduce((total, payment) => total + Number(payment.amount || 0), 0)
  const pending = payments.filter((payment) => ['pending', 'initiated'].includes(payment.status)).length
  const visibleRows = tab === 'history' ? filteredPayments : filteredOnline
  return <AdminPageShell activePath="payments" title="Payments"><PageHeader title="Payment tracking" description="See who paid, which fee it belongs to, and how the payment was received." /><div className="payment-summary-grid"><div className="payment-summary-card"><span>Confirmed collected</span><strong>Rs. {confirmed.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong><small>From recorded payments</small></div><div className="payment-summary-card"><span>Total payments</span><strong>{payments.length}</strong><small>Cash, bank and eSewa</small></div><div className="payment-summary-card"><span>Awaiting confirmation</span><strong>{pending}</strong><small>Initiated or pending</small></div></div><Card className="payment-tracker"><div className="payment-toolbar"><div className="payment-tabs"><button className={tab === 'history' ? 'active' : ''} onClick={() => setTab('history')}>All payments <b>{payments.length}</b></button><button className={tab === 'online' ? 'active' : ''} onClick={() => setTab('online')}>eSewa activity <b>{online.length}</b></button></div><div className="payment-filters"><input aria-label="Search payments" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search student, fee or reference" /><select aria-label="Filter payment status" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="all">All statuses</option><option value={tab === 'online' ? 'complete' : 'confirmed'}>{tab === 'online' ? 'Complete' : 'Confirmed'}</option><option value={tab === 'online' ? 'pending' : 'pending'}>Pending</option><option value={tab === 'online' ? 'failed' : 'failed'}>Failed</option></select></div></div>{visibleRows.length ? <div className="payment-ledger"><div className="payment-ledger-head"><span>Student</span><span>Fee</span><span>Amount</span><span>Method</span><span>Status</span><span>Date</span></div>{tab === 'history' ? filteredPayments.map((payment) => <div className="payment-ledger-row" key={payment.id}><div className="student-payment"><span className="payment-avatar">{(payment.student?.name || 'S')[0].toUpperCase()}</span><div><strong>{payment.student?.name || 'Unknown student'}</strong><small>{payment.student?.email || 'No email'}</small></div></div><div><strong>Fee #{payment.fee?.id || '—'}</strong><small>{payment.fee?.status || 'No status'}</small></div><strong>Rs. {Number(payment.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong><span className="method-pill">{payment.method === 'esewa' ? 'eSewa' : payment.method || 'Cash'}</span><span className={`payment-status ${payment.status}`}>{payment.status}</span><small>{new Date(payment.created_at).toLocaleDateString()}</small></div>) : filteredOnline.map((item) => <div className="payment-ledger-row" key={item.id}><div className="student-payment"><span className="payment-avatar">{(item.student?.name || item.student?.email || 'S')[0].toUpperCase()}</span><div><strong>{item.student?.name || 'Unknown student'}</strong><small>{item.student?.email || 'No email'}</small></div></div><div><strong>Fee #{item.fee?.id || '—'}</strong><small>{item.transaction_uuid}</small></div><strong>Rs. {Number(item.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong><span className="method-pill esewa">eSewa</span><span className={`payment-status ${item.status.toLowerCase()}`}>{item.status}</span><small>{new Date(item.created_at).toLocaleDateString()}</small></div>)}</div> : <EmptyState title="No payment records found" description="Try changing the search or status filter." />}</Card></AdminPageShell>
}
