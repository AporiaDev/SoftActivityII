import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { fetchMe, fetchQuestions, submitAnswers } from '../api'
import styles from './FormPage.module.css'

export default function FormPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [authChecked, setAuthChecked] = useState(false)
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [answers, setAnswers] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)

  useEffect(() => {
    fetchMe()
      .then((data) => {
        setUser(data)
        setAuthChecked(true)
      })
      .catch(() => setAuthChecked(true))
  }, [])

  useEffect(() => {
    if (!authChecked || !user) return
    fetchQuestions()
      .then(setQuestions)
      .catch(() => setError('No se pudieron cargar las preguntas.'))
      .finally(() => setLoading(false))
  }, [authChecked, user])

  const handleChange = (questionId, value) => {
    setAnswers((prev) => ({ ...prev, [questionId]: parseInt(value, 10) }))
    setSubmitError(null)
  }

  const allAnswered = questions.length > 0 && questions.every((q) => answers[q.id] >= 1 && answers[q.id] <= 10)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!allAnswered) return
    setSubmitting(true)
    setSubmitError(null)
    const payload = questions.map((q) => ({ question_id: q.id, value: answers[q.id] }))
    submitAnswers(payload)
      .then(() => navigate('/gracias', { replace: true }))
      .catch((err) => {
        setSubmitError(err.message || 'Error al enviar. Intente de nuevo.')
        setSubmitting(false)
      })
  }

  if (!authChecked || (authChecked && !user)) {
    return (
      <div className={styles.wrapper}>
        <div className={styles.gate}>
          <h1 className={styles.gateTitle}>Evaluación de perfiles</h1>
          <p className={styles.gateMessage}>
            Para responder la encuesta debe ingresar con su nombre y cédula.
          </p>
          <Link to="/ingresar" className={styles.gateBtn}>
            Ingresar para responder
          </Link>
          <p className={styles.gateFooter}>
            <Link to="/admin">Soy administrador</Link>
          </p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className={styles.wrapper}>
        <div className={styles.loading}>Cargando formulario…</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={styles.wrapper}>
        <div className={styles.error}>{error}</div>
      </div>
    )
  }

  return (
    <div className={styles.wrapper}>
      <header className={styles.header}>
        <h1 className={styles.title}>Evaluación de perfiles</h1>
        <p className={styles.subtitle}>
          Responda cada afirmación según su grado de acuerdo (1 = muy en desacuerdo, 10 = muy de acuerdo).
        </p>
        <p className={styles.userInfo}>Conectado como: {user.nombre || user.username}</p>
      </header>

      <form onSubmit={handleSubmit} className={styles.form}>
        <ol className={styles.list}>
          {questions.map((q) => (
            <li key={q.id} className={styles.item}>
              <p className={styles.questionText}>{q.text}</p>
              <div className={styles.scale}>
                <span className={styles.scaleLabel}>1</span>
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={answers[q.id] ?? 5}
                  onChange={(e) => handleChange(q.id, e.target.value)}
                  className={styles.slider}
                />
                <span className={styles.scaleLabel}>10</span>
                <span className={styles.value}>{answers[q.id] ?? 5}</span>
              </div>
            </li>
          ))}
        </ol>

        {submitError && <p className={styles.submitError}>{submitError}</p>}

        <button
          type="submit"
          className={styles.submitBtn}
          disabled={!allAnswered || submitting}
        >
          {submitting ? 'Enviando…' : 'Enviar respuestas'}
        </button>
      </form>

      <footer className={styles.footer}>
        <Link to="/admin">Acceso administrador</Link>
      </footer>
    </div>
  )
}
