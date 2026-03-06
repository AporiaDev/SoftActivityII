import { Link } from 'react-router-dom'
import styles from './ThankYouPage.module.css'

export default function ThankYouPage() {
  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <h1 className={styles.title}>Gracias</h1>
        <p className={styles.message}>
          Su formulario ha sido enviado correctamente. Agradecemos su participación.
        </p>
        <Link to="/" className={styles.link}>
          Volver al inicio
        </Link>
      </div>
    </div>
  )
}
