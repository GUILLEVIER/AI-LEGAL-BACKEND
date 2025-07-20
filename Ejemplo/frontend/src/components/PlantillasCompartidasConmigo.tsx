import React, { useEffect, useState } from 'react';
import { getPlantillasCompartidasConmigo } from '../services/api';
import { PlantillaCompartida } from '../types';
import { useNavigate } from 'react-router-dom';

const PlantillasCompartidasConmigo: React.FC = () => {
  const [compartidas, setCompartidas] = useState<PlantillaCompartida[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      try {
        const data = await getPlantillasCompartidasConmigo();
        setCompartidas(data);
      } catch (e: any) {
        if (e.response && e.response.status === 401) {
          setError('Debes iniciar sesión para ver las plantillas compartidas.');
        } else {
          setError('No se pudieron cargar las plantillas compartidas.');
        }
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, []);

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Plantillas compartidas conmigo</h2>
      {cargando && <p>Cargando...</p>}
      {error && <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded mb-4">{error}</div>}
      {compartidas.length === 0 && !cargando && !error && (
        <div className="text-center text-gray-500 py-12">No tienes plantillas compartidas.</div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {compartidas.map((c) => (
          <div key={c.id} className="bg-white rounded-lg shadow p-4 flex flex-col">
            <h3 className="text-lg font-semibold mb-2 cursor-pointer hover:underline" onClick={() => navigate(`/plantillas/${c.plantilla}/editar`)}>{c.plantilla_nombre}</h3>
            <p className="text-gray-600 mb-1">Compartida por: <span className="font-semibold">{c.usuario_username}</span></p>
            <p className="text-xs text-gray-500 mb-1">Permisos: {c.permisos === 'edicion' ? 'Lectura y edición' : 'Solo lectura'}</p>
            <p className="text-xs text-gray-400 mb-2">Fecha: {new Date(c.fecha_compartida).toLocaleString()}</p>
            <button
              onClick={() => navigate(`/plantillas/${c.plantilla}/editar`)}
              className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 mt-auto"
            >
              Abrir
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlantillasCompartidasConmigo; 