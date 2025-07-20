import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMisFavoritos, quitarFavorito } from '../services/api';
import { PlantillaDocumento } from '../types';

const ListaFavoritos: React.FC = () => {
  const [favoritos, setFavoritos] = useState<PlantillaDocumento[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalEliminar, setModalEliminar] = useState<{ mostrar: boolean; plantilla: PlantillaDocumento | null }>({ mostrar: false, plantilla: null });
  const navigate = useNavigate();

  const cargarFavoritos = async () => {
    setCargando(true);
    try {
      const data = await getMisFavoritos();
      setFavoritos(data);
    } catch (e) {
      setError('Error al cargar favoritos');
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarFavoritos();
  }, []);

  const handleUsar = (id: number) => {
    navigate(`/generar?plantilla=${id}`);
  };

  const handleEditar = (id: number) => {
    navigate(`/plantillas/${id}/editar`);
  };

  const handleQuitarFavorito = async (plantilla: PlantillaDocumento) => {
    setModalEliminar({ mostrar: true, plantilla });
  };

  const confirmarQuitarFavorito = async () => {
    if (!modalEliminar.plantilla) return;
    
    setCargando(true);
    try {
      await quitarFavorito(modalEliminar.plantilla.id);
      await cargarFavoritos();
      setModalEliminar({ mostrar: false, plantilla: null });
    } catch (e) {
      setError('Error al quitar de favoritos');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">⭐ Mis Plantillas Favoritas</h2>
      {cargando && <p>Cargando...</p>}
      {error && <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded mb-4">{error}</div>}
      
      {favoritos.length === 0 && !cargando && (
        <div className="text-center text-gray-500 py-12">
          <div className="text-6xl mb-4">⭐</div>
          <p className="text-xl mb-2">No tienes plantillas favoritas</p>
          <p className="text-gray-400">Ve a la sección de Plantillas y marca algunas como favoritas</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {favoritos.map((plantilla) => (
          <div key={plantilla.id} className="bg-white rounded-lg shadow p-4 flex flex-col border-2 border-yellow-200">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold">{plantilla.nombre}</h3>
              <span className="text-yellow-500 text-xl">⭐</span>
            </div>
            <p className="text-gray-600 mb-2">{plantilla.descripcion}</p>
            <p className="text-xs text-gray-400 mb-2">Creada: {new Date(plantilla.fecha_creacion).toLocaleString()}</p>
            {plantilla.fecha_agregado_favorito && (
              <p className="text-xs text-yellow-600 mb-2">
                Agregada a favoritos: {new Date(plantilla.fecha_agregado_favorito).toLocaleString()}
              </p>
            )}
            <div className="flex-1" />
            <div className="flex gap-2 mt-4">
              <button onClick={() => handleUsar(plantilla.id)} className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">Usar</button>
              <button onClick={() => handleEditar(plantilla.id)} className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600">Editar</button>
              <button 
                onClick={() => handleQuitarFavorito(plantilla)} 
                className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
                title="Quitar de favoritos"
              >
                ❌ Quitar
              </button>
            </div>
          </div>
        ))}
      </div>
      
      {/* Modal de confirmación para quitar de favoritos */}
      {modalEliminar.mostrar && modalEliminar.plantilla && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full">
            <h3 className="text-lg font-semibold mb-4">Confirmar acción</h3>
            <p className="text-gray-600 mb-6">
              ¿Seguro que deseas quitar <strong>"{modalEliminar.plantilla.nombre}"</strong> de tus favoritos?
            </p>
            <div className="flex gap-2 justify-end">
              <button 
                onClick={() => setModalEliminar({ mostrar: false, plantilla: null })} 
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                disabled={cargando}
              >
                Cancelar
              </button>
              <button 
                onClick={confirmarQuitarFavorito} 
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                disabled={cargando}
              >
                {cargando ? 'Quitando...' : 'Quitar de favoritos'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ListaFavoritos; 