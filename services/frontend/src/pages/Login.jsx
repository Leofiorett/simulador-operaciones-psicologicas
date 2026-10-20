import { useOutletContext, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { api, setToken } from '../api'

export function Login() {
  const { setUser } = useOutletContext()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const data = await api('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      })
      setToken(data.token)
      setUser(data)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="login-wrap">
      <div className="aviso-clasificacion">
        PLATAFORMA DE INSTRUCCIÓN INSTITUCIONAL · Audiencias 100% sintéticas en
        entorno aislado · Uso reservado a personal autorizado
      </div>
      <div className="card">
        <h1>◉ SOP — Simulador de Operaciones Psicológicas</h1>
        <form onSubmit={submit}>
          <label>Usuario</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />
          <label>Contraseña</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          {error && <p className="error-text">{error}</p>}
          <button type="submit" style={{ width: '100%' }}>Ingresar</button>
        </form>
      </div>
    </div>
  )
}
