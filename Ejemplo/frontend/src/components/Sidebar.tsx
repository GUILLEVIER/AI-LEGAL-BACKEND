import React from 'react';
import { NavLink } from 'react-router-dom';
import { logout } from '../services/auth';

const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Subir Documento' },
    { to: '/plantillas', label: 'Plantillas' },
    { to: '/favoritos', label: '⭐ Favoritos' },
    { to: '/tipos-plantilla', label: '📂 Tipos de Plantilla' },
    { to: '/compartidas', label: '📤 Plantillas compartidas conmigo' },
    { to: '/generar', label: 'Generar Documento' },
    { to: '/documentos-generados', label: 'Documentos Generados' },
  ];

  return (
    <aside className="bg-blue-50 min-h-screen w-64 flex flex-col">
      <div className="p-6 font-bold text-2xl text-blue-700">Generador</div>
      <nav className="flex-1">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `block px-4 py-2 rounded transition-colors ${isActive ? 'bg-blue-200 text-blue-900 font-semibold' : 'text-blue-700 hover:bg-blue-100'}`
                }
              >
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <div className="p-4 mt-auto">
        <button
          onClick={logout}
          className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-100 rounded"
        >
          🚪 Cerrar sesión
        </button>
      </div>
    </aside>
  );
};

export default Sidebar; 