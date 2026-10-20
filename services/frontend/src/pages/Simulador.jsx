import { useEffect, useState } from 'react'
import { api } from '../api'

function BarChart({ series, campo, titulo }) {
  if (!series || series.length === 0) return null
  const valores = series.map((s) => Math.abs(s[campo]))
  const max = Math.max(...valores, 0.0001)
  const paso = Math.max(1, Math.floor(series.length / 12))
  const puntos = series.filter((_, i) => i % paso === 0 || i === series.length - 1)
  return (
    <div>
      <h3 style={{ marginTop: 18 }}>{titulo}</h3>
      <div className="bar-chart">
        {puntos.map((s) => (
          <div className="bar-row" key={s.turno}>
            <div className="bar-label">turno {s.turno}</div>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{ width: `${(Math.abs(s[campo]) / max) * 100}%` }}
              />
            </div>
            <div className="bar-value">{s[campo]}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function Simulador() {
  const [escenarios, setEscenarios] = useState([])
  const [canales, setCanales] = useState([])
  const [sesgos, setSesgos] = useState([])
  const [ejercicios, setEjercicios] = useState([])
  const [codigo, setCodigo] = useState('crisis_humanitaria')
  const [modoDefensa, setModoDefensa] = useState(false)
  const [mensajes, setMensajes] = useState([nuevoMensaje()])
  const [semilla, setSemilla] = useState(42)
  const [ejercicioId, setEjercicioId] = useState('')
  const [resultado, setResultado] = useState(null)
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  useEffect(() => {
    api('/api/simulation/scenarios').then((d) => setEscenarios(d.escenarios))
    api('/api/taxonomies/canales').then(setCanales)
    api('/api/taxonomies/sesgos').then(setSesgos)
    api('/api/exercises').then((d) => setEjercicios(
      d.ejercicios.filter((e) => e.status === 'running')))
  }, [])

  useEffect(() => {
    const sc = escenarios.find((e) => e.code === codigo)
    if (sc) {
      setModoDefensa(!!sc.tiene_operacion_adversaria)
    }
  }, [codigo, escenarios])

  function nuevoMensaje() {
    return { segmento: 'all', canal: 'radio', valencia: 0.8, fuerza: 0.7,
             credibilidad: 0.8, frecuencia: 2, ganchos: ['autoridad'],
             turno_inicio: 0, turno_fin: 11 }
  }

  const escenarioSel = escenarios.find((e) => e.code === codigo)

  const actualizar = (i, campo, valor) => {
    const next = [...mensajes]
    if (['valencia', 'fuerza', 'credibilidad'].includes(campo)) {
      next[i][campo] = parseFloat(valor)
    } else if (['frecuencia', 'turno_inicio', 'turno_fin'].includes(campo)) {
      next[i][campo] = parseInt(valor)
    } else {
      next[i][campo] = valor
    }
    setMensajes(next)
  }

  const toggleGancho = (i, gancho) => {
    const next = [...mensajes]
    const lista = new Set(next[i].ganchos)
    if (lista.has(gancho)) lista.delete(gancho)
    else lista.add(gancho)
    next[i].ganchos = [...lista]
    setMensajes(next)
  }

  const ejecutar = async () => {
    setError(''); setCargando(true); setResultado(null)
    try {
      if (modoDefensa) {
        const r = await api('/api/simulation/defensa', {
          method: 'POST',
          body: JSON.stringify({
            escenario: codigo,
            campana_defensiva: { mensajes },
            semilla: semilla,
            ejercicio_id: ejercicioId || null,
          }),
        })
        setResultado({ tipo: 'defensa', ...r })
      } else {
        const r = await api('/api/simulation/run', {
          method: 'POST',
          body: JSON.stringify({
            escenario: codigo,
            campana: { mensajes },
            semilla: semilla,
            ejercicio_id: ejercicioId || null,
          }),
        })
        setResultado({ tipo: 'simulacion', ...r })
      }
    } catch (err) { setError(err.message) }
    finally { setCargando(false) }
  }

  const metricaFila = (etiqueta, valor, invertir) => {
    const pct = Math.min(100, Math.abs(valor) * 100)
    const clase = invertir ? (pct > 50 ? 'bad' : '') : (valor >= 0 ? '' : 'bad')
    return (
      <div className="bar-row" key={etiqueta}>
        <div className="bar-label">{etiqueta}</div>
        <div className="bar-track"><div className={`bar-fill ${clase}`} style={{ width: `${pct}%` }} /></div>
        <div className="bar-value">{valor}</div>
      </div>
    )
  }

  return (
    <>
      <h2>Simulador de campañas</h2>
      <p className="muted">Audiencias sintéticas en entorno aislado. Los resultados son métricas de instrucción, no operaciones reales.</p>

      <div className="card">
        <div className="grid-2">
          <div>
            <label>Escenario</label>
            <select value={codigo} onChange={(e) => setCodigo(e.target.value)}>
              {escenarios.map((s) => (
                <option key={s.code} value={s.code}>{s.nombre}</option>
              ))}
            </select>
            {escenarioSel && <p className="muted">{escenarioSel.descripcion}</p>}
            {escenarioSel?.tiene_operacion_adversaria && (
              <p><span className="badge warn">operación adversaria inyectada — modo defensa activado</span></p>
            )}
          </div>
          <div>
            <label>Semilla (reproducibilidad)</label>
            <input type="number" value={semilla} onChange={(e) => setSemilla(parseInt(e.target.value))} />
            <label>Adjuntar a ejercicio (opcional)</label>
            <select value={ejercicioId} onChange={(e) => setEjercicioId(e.target.value)}>
              <option value="">— sin ejercicio —</option>
              {ejercicios.map((e) => (
                <option key={e.id} value={e.id}>{e.id} · {e.type} · {e.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Mensajes de la campaña</h3>
        {mensajes.map((m, i) => (
          <div key={i} style={{ borderBottom: '1px solid var(--border)', paddingBottom: 14, marginBottom: 14 }}>
            <div className="grid-2">
              <div>
                <label>Segmento objetivo</label>
                <select value={m.segmento} onChange={(e) => actualizar(i, 'segmento', e.target.value)}>
                  <option value="all">Toda la población</option>
                  {escenarioSel?.segmentos.map((s) => (
                    <option key={s.nombre} value={s.nombre}>{s.nombre}</option>
                  ))}
                </select>
                <label>Canal</label>
                <select value={m.canal} onChange={(e) => actualizar(i, 'canal', e.target.value)}>
                  {canales.map((c) => <option key={c.code} value={c.code}>{c.nombre}</option>)}
                </select>
                <label>Idea-fuerza / nota del mensaje</label>
                <input value={m.idea_fuerza || ''} placeholder="frase central del mensaje"
                       onChange={(e) => actualizar(i, 'idea_fuerza', e.target.value)} />
              </div>
              <div>
                <div className="grid-2">
                  <div>
                    <label>Valencia ({m.valencia})</label>
                    <input type="range" min="-1" max="1" step="0.05" value={m.valencia}
                           onChange={(e) => actualizar(i, 'valencia', e.target.value)} />
                    <label>Fuerza ({m.fuerza})</label>
                    <input type="range" min="0" max="1" step="0.05" value={m.fuerza}
                           onChange={(e) => actualizar(i, 'fuerza', e.target.value)} />
                  </div>
                  <div>
                    <label>Credibilidad ({m.credibilidad})</label>
                    <input type="range" min="0" max="1" step="0.05" value={m.credibilidad}
                           onChange={(e) => actualizar(i, 'credibilidad', e.target.value)} />
                    <label>Frecuencia por turno</label>
                    <input type="number" min="1" max="5" value={m.frecuencia}
                           onChange={(e) => actualizar(i, 'frecuencia', e.target.value)} />
                  </div>
                </div>
                <label>Ventana de turnos: inicio y fin</label>
                <div style={{ display: 'flex', gap: 10 }}>
                  <input type="number" min="0" value={m.turno_inicio}
                         onChange={(e) => actualizar(i, 'turno_inicio', e.target.value)} />
                  <input type="number" min="0" value={m.turno_fin}
                         onChange={(e) => actualizar(i, 'turno_fin', e.target.value)} />
                </div>
              </div>
            </div>
            <label>Ganchos cognitivos</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {sesgos.map((s) => (
                <button key={s.id}
                        className={m.ganchos.includes(s.id) ? '' : 'secondary'}
                        style={{ padding: '4px 10px', fontSize: 12 }}
                        onClick={() => toggleGancho(i, s.id)}>
                  {s.nombre}
                </button>
              ))}
            </div>
          </div>
        ))}
        <button className="secondary" onClick={() => setMensajes([...mensajes, nuevoMensaje()])}>
          + Agregar mensaje
        </button>
        {mensajes.length > 1 && (
          <button className="danger" onClick={() => setMensajes(mensajes.slice(0, -1))}>
            Quitar último
          </button>
        )}
        <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '16px 0' }} />
        <button onClick={ejecutar} disabled={cargando}>
          {cargando ? 'Simulando…' : modoDefensa ? 'Ejecutar defensa' : 'Ejecutar campaña'}
        </button>
        {error && <p className="error-text">{error}</p>}
      </div>

      {resultado && resultado.tipo === 'simulacion' && (
        <>
          <div className="card">
            <h3>Resultados finales</h3>
            <p>
              Evaluación automática:{' '}
              <span className={`badge ${resultado.evaluacion.aprobado ? 'ok' : 'bad'}`}>
                score {resultado.evaluacion.score} / 100 — {resultado.evaluacion.aprobado ? 'OBJETIVOS CUMPLIDOS' : 'OBJETIVOS NO CUMPLIDOS'}
              </span>
            </p>
            {metricaFila('actitud media global', resultado.simulacion.metricas_finales.actitud_media_global)}
            {metricaFila('polarización', resultado.simulacion.metricas_finales.polarizacion_global, true)}
            {metricaFila('alcance', resultado.simulacion.metricas_finales.alcance_global)}
            <BarChart series={resultado.simulacion.serie_temporal} campo="actitud_media" titulo="Evolución actitud media" />
            <BarChart series={resultado.simulacion.serie_temporal} campo="polarizacion" titulo="Evolución polarización" />
          </div>
          <div className="card">
            <h3>Efectos por segmento</h3>
            <table>
              <thead>
                <tr><th>Segmento</th><th>n</th><th>Base</th><th>Final</th><th>Δ</th><th>Polariz.</th><th>Alcance</th></tr>
              </thead>
              <tbody>
                {Object.entries(resultado.simulacion.metricas_finales.por_segmento).map(([seg, v]) => (
                  <tr key={seg}>
                    <td>{seg}</td><td>{v.n}</td><td>{v.actitud_base}</td>
                    <td>{v.actitud_final}</td>
                    <td className={v.desplazamiento >= 0 ? 'ok-text' : 'error-text'}>{v.desplazamiento > 0 ? '+' : ''}{v.desplazamiento}</td>
                    <td>{v.polarizacion}</td><td>{v.alcance}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {resultado && resultado.tipo === 'defensa' && (
        <>
          <div className="card">
            <h3>Resultado defensivo</h3>
            <p>
              <span className={`badge ${resultado.evaluacion.aprobado ? 'ok' : 'bad'}`}>
                score {resultado.evaluacion.score}/100 — {resultado.evaluacion.aprobado ? 'DEFENSA EFECTIVA' : 'DEFENSA INSUFICIENTE'}
              </span>
            </p>
            <table>
              <thead>
                <tr><th>Criterio</th><th>Estado</th></tr>
              </thead>
              <tbody>
                {Object.entries(resultado.evaluacion.criterios).map(([k, v]) => (
                  <tr key={k}><td>{k}</td><td>{v ? '✔ cumplido' : '✘ no cumplido'}</td></tr>
                ))}
              </tbody>
            </table>
            <p className="muted">
              Mejora de actitud vs. línea base adversaria: {resultado.evaluacion.mejora_actitud} ·
              mejora de polarización: {resultado.evaluacion.mejora_polarizacion}
            </p>
          </div>
          <div className="card">
            <h3>Línea base vs. defensa</h3>
            <table>
              <thead>
                <tr><th>Métrica</th><th>Solo adversaria</th><th>Con defensa</th></tr>
              </thead>
              <tbody>
                <tr><td>Actitud media</td><td>{resultado.linea_base.actitud_media_global}</td><td>{resultado.defensa.actitud_media_global}</td></tr>
                <tr><td>Polarización</td><td>{resultado.linea_base.polarizacion_global}</td><td>{resultado.defensa.polarizacion_global}</td></tr>
                <tr><td>Alcance adversario</td><td>{resultado.linea_base.alcance_global}</td><td>{resultado.defensa.alcance_global}</td></tr>
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  )
}
