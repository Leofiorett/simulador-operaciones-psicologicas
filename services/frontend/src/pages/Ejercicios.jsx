import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'

export function Ejercicios() {
  const [ejercicios, setEjercicios] = useState([])
  const [tipos] = useState(['doctrina', 'planificacion', 'simulacion', 'defensa'])
  const [escenarios, setEscenarios] = useState([])
  const [tipo, setTipo] = useState('simulacion')
  const [nombre, setNombre] = useState('')
  const [escenario, setEscenario] = useState('crisis_humanitaria')
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [userRole, setUserRole] = useState(null)

  const cargar = () => {
    api('/api/exercises').then((d) => setEjercicios(d.ejercicios)).catch((e) => setError(e.message))
  }

  useEffect(() => {
    cargar()
    api('/api/simulation/scenarios').then((d) => setEscenarios(d.escenarios))
    api('/api/auth/me').then((u) => setUserRole(u.role)).catch(() => {})
  }, [])

  const crear = async () => {
    setError(''); setMensaje('')
    try {
      const meta = await api('/api/exercises', {
        method: 'POST',
        body: JSON.stringify({ type: tipo, name: nombre,
                               scenario_code: tipo === 'doctrina' ? null : escenario }),
      })
      setMensaje(`Creado ${meta.id}`)
      cargar()
    } catch (err) { setError(err.message) }
  }

  const iniciar = async (id) => {
    setError(''); setMensaje('')
    try {
      await api(`/api/exercises/${id}/start`, { method: 'POST', body: JSON.stringify({}) })
      setMensaje(`Ejercicio ${id} iniciado`)
      cargar()
    } catch (err) { setError(err.message) }
  }

  const detener = async (id) => {
    setError(''); setMensaje('')
    try {
      await api(`/api/exercises/${id}/stop`, { method: 'POST', body: JSON.stringify({}) })
      cargar()
    } catch (err) { setError(err.message) }
  }

  return (
    <>
      <h2>Ejercicios</h2>
      <div className="card">
        <h3>Nuevo ejercicio</h3>
        <div className="grid-2">
          <div>
            <label>Tipo</label>
            <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
              {tipos.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            <label>Nombre</label>
            <input value={nombre} placeholder="p. ej.: Ataque a Central Eléctrica — fase informativa"
                   onChange={(e) => setNombre(e.target.value)} />
          </div>
          <div>
            <label>Escenario sintético (no aplica a doctrina)</label>
            <select value={escenario} disabled={tipo === 'doctrina'}
                    onChange={(e) => setEscenario(e.target.value)}>
              {escenarios.map((s) => <option key={s.code} value={s.code}>{s.nombre}</option>)}
            </select>
            <button onClick={crear} disabled={!nombre}>Crear ejercicio</button>
          </div>
        </div>
        <p className="muted">
          Para iniciar un ejercicio se requiere autorización de instructor
          (el campo authorized_by lo completa el rol instructor al presionar Iniciar).
        </p>
        {error && <p className="error-text">{error}</p>}
        {mensaje && <p className="ok-text">{mensaje}</p>}
      </div>

      <div className="card">
        <table>
          <thead>
            <tr><th>ID</th><th>Estado</th><th>Tipo</th><th>Nombre</th><th>Autorizó</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {ejercicios.map((e) => (
              <tr key={e.id}>
                <td><Link to={`/ejercicios/${e.id}`}>{e.id}</Link></td>
                <td><span className={`badge ${e.status === 'completed' ? 'ok' : e.status === 'running' ? 'info' : e.status === 'timeout' ? 'bad' : 'warn'}`}>{e.status}</span></td>
                <td>{e.type}</td>
                <td>{e.name}</td>
                <td>{e.authorized_by || '—'}</td>
                <td>
                  {e.status === 'created' && userRole === 'instructor' && (
                    <button style={{ padding: '4px 10px', fontSize: 12 }}
                            onClick={() => iniciar(e.id)}>Iniciar</button>
                  )}
                  {e.status === 'running' && (
                    <button className="danger" style={{ padding: '4px 10px', fontSize: 12 }}
                            onClick={() => detener(e.id)}>Detener</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {ejercicios.length === 0 && <p className="muted">Sin ejercicios registrados.</p>}
      </div>
    </>
  )
}

export function EjercicioDetalle() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [reporte, setReporte] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    api(`/api/exercises/${id}`).then(setData).catch((e) => setError(e.message))
  }, [id])

  const generarReporte = async () => {
    try {
      const r = await api(`/api/exercises/${id}/report`, { method: 'POST', body: JSON.stringify({}) })
      setReporte(r.reporte)
    } catch (err) { setError(err.message) }
  }

  if (error) return <p className="error-text">{error}</p>
  if (!data) return <p className="muted">Cargando…</p>

  const m = data.metadata
  return (
    <>
      <h2>{m.name}</h2>
      <p><Link to="/ejercicios">← volver a ejercicios</Link></p>
      <div className="card">
        <table>
          <tbody>
            <tr><td>ID</td><td>{m.id}</td></tr>
            <tr><td>Estado</td><td><span className={`badge ${m.status === 'completed' ? 'ok' : m.status === 'running' ? 'info' : 'warn'}`}>{m.status}</span></td></tr>
            <tr><td>Tipo</td><td>{m.type}</td></tr>
            <tr><td>Autorizado por</td><td>{m.authorized_by || 'NO AUTORIZADO'}</td></tr>
            <tr><td>Escenario</td><td>{m.scenario_code || '—'}</td></tr>
            <tr><td>Iniciado</td><td>{m.started_at || '—'}</td></tr>
            <tr><td>Finalizado</td><td>{m.ended_at || '—'}</td></tr>
          </tbody>
        </table>
        <button onClick={generarReporte}>Generar reporte</button>
        <p className="muted">Evidencias registradas: {(data.evidencias || []).join(', ') || 'ninguna'}</p>
      </div>

      {reporte && (
        <div className="card markdown">
          <pre style={{ whiteSpace: 'pre-wrap' }}>{reporte}</pre>
        </div>
      )}

      <div className="card">
        <h3>Bitácora de eventos</h3>
        <table>
          <thead><tr><th>Momento</th><th>Evento</th><th>Detalle</th></tr></thead>
          <tbody>
            {data.eventos.map((ev, i) => (
              <tr key={i}>
                <td>{(ev.ts || '').replace('T', ' ').slice(0, 19)}</td>
                <td>{ev.event}</td>
                <td className="muted">{JSON.stringify(ev.payload).slice(0, 120)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {(!data.eventos || data.eventos.length === 0) && <p className="muted">Sin eventos.</p>}
      </div>
    </>
  )
}
