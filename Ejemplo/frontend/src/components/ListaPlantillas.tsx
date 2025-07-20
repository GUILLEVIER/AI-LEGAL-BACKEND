import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPlantillas, crearPlantilla, duplicarPlantilla, getPlantilla, generarDocumento, getDocumentosGenerados, getDocumentoGenerado, getCamposDisponibles, crearCampoDisponible, eliminarPlantilla, getPlantillasCompartidasConmigo, agregarFavorito, quitarFavorito } from '../services/api';
import { PlantillaDocumento, PlantillaCompartida } from '../types';
import ModalCompartirPlantilla from './ModalCompartirPlantilla';

const ListaPlantillas: React.FC = () => {
  const [plantillas, setPlantillas] = useState<PlantillaDocumento[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalEliminar, setModalEliminar] = useState<{ mostrar: boolean; plantilla: PlantillaDocumento | null }>({ mostrar: false, plantilla: null });
  const [modalVistaPrevia, setModalVistaPrevia] = useState<{ mostrar: boolean; plantilla: PlantillaDocumento | null }>({ mostrar: false, plantilla: null });
  const [favoritosCargando, setFavoritosCargando] = useState<Set<number>>(new Set());
  const [duplicandoPlantillas, setDuplicandoPlantillas] = useState<Set<number>>(new Set());
  const [datosPreview, setDatosPreview] = useState<Record<string, string>>({});
  const [modalCompartir, setModalCompartir] = useState<{ mostrar: boolean; plantilla: PlantillaDocumento | null }>({ mostrar: false, plantilla: null });
  const [compartidas, setCompartidas] = useState<PlantillaCompartida[]>([]);
  const navigate = useNavigate();

  const cargarPlantillas = async () => {
    setCargando(true);
    try {
      const data = await getPlantillas();
      setPlantillas(data);
    } catch (e) {
      setError('Error al cargar plantillas');
    } finally {
      setCargando(false);
    }
  };

  // Cargar compartidas para una plantilla específica
  const cargarCompartidas = async (plantillaId: number) => {
    // Filtrar solo las compartidas de esta plantilla
    const todas = await getPlantillasCompartidasConmigo();
    setCompartidas(todas.filter(c => c.plantilla === plantillaId));
  };

  useEffect(() => {
    cargarPlantillas();
  }, []);

  const handleUsar = (id: number) => {
    navigate(`/generar?plantilla=${id}`);
  };

  const handleEditar = (id: number) => {
    navigate(`/plantillas/${id}/editar`);
  };

  const handleVistaPrevia = (plantilla: PlantillaDocumento) => {
    setModalVistaPrevia({ mostrar: true, plantilla });
    // Limpiar datos de preview anteriores
    setDatosPreview({});
  };

  const getPreviewHtml = (html: string, campos: any[], datos: Record<string, string>) => {
    let preview = html;
    campos.forEach(campo => {
      const valor = datos[campo.nombre_variable]?.trim() || campo.nombre_variable.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
      preview = preview.replaceAll(`{{${campo.nombre_variable}}}`, valor);
    });
    return preview;
  };

  const handleEliminar = (plantilla: PlantillaDocumento) => {
    setModalEliminar({ mostrar: true, plantilla });
  };

  // Reemplazar fetchApi para eliminar plantilla
  const confirmarEliminar = async () => {
    if (!modalEliminar.plantilla) return;
    setCargando(true);
    try {
      await eliminarPlantilla(modalEliminar.plantilla.id);
      await cargarPlantillas();
      setModalEliminar({ mostrar: false, plantilla: null });
    } catch (e) {
      setError('Error al eliminar la plantilla');
    } finally {
      setCargando(false);
    }
  };

  const handleDuplicar = async (plantilla: PlantillaDocumento) => {
    // Evitar múltiples clicks
    if (duplicandoPlantillas.has(plantilla.id)) return;
    
    setDuplicandoPlantillas(prev => new Set(prev).add(plantilla.id));
    setError(null); // Limpiar errores anteriores
    
    try {
      console.log('Plantilla a duplicar:', plantilla); // Debug
      console.log('campos_asociados:', plantilla.campos_asociados); // Debug
      console.log('Tipo de plantilla:', plantilla.tipo); // Debug
      console.log('Tipo info de plantilla:', plantilla.tipo_info); // Debug
      
      // Crear una nueva plantilla con los datos de la original
      const plantillaDuplicada = {
        nombre: `${plantilla.nombre} (Copia)`,
        descripcion: plantilla.descripcion || '',
        html_con_campos: plantilla.html_con_campos || '',
        tipo_id: plantilla.tipo?.id || plantilla.tipo_info?.id || undefined,
        campos: plantilla.campos_asociados && Array.isArray(plantilla.campos_asociados) 
          ? plantilla.campos_asociados.map(campo => ({
              campo_id: campo.campo,
              nombre_variable: campo.nombre_variable
            }))
          : []
      };
      
      console.log('Plantilla duplicada a enviar:', plantillaDuplicada); // Debug
      console.log('Tipo ID a enviar:', plantillaDuplicada.tipo_id); // Debug
      console.log('JSON a enviar:', JSON.stringify(plantillaDuplicada, null, 2)); // Debug
      
      console.log('Duplicando plantilla:', plantillaDuplicada); // Debug
      await duplicarPlantilla(plantillaDuplicada);
      await cargarPlantillas();
    } catch (e) {
      console.error('Error al duplicar:', e); // Debug
      setError('Error al duplicar la plantilla');
    } finally {
      setDuplicandoPlantillas(prev => {
        const newSet = new Set(prev);
        newSet.delete(plantilla.id);
        return newSet;
      });
    }
  };

  const handleFavorito = async (plantilla: PlantillaDocumento) => {
    if (favoritosCargando.has(plantilla.id)) return;
    setFavoritosCargando(prev => new Set(prev).add(plantilla.id));
    try {
      // Optimistic update
      setPlantillas(prevPlantillas =>
        prevPlantillas.map(p =>
          p.id === plantilla.id
            ? { ...p, es_favorito: !p.es_favorito }
            : p
        )
      );

      // Llamar a la API real
      if (plantilla.es_favorito) {
        await quitarFavorito(plantilla.id);
      } else {
        await agregarFavorito(plantilla.id);
      }
      // Opcional: recargar la lista para asegurar sincronía
      // await cargarPlantillas();
    } catch (e) {
      // Si hay error, revertir el cambio
      setPlantillas(prevPlantillas =>
        prevPlantillas.map(p =>
          p.id === plantilla.id
            ? { ...p, es_favorito: plantilla.es_favorito }
            : p
        )
      );
      setError('Error al actualizar favoritos');
    } finally {
      setFavoritosCargando(prev => {
        const newSet = new Set(prev);
        newSet.delete(plantilla.id);
        return newSet;
      });
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Plantillas Guardadas</h2>
      {cargando && <p>Cargando...</p>}
      {error && <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded mb-4">{error}</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {plantillas.map((plantilla) => (
          <div key={plantilla.id} className="bg-white rounded-lg shadow p-4 flex flex-col relative">
            {/* Botón de compartir en la esquina superior derecha */}
            <button
              onClick={async () => {
                setModalCompartir({ mostrar: true, plantilla });
                await cargarCompartidas(plantilla.id);
              }}
              className="absolute top-2 right-2 text-2xl text-blue-600 hover:text-blue-800 bg-blue-50 rounded-full p-1 shadow"
              title="Compartir plantilla"
            >
              🤝
            </button>
            <h3 className="text-lg font-semibold mb-2">{plantilla.nombre}</h3>
            <p className="text-gray-600 mb-2">{plantilla.descripcion}</p>
            {plantilla.tipo && (
              <p className="text-xs text-blue-600 mb-1">
                📂 {plantilla.tipo.nombre}
              </p>
            )}
            <p className="text-xs text-gray-400 mb-2">Creada: {new Date(plantilla.fecha_creacion).toLocaleString()}</p>
            <div className="flex-1" />
            <div className="flex gap-2 mt-4">
              <button 
                onClick={() => handleFavorito(plantilla)} 
                disabled={favoritosCargando.has(plantilla.id)}
                className={`px-3 py-1 rounded text-lg transition-colors ${
                  favoritosCargando.has(plantilla.id)
                    ? 'text-gray-300 cursor-not-allowed'
                    : plantilla.es_favorito 
                      ? 'text-yellow-500 hover:text-yellow-600' 
                      : 'text-gray-400 hover:text-yellow-500'
                }`}
                title={plantilla.es_favorito ? 'Quitar de favoritos' : 'Agregar a favoritos'}
              >
                {favoritosCargando.has(plantilla.id) ? '⏳' : '★'}
              </button>
              <button 
                onClick={() => handleVistaPrevia(plantilla)} 
                className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 text-lg"
                title="Vista previa"
              >
                👁️
              </button>
              <button 
                onClick={() => handleUsar(plantilla.id)} 
                className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                title="Usar plantilla"
              >
                ▶️
              </button>
              <button 
                onClick={() => handleEditar(plantilla.id)} 
                className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600 text-lg"
                title="Editar plantilla"
              >
                ✏️
              </button>
              <button 
                onClick={() => handleDuplicar(plantilla)} 
                disabled={duplicandoPlantillas.has(plantilla.id)}
                className={`px-3 py-1 rounded text-lg ${
                  duplicandoPlantillas.has(plantilla.id)
                    ? 'bg-purple-400 text-white cursor-not-allowed'
                    : 'bg-purple-600 text-white hover:bg-purple-700'
                }`}
                title="Duplicar plantilla"
              >
                {duplicandoPlantillas.has(plantilla.id) ? '⏳' : '📋'}
              </button>
              <button 
                onClick={() => handleEliminar(plantilla)} 
                className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 text-lg"
                title="Eliminar plantilla"
              >
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>
      {plantillas.length === 0 && !cargando && (
        <div className="text-center text-gray-500 py-12">No hay plantillas guardadas.</div>
      )}
      
      {/* Modal de confirmación para eliminar */}
      {modalEliminar.mostrar && modalEliminar.plantilla && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full">
            <h3 className="text-lg font-semibold mb-4">Confirmar eliminación</h3>
            <p className="text-gray-600 mb-6">
              ¿Seguro que deseas eliminar la plantilla <strong>"{modalEliminar.plantilla.nombre}"</strong>?
            </p>
            <p className="text-sm text-red-600 mb-6">
              Esta acción no se puede deshacer.
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
                onClick={confirmarEliminar} 
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                disabled={cargando}
              >
                {cargando ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de vista previa */}
      {modalVistaPrevia.mostrar && modalVistaPrevia.plantilla && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Vista Previa: {modalVistaPrevia.plantilla.nombre}</h3>
              <button 
                onClick={() => setModalVistaPrevia({ mostrar: false, plantilla: null })} 
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                ✕
              </button>
            </div>
            
            {/* Campos de datos de ejemplo */}
            {modalVistaPrevia.plantilla.campos_asociados && modalVistaPrevia.plantilla.campos_asociados.length > 0 && (
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Datos de ejemplo:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {modalVistaPrevia.plantilla.campos_asociados.map((campo) => (
                    <div key={campo.nombre_variable}>
                      <label className="text-xs text-gray-600">{campo.nombre_variable}</label>
                      <input
                        type="text"
                        className="w-full p-1 border border-gray-300 rounded text-xs"
                        value={datosPreview[campo.nombre_variable] || ''}
                        onChange={e => setDatosPreview(prev => ({ ...prev, [campo.nombre_variable]: e.target.value }))}
                        placeholder={`Ejemplo: ${campo.nombre_variable.replace(/_/g, ' ')}`}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Vista previa del documento */}
            <div className="border border-gray-300 rounded-lg p-4 bg-white">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Vista previa del documento:</h4>
              <div 
                className="prose max-w-none min-h-[200px] p-4 border border-dashed border-gray-300 rounded bg-gray-50"
                dangerouslySetInnerHTML={{ 
                  __html: getPreviewHtml(
                    modalVistaPrevia.plantilla.html_con_campos, 
                    modalVistaPrevia.plantilla.campos_asociados, 
                    datosPreview
                  ).replace(/\n/g, '<br>') 
                }} 
              />
            </div>

            <div className="flex justify-end mt-4">
              <button 
                onClick={() => setModalVistaPrevia({ mostrar: false, plantilla: null })} 
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Modal de Compartir */}
      {modalCompartir.mostrar && modalCompartir.plantilla && (
        <ModalCompartirPlantilla
          open={modalCompartir.mostrar}
          onClose={() => setModalCompartir({ mostrar: false, plantilla: null })}
          plantilla={modalCompartir.plantilla}
          onCompartido={async () => {
            // Si necesitas refrescar algo en el padre, hazlo aquí
          }}
        />
      )}
    </div>
  );
};

export default ListaPlantillas; 