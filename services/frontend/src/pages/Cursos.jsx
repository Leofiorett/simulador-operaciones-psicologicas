import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { marked } from 'marked'
import { api } from '../api'

export function Cursos() {
  const [modulos, setModulos] = useState([])
  const [progress, setProgress] = useState(null)

  useEffect(() => {
    api('/api/courses').then((d) => setModulos(d.modulos))
    api('/api/courses/progress/mine').then(setProgress).catch(() => {})
  }, [])

  const estado = (slug) => {
    if (!progress) return null
    const p = progress.progreso.find((x) => x.module_slug === slug)
    if (!p) return <span className="badge warn">pendiente</span>
    return p.completed
      ? <span className="badge ok">aprobado</span>
      : <span className="badge bad">reprobado ({p.quiz_score}/{p.quiz_total})</span>
  }

  return (
    <>
      <h2>Cursos doctrinales</h2>
      <p className="muted">Marco doctrinal basado en el manual del Gral. H. K. Johnson (1974), reconstruido desde fuentes públicas equivalentes.</p>
      <div className="card">
        <table>
          <thead>
            <tr><th>Módulo</th><th>Título</th><th>Estado</th></tr>
          </thead>
          <tbody>
            {modulos.map((m) => (
              <tr key={m.slug}>
                <td>{String(m.numero).padStart(2, '0')}</td>
                <td><Link to={`/cursos/${m.slug}`}>{m.titulo}</Link></td>
                <td>{estado(m.slug)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}

export function CursoDetalle() {
  const { slug } = useParams()
  const [modulo, setModulo] = useState(null)
  const [quiz, setQuiz] = useState(null)
  const [respuestas, setRespuestas] = useState([])
  const [resultado, setResultado] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    setResultado(null); setRespuestas([]); setQuiz(null); setError('')
    api(`/api/courses/${slug}`).then(setModulo).catch((e) => setError(e.message))
    api(`/api/courses/${slug}/quiz`).then((q) => {
      setQuiz(q)
      setRespuestas(new Array(q.preguntas.length).fill(-1))
    }).catch(() => {})
  }, [slug])

  const rendir = async () => {
    setError('')
    try {
      const r = await api(`/api/courses/${slug}/quiz`, {
        method: 'POST',
        body: JSON.stringify({ respuestas }),
      })
      setResultado(r)
    } catch (err) { setError(err.message) }
  }

  if (!modulo) return <p className="muted">Cargando…</p>

  return (
    <>
      <div className="card markdown" dangerouslySetInnerHTML={{ __html: marked(modulo.contenido) }} />
      {quiz && (
        <div className="card">
          <h3>Cuestionario de comprensión (aprobado ≥ 70%)</h3>
          {resultado && (
            <p className={resultado.aprobado ? 'ok-text' : 'error-text'}>
              Resultado: {resultado.score}/{resultado.total} — {resultado.aprobado ? 'APROBADO' : 'REPROBADO (se puede volver a rendir)'}
            </p>
          )}
          {!resultado && quiz.preguntas.map((p, i) => (
            <div key={i} style={{ marginBottom: 16 }}>
              <label><strong>{i + 1}. {p.pregunta}</strong></label>
              {p.opciones.map((op, j) => (
                <div key={j}>
                  <label style={{ color: 'var(--text)', marginBottom: 2 }}>
                    <input
                      type="radio"
                      name={`q${i}`}
                      checked={respuestas[i] === j}
                      onChange={() => {
                        const next = [...respuestas]
                        next[i] = j
                        setRespuestas(next)
                      }}
                      style={{ width: 'auto', marginRight: 8 }}
                    />
                    {op}
                  </label>
                </div>
              ))}
            </div>
          ))}
          {!resultado && (
            <button onClick={rendir} disabled={respuestas.some((r) => r === -1)}>
              Enviar respuestas
            </button>
          )}
          {resultado && (
            <div>
              {resultado.detalle.map((d) => (
                <p key={d.indice} className={d.correcta === d.elegida ? 'ok-text' : 'error-text'}>
                  {d.indice + 1}. {d.correcta === d.elegida ? '✔' : `✘ (correcta: opción ${d.correcta + 1})`} — {d.explicacion}
                </p>
              ))}
              <button className="secondary" onClick={() => { setResultado(null); setRespuestas(new Array(quiz.preguntas.length).fill(-1)) }}>
                Volver a rendir
              </button>
            </div>
          )}
          {error && <p className="error-text">{error}</p>}
        </div>
      )}
    </>
  )
}
