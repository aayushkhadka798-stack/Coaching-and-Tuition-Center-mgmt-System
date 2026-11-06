import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Card, Button } from '../../components/ui'
import { failEsewa, verifyEsewa } from '../../api/feesApi'

export function EsewaSuccessPage() {
  const [params] = useSearchParams()
  const [state, setState] = useState({ loading: true })
  const submitted = useRef(false)
  useEffect(() => {
    if (submitted.current) return
    submitted.current = true
    const data = params.get('data')
    if (!data) return setState({ loading: false, error: 'The eSewa response was missing.' })
    verifyEsewa({ data }).then(({ data: result }) => setState({ loading: false, result })).catch((error) => setState({ loading: false, error: error.response?.data?.detail || 'Unable to verify this payment.' }))
  }, [params])
  return <main className="dashboard-content"><Card><p className="eyebrow">eSEWA PAYMENT</p>{state.loading ? <h1>Confirming your payment...</h1> : state.error ? <><h1>Payment verification failed</h1><p className="error">{state.error}</p></> : <><h1>Payment successful</h1><p>Paid NPR {state.result.payment.amount}. Reference: {state.result.payment.gateway_reference || 'Confirmed'}</p><p>New balance: NPR {state.result.fee.balance}</p></>}<Link to="/student/fees"><Button>Back to fees</Button></Link></Card></main>
}

export function EsewaFailurePage() {
  const [params] = useSearchParams()
  const [message, setMessage] = useState('Your payment was canceled or could not be completed.')
  const submitted = useRef(false)
  useEffect(() => {
    if (submitted.current) return
    let transactionUuid = params.get('transaction_uuid')
    if (!transactionUuid && params.get('data')) {
      try {
        const encoded = params.get('data')
        const decoded = atob(encoded + '='.repeat((4 - encoded.length % 4) % 4))
        transactionUuid = JSON.parse(decoded).transaction_uuid
      } catch {
        transactionUuid = null
      }
    }
    if (!transactionUuid) return
    submitted.current = true
    failEsewa({ transaction_uuid: transactionUuid }).catch(() => setMessage('The payment could not be completed. You can try again from your fees page.'))
  }, [params])
  return <main className="dashboard-content"><Card><p className="eyebrow">eSEWA PAYMENT</p><h1>Payment canceled</h1><p>{message}</p><Link to="/student/fees"><Button>Try again</Button></Link></Card></main>
}
