import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Card, Button } from '../../components/ui'
import { CreditCard } from 'lucide-react'
import StudentPageShell from '../../components/student/StudentPageShell'
import { listFees, listStudentPayments, initiateEsewa } from '../../api/feesApi'

export default function FeesPage() {
  const [fees, setFees] = useState([])
  const [payments, setPayments] = useState([])
  const [selectedFee, setSelectedFee] = useState(null)
  const [amount, setAmount] = useState('')
  const [paying, setPaying] = useState(false)
  useEffect(() => { Promise.all([listFees(), listStudentPayments()]).then(([feeResult, paymentResult]) => { setFees(feeResult.data.results || feeResult.data); setPayments(paymentResult.data.results || paymentResult.data) }).catch(() => toast.error('Unable to load fees.')) }, [])
  const openPayment = (fee) => { setSelectedFee(fee); setAmount(fee.balance) }
  const pay = () => {
    if (!selectedFee || Number(amount) <= 0 || Number(amount) > Number(selectedFee.balance)) return toast.error('Enter an amount within the outstanding balance.')
    setPaying(true)
    initiateEsewa({ fee_id: selectedFee.id, amount }).then(({ data }) => {
    const form = document.createElement('form'); form.method = 'POST'; form.action = data.form_url
    Object.entries(data.fields).forEach(([name, value]) => { const input = document.createElement('input'); input.type = 'hidden'; input.name = name; input.value = value; form.appendChild(input) })
    document.body.appendChild(form); form.submit()
    }).catch((e) => { setPaying(false); toast.error(e.response?.data?.detail || 'Unable to start eSewa payment.') })
  }
  return <StudentPageShell activePath="fees" title="Fees & payments"><header className="profile-header"><div><p className="eyebrow">STUDENT PORTAL</p><h1>My fees</h1><p className="muted">View your balance and pay securely with eSewa Sandbox.</p></div></header><div className="fee-list">{fees.map((fee) => <Card key={fee.id}><strong>Fee #{fee.id}</strong><p>Due: NPR {fee.amount_due} · Paid: NPR {fee.paid_amount}</p><p>Status: {fee.status}</p>{Number(fee.balance) > 0 && <Button className="esewa-button" onClick={() => openPayment(fee)}><img src="/esewa-logo.png" alt="" />Pay with eSewa</Button>}</Card>)}{!fees.length && <Card><p className="muted">No fee records yet.</p></Card>}</div><Card><h2>Payment history</h2>{payments.map((payment) => <div className="student-list-row" key={payment.id}><span>{new Date(payment.created_at).toLocaleDateString()}</span><strong>NPR {payment.amount}</strong><span>{payment.method || 'eSewa'} · {payment.status}</span></div>)}{!payments.length && <p className="muted">No payments recorded yet.</p>}</Card>{selectedFee && <div className="dialog-backdrop"><section className="dialog-card" role="dialog" aria-modal="true" aria-labelledby="esewa-title"><img className="esewa-dialog-logo" src="/esewa-logo.png" alt="eSewa" /><h2 id="esewa-title">Pay with eSewa</h2><p className="muted">Outstanding balance: NPR {selectedFee.balance}</p><label>Amount<input className="ui-input" type="number" min="0.01" max={selectedFee.balance} step="0.01" value={amount} onChange={(event) => setAmount(event.target.value)} /></label><div className="dialog-actions"><Button variant="outline" onClick={() => setSelectedFee(null)} disabled={paying}>Cancel</Button><Button className="esewa-button" onClick={pay} disabled={paying}><CreditCard size={16} />{paying ? 'Redirecting...' : 'Continue to eSewa'}</Button></div></section></div>}</StudentPageShell>
}
