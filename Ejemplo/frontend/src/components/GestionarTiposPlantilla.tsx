import React, { useEffect, useState } from 'react';
import { getTiposPlantilla, crearTipoPlantilla } from '../services/api';
import { TipoPlantillaDocumento } from '../types';

const GestionarTiposPlantilla: React.FC = () => {
  const [tipos, setTipos] = useState<TipoPlantillaDocumento[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nuevoTipo, setNuevoTipo] = useState('');
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  const cargarTipos = async () => {
    setCargando(true);
    try {
      const data = await getTiposPlantilla();
      setTipos(data);
    } catch (e) {
      setError('Error al cargar tipos de plantilla');
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarTipos();
  }, []);

  const handleCrearTipo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nuevoTipo.trim()) return;

    setCargando(true);
    try {
      await crearTipoPlantilla({ nombre: nuevoTipo.trim() });
      setNuevoTipo('');
      setMostrarFormulario(false);
      await cargarTipos();
    } catch (e) {
      setError('Error al crear tipo de plantilla');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Tipos de Plantilla</h2>
        <button
          onClick={() => setMostrarFormulario(!mostrarFormulario)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {mostrarFormulario ? 'Cancelar' : '+ Nuevo Tipo'}
        </button>
      </div>

      {error && <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded mb-4">{error}</div>}

      {/* Formulario para crear nuevo tipo */}
      {mostrarFormulario && (
        <form onSubmit={handleCrearTipo} className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex gap-4">
            <input
              type="text"
              value={nuevoTipo}
              onChange={(e) => setNuevoTipo(e.target.value)}
              placeholder="Nombre del tipo de plantilla"
              className="flex-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={cargando}
            />
            <button
              type="submit"
              disabled={cargando || !nuevoTipo.trim()}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
            >
              {cargando ? 'Creando...' : 'Crear'}
            </button>
          </div>
        </form>
      )}

      {/* Lista de tipos */}
      {cargando && <p className="text-center py-4">Cargando tipos...</p>}
      
      {!cargando && tipos.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          <p className="text-lg mb-2">No hay tipos de plantilla</p>
          <p>Crea el primer tipo para empezar a categorizar tus plantillas</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tipos.map((tipo) => (
          <div key={tipo.id} className="bg-gray-50 p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-800">{tipo.nombre}</h3>
              <span className="text-sm text-gray-500">ID: {tipo.id}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GestionarTiposPlantilla; 