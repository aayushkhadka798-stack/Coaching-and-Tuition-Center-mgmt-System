import { AuthProvider } from './context/AuthContext'
import AppRoutes from './routes/AppRoutes'
import './App.css'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'

const queryClient = new QueryClient()
export default function App() {
  return <QueryClientProvider client={queryClient}><AuthProvider><AppRoutes /></AuthProvider><Toaster position="top-right" richColors /></QueryClientProvider>
}
