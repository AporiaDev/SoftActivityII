import { Routes, Route, Navigate } from 'react-router-dom'
import FormPage from './pages/FormPage'
import ThankYouPage from './pages/ThankYouPage'
import AdminLogin from './pages/AdminLogin'
import RegisterPage from './pages/RegisterPage'
import AdminDashboard from './pages/AdminDashboard'
import ProtectedAdmin from './components/ProtectedAdmin'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<FormPage />} />
      <Route path="/gracias" element={<ThankYouPage />} />
      <Route path="/ingresar" element={<AdminLogin />} />
      <Route path="/ingresar/registro" element={<RegisterPage />} />
      <Route path="/admin" element={<AdminLogin />} />
      <Route path="/admin/registro" element={<RegisterPage />} />
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedAdmin>
            <AdminDashboard />
          </ProtectedAdmin>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
