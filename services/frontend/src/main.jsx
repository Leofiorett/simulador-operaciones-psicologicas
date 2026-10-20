import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App'
import { Login, Dashboard, Cursos, CursoDetalle, Simulador, Ejercicios, EjercicioDetalle, Taxonomias } from './pages'
import './styles.css'

const router = createBrowserRouter(
  [
    {
      path: '/',
      element: <App />,
      children: [
        { index: true, element: <Dashboard /> },
        { path: 'login', element: <Login /> },
        { path: 'cursos', element: <Cursos /> },
        { path: 'cursos/:slug', element: <CursoDetalle /> },
        { path: 'simulador', element: <Simulador /> },
        { path: 'ejercicios', element: <Ejercicios /> },
        { path: 'ejercicios/:id', element: <EjercicioDetalle /> },
        { path: 'taxonomias', element: <Taxonomias /> },
      ],
    },
  ],
  { basename: import.meta.env.BASE_URL }
)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
