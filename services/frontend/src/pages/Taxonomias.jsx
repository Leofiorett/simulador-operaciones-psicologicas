import { useEffect, useState } from 'react'
import { api } from '../api'

function Tabla({ filas, columnas, filtro }) {
  const q = filtro.toLowerCase()
  const visibles = filas.filter((f) =>
    JSON.stringify(f).toLowerCase().includes(q))
  return (
    <table>
      <thead>
        <tr>{columnas.map(([k, t]) => <th key={k}>{t}</th>)}</tr>
      </thead>
      <tbody>
        {visibles.map((f) => (
          <tr key={f.id}>
            {columnas.map(([k]) => (
              <td key={k} className="muted">{String(f[k] ?? '—').slice(0, 160)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export function Taxonomias() {
  const [tab, setTab] = useState('disarm')
  const [filtro, setFiltro] = useState('')
  const [disarm, setDisarm] = useState(null)
  const [cwm, setCwm] = useState(null)
  const [canales, setCanales] = useState([])
  const [sesgos, setSesgos] = useState([])

  useEffect(() => {
    api('/api/taxonomies/disarm-es').then(setDisarm)
    api('/api/taxonomies/cwm').then(setCwm)
    api('/api/taxonomies/canales').then(setCanales)
    api('/api/taxonomies/sesgos').then(setSesgos)
  }, [])

  const tabs = [
    ['disarm', `DISARM-ES (${disarm?.total_tecnicas ?? '…'})`],
    ['cwm', `CWM (${cwm ? cwm.total_tecnicas + cwm.conceptos.length : '…'})`],
    ['canales', `Canales doctrinales (${canales.length})`],
    ['sesgos', `Sesgos cognitivos (${sesgos.length})`],
  ]

  return (
    <>
      <h2>Taxonomías de referencia</h2>
      <p className="muted">
        Marcos públicos usados para clasificar conducta informativa adversaria
        (DISARM TTPs ES, CWM) y el repertorio doctrinal del manual (canales,
        ganchos). Solo para instrucción defensiva.
      </p>
      <div style={{ marginBottom: 14 }}>
        {tabs.map(([k, label]) => (
          <button key={k} className={tab === k ? '' : 'secondary'}
                  style={{ fontSize: 13 }}
                  onClick={() => setTab(k)}>
            {label}
          </button>
        ))}
      </div>
      <input placeholder="Buscar…" value={filtro}
             onChange={(e) => setFiltro(e.target.value)} />

      {tab === 'disarm' && disarm && (
        <div className="card">
          <Tabla
            filas={disarm.tecnicas.map((t) => ({ id: t.id, nombre: t.nombre,
              tactica: t.tactica, descripcion: t.descripcion }))}
            columnas={[['id', 'ID'], ['nombre', 'Técnica'],
                       ['tactica', 'Táctica'], ['descripcion', 'Descripción']]}
            filtro={filtro}
          />
        </div>
      )}

      {tab === 'cwm' && cwm && (
        <>
          <div className="card">
            <h3>Matriz de weaponización cognitiva — técnicas</h3>
            <Tabla
              filas={cwm.tecnicas}
              columnas={[['id', 'ID'], ['nombre', 'Técnica'],
                         ['categoria', 'Categoría'], ['descripcion', 'Descripción']]}
              filtro={filtro}
            />
          </div>
          <div className="card">
            <h3>Conceptos</h3>
            <Tabla
              filas={cwm.conceptos}
              columnas={[['id', 'ID'], ['nombre', 'Concepto'],
                         ['descripcion', 'Descripción']]}
              filtro={filtro}
            />
          </div>
        </>
      )}

      {tab === 'canales' && (
        <div className="card">
          <Tabla
            filas={canales}
            columnas={[['code', 'Código'], ['nombre', 'Canal'],
                       ['alcance_base', 'Alcance base'], ['fatiga_por_turno', 'Fatiga'],
                       ['nota_doctrinal', 'Nota doctrinal']]}
            filtro={filtro}
          />
        </div>
      )}

      {tab === 'sesgos' && (
        <div className="card">
          <Tabla
            filas={sesgos}
            columnas={[['id', 'ID'], ['nombre', 'Sesgo / gancho'],
                       ['factor', 'Factor'], ['descripcion', 'Descripción']]}
            filtro={filtro}
          />
        </div>
      )}
    </>
  )
}
