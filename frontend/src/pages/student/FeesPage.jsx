import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Card, Button } from '../../components/ui'
import { listFees, initiateEsewa } from '../../api/feesApi'

export default function FeesPage() {
  const [fees, setFees] = useState([])
  useEffect(() => { listFees().then(({ data }) => setFees(data)).catch(() => toast.error('Unable to load fees.')) }, [])
  const pay = (fee) => initiateEsewa({ fee_id: fee.id, amount: fee.balance, success_url: `${window.location.origin}/student/fees?payment=success`, failure_url: `${window.location.origin}/student/fees?payment=failed` }).then(({ data }) => {
    const form = document.createElement('form'); form.method = 'POST'; form.action = data.gateway_url
    Object.entries(data.fields).forEach(([name, value]) => { const input = document.createElement('input'); input.type = 'hidden'; input.name = name; input.value = value; form.appendChild(input) })
    document.body.appendChild(form); form.submit()
  }).catch((e) => toast.error(e.response?.data?.detail || 'Unable to start eSewa payment.'))
  return <main className="dashboard-content"><div className="profile-header"><div><p className="eyebrow">STUDENT PORTAL</p><h1>My fees</h1><p className="muted">View your balance and pay securely with eSewa Sandbox.</p></div></div><div className="fee-list">{fees.map((fee) => <Card key={fee.id}><strong>Fee #{fee.id}</strong><p>Due: NPR {fee.amount_due} · Paid: NPR {fee.paid_amount}</p><p>Status: {fee.status}</p>{Number(fee.balance) > 0 && <Button onClick={() => pay(fee)}>Pay NPR {fee.balance} with eSewa</Button>}</Card>)}{!fees.length && <Card><p className="muted">No fee records yet.</p></Card>}</div></main>
}
