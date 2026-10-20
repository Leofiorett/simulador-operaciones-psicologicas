import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export function Dashboard() {
  const [progress, setProgress] = useState(null)
  const [ejercicios, setEjercicios] = useState([])

  useEffect(() => {
    api('/api/courses/progress/mine').then(setProgress).catch(() => {})
    api('/api/exercises').then((d) => setEjercicios(d.ejercicios)).catch(() => {})
  }, [])

  const activos = ejercicios.filter((e) => e.status === 'running')

  return (
    <>
      <h2>Panel de instrucción</h2>
      <div className="kpi-row">
        <div className="kpi">
          <div className="valor">{progress ? `${progress.porcentaje_curso}%` : '—'}</div>
          <div className="etiqueta">Avance curricular</div>
        </div>
        <div className="kpi">
          <div className="valor">{progress ? `${progress.completados}/${progress.modulos_totales}` : '—'}</div>
          <div className="etiqueta">Módulos aprobados</div>
        </div>
        <div className="kpi">
          <div className="valor">{activos.length}</div>
          <div className="etiqueta">Ejercicios activos</div>
        </div>
      </div>

      <div className="card">
        <h3>Ejercicios recientes</h3>
        {ejercicios.length === 0 && (
          <p className="muted">Sin ejercicios. Crear uno en la sección Ejercicios.</p>
        )}
        <table>
          <tbody>
            {ejercicios.slice(0, 6).map((e) => (
              <tr key={e.id}>
                <td><Link to={`/ejercicios/${e.id}`}>{e.id}</Link></td>
                <td><span className={`badge ${e.status === 'completed' ? 'ok' : e.status === 'running' ? 'info' : 'warn'}`}>{e.status}</span></td>
                <td>{e.type}</td>
                <td>{e.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Progreso por módulo</h3>
        {!progress && <p className="muted">Cargando…</p>}
        {progress && progress.progreso.length === 0 && (
          <p className="muted">Aún sin evaluaciones rendidas. Comenzar por <Link to="/cursos">Cursos doctrinales</Link>.</p>
        )}
        {progress && progress.progreso.map((p) => (
          <div key={p.module_slug} style={{ marginBottom: 8 }}>
            <strong>{p.module_slug}</strong> — {p.completed ? 'aprobado' : `intento ${p.attempts}, score ${p.quiz_score}/${p.quiz_total}`}
          </div>
        ))}
      </div>
    </>
  )
}
