import { useEffect, useState } from 'react'
import { NavLink, Navigate, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { api, clearToken, getToken } from './api'

export default function App() {
  const [user, setUser] = useState(null)
  const [checked, setChecked] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    if (!getToken()) {
      setChecked(true)
      return
    }
    api('/api/auth/me')
      .then((u) => { setUser(u); setChecked(true) })
      .catch(() => { clearToken(); setChecked(true) })
  }, [])

  useEffect(() => {
    if (checked && !user && location.pathname !== '/login') {
      navigate('/login', { replace: true })
    }
    if (checked && user && location.pathname === '/login') {
      navigate('/', { replace: true })
    }
  }, [checked, user, location.pathname])

  const logout = () => {
    clearToken()
    setUser(null)
    navigate('/login', { replace: true })
  }

  if (!user) {
    return checked ? (
      <main className="main" style={{ margin: '0 auto' }}>
        <Outlet context={{ user, setUser }} />
      </main>
    ) : null
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>◉ SOP — OPSIC</h1>
        <nav>
          <NavLink to="/" end>Panel</NavLink>
          <NavLink to="/cursos">Cursos doctrinales</NavLink>
          <NavLink to="/simulador">Simulador</NavLink>
          <NavLink to="/ejercicios">Ejercicios</NavLink>
          <NavLink to="/taxonomias">Taxonomías</NavLink>
        </nav>
        <div className="user">
          <div>{user.display_name || user.username}</div>
          <div>{user.role === 'instructor' ? '⬢ INSTRUCTOR' : '⬡ alumno'}</div>
          <button className="secondary" style={{ marginTop: 10 }} onClick={logout}>
            Salir
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet context={{ user, setUser }} />
      </main>
    </div>
  )
}
