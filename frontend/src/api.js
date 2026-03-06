/**
 * Cliente API hacia el backend Django.
 * Usar proxy en dev: /api -> http://127.0.0.1:8000/api
 */

const BASE = '/api';

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : null;
}

async function apiFetch(path, options = {}) {
  const url = path.startsWith('http') ? path : `${BASE}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  const method = (options.method || 'GET').toUpperCase();
  if (method !== 'GET' && method !== 'HEAD') {
    const csrf = getCsrfToken();
    if (csrf) headers['X-CSRFToken'] = csrf;
  }
  const config = {
    ...options,
    headers,
    credentials: 'include',
  };
  const res = await fetch(url, config);
  return res;
}

/** Obtener token CSRF (llamar antes del primer POST si usas sesión). */
export async function fetchCsrf() {
  const res = await apiFetch('/csrf/');
  const data = await res.json();
  return data.csrfToken;
}

/** Lista de preguntas (público). */
export async function fetchQuestions() {
  const res = await apiFetch('/questions/');
  if (!res.ok) throw new Error('Error al cargar preguntas');
  return res.json();
}

/** Enviar respuestas del formulario (público). */
export async function submitAnswers(answers) {
  const res = await apiFetch('/submit/', {
    method: 'POST',
    body: JSON.stringify({ answers }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.answers || data.detail || 'Error al enviar');
  return data;
}

/** Registro con nombre, cédula y rol (responder | admin). */
export async function register(nombre, cedula, rol = 'responder') {
  const res = await apiFetch('/register/', {
    method: 'POST',
    body: JSON.stringify({
      nombre: nombre.trim(),
      cedula: (cedula || '').trim(),
      rol: rol === 'admin' ? 'admin' : 'responder',
    }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Error al registrarse');
  return data;
}

/** Login con nombre y cédula. */
export async function login(nombre, cedula) {
  const res = await apiFetch('/login/', {
    method: 'POST',
    body: JSON.stringify({ nombre: nombre.trim(), cedula: (cedula || '').trim() }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Error al iniciar sesión');
  return data;
}

/** Logout admin. */
export async function logout() {
  await apiFetch('/logout/', { method: 'POST' });
}

/** Comprobar sesión admin. */
export async function fetchMe() {
  const res = await apiFetch('/me/');
  if (res.status === 401) return null;
  if (!res.ok) return null;
  return res.json();
}

/** Estadísticas para el dashboard (requiere auth). */
export async function fetchStats() {
  const res = await apiFetch('/stats/');
  if (!res.ok) throw new Error('No autorizado o error del servidor');
  return res.json();
}

/** Descargar CSV (requiere auth). Devuelve blob para guardar. */
export async function downloadCsv() {
  const res = await apiFetch('/export/csv/');
  if (!res.ok) throw new Error('Error al exportar');
  return res.blob();
}

/** Descargar Excel (requiere auth). */
export async function downloadExcel() {
  const res = await apiFetch('/export/xlsx/');
  if (!res.ok) throw new Error('Error al exportar');
  return res.blob();
}
