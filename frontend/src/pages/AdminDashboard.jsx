import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
import { fetchStats, logout, downloadCsv, downloadExcel } from '../api'
import styles from './AdminDashboard.module.css'

const TYPE_LABELS = { a: 'Tipo A', b: 'Tipo B', c: 'Tipo C', d: 'Tipo D' }
const COLORS = ['#c9a227', '#6b8e6b', '#8b6b9e', '#c97a5c']

export default function AdminDashboard() {
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [exporting, setExporting] = useState(null) // 'csv' | 'xlsx' | null
  const [exportError, setExportError] = useState(null)

  useEffect(() => {
    fetchStats()
      .then(setStats)
      .catch(() => setError('No se pudieron cargar las estadísticas.'))
      .finally(() => setLoading(false))
  }, [])

  const handleLogout = () => {
    logout().then(() => navigate('/admin', { replace: true }))
  }

  const chartData = stats
    ? ['a', 'b', 'c', 'd'].map((t) => ({
        name: TYPE_LABELS[t],
        tipo: t,
        cantidad: stats.distribution[t] ?? 0,
      }))
    : []

  const triggerDownload = (blob, filename) => {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleExportCsv = () => {
    setExporting('csv')
    downloadCsv()
      .then((blob) => {
        triggerDownload(blob, 'evaluacion_respuestas.csv')
        setExportError(null)
      })
      .catch(() => setExportError('Error al exportar CSV'))
      .finally(() => setExporting(null))
  }

  const handleExportExcel = () => {
    setExporting('xlsx')
    downloadExcel()
      .then((blob) => {
        triggerDownload(blob, 'evaluacion_respuestas.xlsx')
        setExportError(null)
      })
      .catch(() => setExportError('Error al exportar Excel'))
      .finally(() => setExporting(null))
  }

  if (loading) {
    return (
      <div className={styles.wrapper}>
        <div className={styles.loading}>Cargando dashboard…</div>
      </div>
    )
  }

  if (error && !stats) {
    return (
      <div className={styles.wrapper}>
        <div className={styles.error}>{error}</div>
        <button type="button" onClick={() => navigate('/admin')} className={styles.backBtn}>
          Volver al login
        </button>
      </div>
    )
  }

  return (
    <div className={styles.wrapper}>
      <header className={styles.header}>
        <h1 className={styles.title}>Dashboard</h1>
        <div className={styles.actions}>
          <a href="/">Formulario</a>
          <button type="button" onClick={handleLogout} className={styles.logoutBtn}>
            Cerrar sesión
          </button>
        </div>
      </header>

      <section className={styles.metrics}>
        <div className={styles.metricCard}>
          <span className={styles.metricValue}>{stats?.total_submissions ?? 0}</span>
          <span className={styles.metricLabel}>Total de envíos</span>
        </div>
      </section>

      <section className={styles.charts}>
        <div className={styles.chartCard}>
          <h2 className={styles.chartTitle}>Distribución por tipo de perfil</h2>
          <div className={styles.chartWrapper}>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData} margin={{ top: 16, right: 16, left: 16, bottom: 16 }}>
                <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} />
                <YAxis stroke="var(--text-muted)" fontSize={12} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    background: 'var(--surface)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: 'var(--text)' }}
                />
                <Bar dataKey="cantidad" fill="var(--accent)" radius={[4, 4, 0, 0]} name="Usuarios" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className={styles.chartCard}>
          <h2 className={styles.chartTitle}>Proporción por tipo</h2>
          <div className={styles.chartWrapper}>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={chartData}
                  dataKey="cantidad"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  label={({ name, cantidad }) => (cantidad > 0 ? `${name}: ${cantidad}` : '')}
                >
                  {chartData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'var(--surface)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className={styles.export}>
        <h2 className={styles.exportTitle}>Exportar datos</h2>
        <div className={styles.exportButtons}>
          <button
            type="button"
            onClick={handleExportCsv}
            disabled={!!exporting}
            className={styles.exportBtn}
          >
            {exporting === 'csv' ? 'Exportando…' : 'Exportar CSV'}
          </button>
          <button
            type="button"
            onClick={handleExportExcel}
            disabled={!!exporting}
            className={styles.exportBtn}
          >
            {exporting === 'xlsx' ? 'Exportando…' : 'Exportar Excel'}
          </button>
        </div>
        {exportError && <p className={styles.exportError}>{exportError}</p>}
      </section>
    </div>
  )
}
