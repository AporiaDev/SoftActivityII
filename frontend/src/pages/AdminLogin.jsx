import { useState, useEffect } from 'react'
import { useNavigate, Link, useLocation } from 'react-router-dom'
import { fetchCsrf, login } from '../api'
import styles from './AdminLogin.module.css'

export default function AdminLogin() {
  const navigate = useNavigate()
  const location = useLocation()
  const isIngresarRoute = location.pathname === '/ingresar'
  const [nombre, setNombre] = useState('')
  const [cedula, setCedula] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchCsrf().catch(() => {})
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    login(nombre, cedula)
      .then((data) => {
        const rol = data.rol || 'responder'
        if (rol === 'admin' && data.is_staff) {
          navigate('/admin/dashboard', { replace: true })
          return
        }
        if (rol === 'admin' && !data.is_staff) {
          setError('No tiene permisos de administrador. Un administrador debe activar su cuenta.')
          setLoading(false)
          return
        }
        navigate('/', { replace: true })
      })
      .catch((err) => {
        setError(err.message || 'Error al iniciar sesión')
        setLoading(false)
      })
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <h1 className={styles.title}>Ingresar</h1>
        <p className={styles.subtitle}>Use su nombre y cédula para entrar</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <p className={styles.error}>{error}</p>}
          <label className={styles.label}>
            Nombre completo
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              autoComplete="name"
              required
              className={styles.input}
              placeholder="Ej. Juan Pérez"
            />
          </label>
          <label className={styles.label}>
            Cédula
            <input
              type="text"
              value={cedula}
              onChange={(e) => setCedula(e.target.value)}
              required
              className={styles.input}
              placeholder="Número de documento"
            />
          </label>
          <button type="submit" className={styles.btn} disabled={loading}>
            {loading ? 'Entrando…' : 'Entrar'}
          </button>
        </form>

        <p className={styles.footer}>
          ¿Aún no tiene cuenta? <Link to={isIngresarRoute ? '/ingresar/registro' : '/admin/registro'}>Registrarse</Link>
        </p>
        <p className={styles.back}>
          <Link to="/">← Volver al inicio</Link>
        </p>
      </div>
    </div>
  )
}
