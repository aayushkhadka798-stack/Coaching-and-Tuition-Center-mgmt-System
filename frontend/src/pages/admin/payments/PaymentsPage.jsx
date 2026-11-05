import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Card } from '../../../components/ui'
import { listPayments } from '../../../api/feesApi'

export default function PaymentsPage() {
  const [payments, setPayments] = useState([])
  useEffect(() => { listPayments().then(({ data }) => setPayments(data)).catch(() => toast.error('Unable to load payment tracking.')) }, [])
  return <main className="dashboard-content"><div className="profile-header"><div><p className="eyebrow">ADMIN PORTAL</p><h1>Payment tracking</h1><p className="muted">Track confirmed, pending, canceled, failed, and error transactions.</p></div></div><Card><div className="payment-table">{payments.map((payment) => <div className="payment-row" key={payment.id}><div><strong>{payment.transaction_uuid}</strong><p>Fee #{payment.fee} · NPR {payment.amount}</p></div><span className={`payment-status ${payment.status}`}>{payment.status}</span><small>{payment.error_message || payment.gateway_reference || new Date(payment.created_at).toLocaleString()}</small></div>)}{!payments.length && <p className="muted">No payment attempts recorded yet.</p>}</div></Card></main>
}
