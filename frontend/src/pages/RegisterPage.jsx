import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { fetchCsrf, register } from '../api'
import styles from './RegisterPage.module.css'

const ROL_RESPONDER = 'responder'
const ROL_ADMIN = 'admin'

export default function RegisterPage() {
  const location = useLocation()
  const isIngresarFlow = location.pathname.startsWith('/ingresar')
  const loginPath = isIngresarFlow ? '/ingresar' : '/admin'
  const [rol, setRol] = useState(ROL_RESPONDER)
  const [nombre, setNombre] = useState('')
  const [cedula, setCedula] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    fetchCsrf().catch(() => {})
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    register(nombre, cedula, rol)
      .then(() => setSuccess(true))
      .catch((err) => {
        setError(err.message || 'Error al registrarse')
        setLoading(false)
      })
  }

  if (success) {
    return (
      <div className={styles.wrapper}>
        <div className={styles.card}>
          <h1 className={styles.title}>Registro exitoso</h1>
          <p className={styles.message}>
            Ya puede ingresar con su nombre y cédula.
          </p>
          <Link to={loginPath} className={styles.btn}>
            Ir a ingresar
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <h1 className={styles.title}>Registrarse</h1>
        <p className={styles.subtitle}>Cree su cuenta con nombre y cédula. Elija si será usuario que responde la encuesta o administrador.</p>

        <div className={styles.rolSelector}>
          <div className={styles.rolOptions}>
            <label className={styles.rolOption}>
              <input
                type="radio"
                name="rol"
                value={ROL_RESPONDER}
                checked={rol === ROL_RESPONDER}
                onChange={() => setRol(ROL_RESPONDER)}
              />
              <span>Usuario que responde la encuesta</span>
            </label>
            <label className={styles.rolOption}>
              <input
                type="radio"
                name="rol"
                value={ROL_ADMIN}
                checked={rol === ROL_ADMIN}
                onChange={() => setRol(ROL_ADMIN)}
              />
              <span>Administrador</span>
            </label>
          </div>
        </div>

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
            {loading ? 'Registrando…' : 'Registrarse'}
          </button>
        </form>

        <p className={styles.footer}>
          ¿Ya tiene cuenta? <Link to={loginPath}>Ingresar</Link>
        </p>
        <p className={styles.back}>
          <Link to="/">← Volver al inicio</Link>
        </p>
      </div>
    </div>
  )
}
