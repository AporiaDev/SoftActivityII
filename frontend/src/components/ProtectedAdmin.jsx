import { useState, useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { fetchMe } from '../api'

export default function ProtectedAdmin({ children }) {
  const [status, setStatus] = useState('loading') // 'loading' | 'ok' | 'unauthorized'

  useEffect(() => {
    let cancelled = false
    fetchMe()
      .then((data) => {
        if (cancelled) return
        if (!data) setStatus('unauthorized')
        else if (data.rol !== 'admin' || !data.is_staff) setStatus('forbidden')
        else setStatus('ok')
      })
      .catch(() => {
        if (!cancelled) setStatus('unauthorized')
      })
    return () => { cancelled = true }
  }, [])

  if (status === 'loading') {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg)',
        color: 'var(--text-muted)',
      }}>
        Cargando…
      </div>
    )
  }

  if (status === 'unauthorized') {
    return <Navigate to="/admin" replace />
  }

  if (status === 'forbidden') {
    return <Navigate to="/" replace />
  }

  return children
}
