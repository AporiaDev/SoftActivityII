# Frontend - Evaluación de Perfiles

React (Vite) + React Router + Recharts.

## Rutas

- `/` — Formulario de evaluación (escala 1-10 por pregunta).
- `/gracias` — Pantalla de agradecimiento tras enviar (sin resultados).
- `/admin` — Login del administrador.
- `/admin/dashboard` — Dashboard (métricas, gráficos, exportar CSV/Excel).

## Desarrollo

```bash
npm install
npm run dev
```

El servidor corre en `http://localhost:3000`. Las peticiones a `/api` se redirigen al backend Django (puerto 8000) mediante el proxy de Vite.

**Requisito:** Backend Django en marcha (`cd backend && python manage.py runserver`).

## Producción

```bash
npm run build
```

Salida en `dist/`. Servir con cualquier estático o configurar Django para servir el frontend.
