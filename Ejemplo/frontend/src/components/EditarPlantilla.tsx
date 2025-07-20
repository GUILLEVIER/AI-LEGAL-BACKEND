import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPlantilla, getCamposDisponibles, crearCampoDisponible, crearPlantilla, eliminarPlantilla, actualizarPlantilla, getTiposPlantilla } from '../services/api';
import { PlantillaDocumento, CampoPlantilla, CampoDisponible, TipoPlantillaDocumento } from '../types';
import ModalCrearCampo from './ModalCrearCampo';
import EditorDocumento from './EditorDocumento';
import html2pdf from 'html2pdf.js';

function getPreviewHtml(html: string, campos: CampoPlantilla[], datos: Record<string, string>) {
  let preview = html;
  campos.forEach(campo => {
    const valor = datos[campo.nombre_variable]?.trim() || campo.nombre_variable.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    preview = preview.replaceAll(`{{${campo.nombre_variable}}}`, valor);
  });
  return preview;
}

function descargarHtmlPreview(html: string) {
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'vista_previa.html';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function descargarPdfPreview(html: string) {
  const container = document.createElement('div');
  container.innerHTML = html;
  html2pdf().from(container).set({
    margin: 10,
    filename: 'vista_previa.pdf',
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  }).save();
}

const EditarPlantilla: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [plantilla, setPlantilla] = useState<PlantillaDocumento | null>(null);
  const [campos, setCampos] = useState<CampoDisponible[]>([]);
  const [nombre, setNombre] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState<string | null>(null);
  const [modalCampo, setModalCampo] = useState(false);
  const [modalAsociar, setModalAsociar] = useState(false);
  const [cargandoCampo, setCargandoCampo] = useState(false);
  const [nuevoAsociado, setNuevoAsociado] = useState<{ campo_id: number; nombre_variable: string }>({ campo_id: 0, nombre_variable: '' });
  const [htmlConCampos, setHtmlConCampos] = useState('');
  const [camposAsignados, setCamposAsignados] = useState<Array<{ campo_id: number; nombre_variable: string }>>([]);
  const [datosPreview, setDatosPreview] = useState<Record<string, string>>({});
  const [tiposPlantilla, setTiposPlantilla] = useState<TipoPlantillaDocumento[]>([]);
  const [tipoSeleccionado, setTipoSeleccionado] = useState<number | null>(null);

  useEffect(() => {
    if (id) {
      cargarPlantilla(Number(id));
      cargarCampos();
      cargarTiposPlantilla();
    }
    // eslint-disable-next-line
  }, [id]);

  const cargarPlantilla = async (plantillaId: number) => {
    setCargando(true);
    try {
      const data = await getPlantilla(plantillaId);
      console.log('Datos completos de la plantilla:', data); // Debug completo
      setPlantilla(data);
      setNombre(data.nombre);
      setDescripcion(data.descripcion);
      setHtmlConCampos(data.html_con_campos || '');
      // Intentar obtener el tipo de diferentes formas
      const tipoId = data.tipo?.id || data.tipo_info?.id || null;
      setTipoSeleccionado(tipoId);
      console.log('Tipo cargado:', data.tipo); // Debug
      console.log('Tipo info cargado:', data.tipo_info); // Debug
      console.log('Tipo seleccionado:', tipoId); // Debug
      // Inicializar camposAsignados con los campos existentes de la plantilla
      const camposIniciales = data.campos_asociados.map((campo: CampoPlantilla) => ({ 
        campo_id: campo.campo, 
        nombre_variable: campo.nombre_variable 
      }));
      setCamposAsignados(camposIniciales);
      console.log('Campos iniciales cargados:', camposIniciales); // Debug
    } catch (e) {
      setError('Error al cargar la plantilla');
    } finally {
      setCargando(false);
    }
  };

  const cargarCampos = async () => {
    try {
      const data = await getCamposDisponibles();
      setCampos(data);
    } catch (e) {
      setError('Error al cargar campos');
    }
  };

  const cargarTiposPlantilla = async () => {
    try {
      const data = await getTiposPlantilla();
      setTiposPlantilla(data);
    } catch (e) {
      setError('Error al cargar tipos de plantilla');
    }
  };

  // Reemplazar fetchApi para eliminar plantilla
  const handleEliminar = async () => {
    if (!plantilla) return;
    setCargando(true);
    setError(null);
    try {
      await eliminarPlantilla(plantilla.id);
      // Redirigir o actualizar la lista
      navigate('/plantillas');
    } catch (e) {
      setError('Error al eliminar la plantilla');
    } finally {
      setCargando(false);
    }
  };

  // Reemplazar fetchApi para actualizar plantilla
  const handleGuardar = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!plantilla) return;
    setCargando(true);
    setError(null);
    setExito(null);
    try {
      // Usar siempre camposAsignados si tiene contenido, sino usar los campos de la plantilla
      let camposPayload;
      if (camposAsignados.length > 0) {
        // Combinar campos existentes de la plantilla con nuevos campos asignados
        const camposExistentes = plantilla.campos_asociados.map((campo: CampoPlantilla) => ({
          campo_id: campo.campo,
          nombre_variable: campo.nombre_variable
        }));
        
        // Filtrar campos duplicados y agregar nuevos
        const camposUnicos = new Map();
        [...camposExistentes, ...camposAsignados].forEach(campo => {
          camposUnicos.set(campo.nombre_variable, campo);
        });
        
        camposPayload = Array.from(camposUnicos.values());
      } else {
        camposPayload = plantilla.campos_asociados.map((campo: CampoPlantilla) => ({
          campo_id: campo.campo,
          nombre_variable: campo.nombre_variable
        }));
      }
      
      console.log('Campos a enviar:', camposPayload); // Debug
      
      await actualizarPlantilla(plantilla.id, {
        nombre,
        descripcion,
        html_con_campos: htmlConCampos,
        tipo: tipoSeleccionado,
        campos: camposPayload
      });
      setExito('Plantilla actualizada correctamente');
      await cargarPlantilla(Number(id));
      setTimeout(() => navigate('/plantillas'), 1200);
    } catch (e) {
      setError('Error al guardar los cambios');
    } finally {
      setCargando(false);
    }
  };

  const handleCrearCampo = async (campo: { nombre: string; tipo_dato: 'texto' | 'fecha' | 'numero' }) => {
    setCargandoCampo(true);
    try {
      await crearCampoDisponible(campo);
      await cargarCampos();
      setModalCampo(false);
    } catch (error) {
      alert('Error al crear el campo');
    } finally {
      setCargandoCampo(false);
    }
  };

  // Asociar campo existente a la plantilla
  const handleAsociarCampo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nuevoAsociado.campo_id || !nuevoAsociado.nombre_variable.trim()) {
      alert('Debes seleccionar un campo y un nombre de variable');
      return;
    }
    setCargandoCampo(true);
    try {
      await actualizarPlantilla(Number(id), {
        agregar_campo: nuevoAsociado
      });
      await cargarPlantilla(Number(id)); // Recarga la plantilla para actualizar los campos asociados
      setModalAsociar(false);
    } catch (error) {
      alert('Error al asociar el campo');
    } finally {
      setCargandoCampo(false);
    }
  };

  // Quitar campo asociado de la plantilla
  const handleQuitarCampo = async (campoPlantillaId: number) => {
    if (!window.confirm('¿Seguro que deseas quitar este campo de la plantilla?')) return;
    setCargandoCampo(true);
    try {
      await actualizarPlantilla(Number(id), {
        quitar_campo_id: campoPlantillaId
      });
      await cargarPlantilla(Number(id));
    } catch (error) {
      alert('Error al quitar el campo');
    } finally {
      setCargandoCampo(false);
    }
  };

  // Duplicar plantilla
  const handleDuplicar = async () => {
    if (!plantilla) return;
    setCargando(true);
    try {
      // Usar camposAsignados si tiene contenido, sino usar los campos de la plantilla
      let camposParaDuplicar;
      if (camposAsignados.length > 0) {
        // Combinar campos existentes de la plantilla con nuevos campos asignados
        const camposExistentes = plantilla.campos_asociados.map((campo: CampoPlantilla) => ({
          campo_id: campo.campo,
          nombre_variable: campo.nombre_variable
        }));
        
        // Filtrar campos duplicados y agregar nuevos
        const camposUnicos = new Map();
        [...camposExistentes, ...camposAsignados].forEach(campo => {
          camposUnicos.set(campo.nombre_variable, campo);
        });
        
        camposParaDuplicar = Array.from(camposUnicos.values());
      } else {
        camposParaDuplicar = plantilla.campos_asociados.map((campo: CampoPlantilla) => ({
          campo_id: campo.campo,
          nombre_variable: campo.nombre_variable
        }));
      }
      
      console.log('Campos para duplicar:', camposParaDuplicar); // Debug
      
      // Crear una nueva plantilla con los datos actuales
      const plantillaDuplicada = {
        nombre: `${nombre} (Copia)`,
        //nombre: `${nombre}`,
        descripcion: descripcion,
        html_con_campos: htmlConCampos || plantilla.html_con_campos,
        campos: camposParaDuplicar
      };
      
      const nuevaPlantilla = await crearPlantilla(plantillaDuplicada);
      setExito('Plantilla duplicada correctamente. Redirigiendo...');
      
      // Navegar a la lista de plantillas guardadas
      setTimeout(() => {
        navigate('/plantillas');
      }, 1500);
    } catch (error) {
      setError('Error al duplicar la plantilla');
    } finally {
      setCargando(false);
    }
  };

  if (cargando && !plantilla) return <div>Cargando...</div>;
  if (error) return <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded mb-4">{error}</div>;
  if (!plantilla) return <div>No se encontró la plantilla.</div>;

  // Lista de campos no asociados
  const camposNoAsociados = campos.filter(c => !plantilla.campos_asociados.some(a => a.campo === c.id));

  return (
    <div className="max-w-6xl mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Editar Plantilla</h2>
      <form onSubmit={handleGuardar} className="space-y-4">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Columna izquierda: editor y campos */}
          <div className="flex-1 min-w-0">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
              <input
                type="text"
                value={nombre}
                onChange={e => setNombre(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
              <textarea
                value={descripcion}
                onChange={e => setDescripcion(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded"
                rows={3}
              />
            </div>
            {tiposPlantilla.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Plantilla</label>
                <select
                  value={tipoSeleccionado || ''}
                  onChange={(e) => {
                    const newValue = e.target.value ? Number(e.target.value) : null;
                    console.log('Cambiando tipo a:', newValue); // Debug
                    setTipoSeleccionado(newValue);
                  }}
                  className="w-full p-2 border border-gray-300 rounded"
                >
                  <option value="">-- Seleccionar tipo de plantilla --</option>
                  {tiposPlantilla.map((tipo) => (
                    <option key={tipo.id} value={tipo.id}>
                      {tipo.nombre}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Tipo seleccionado: {tipoSeleccionado ? tiposPlantilla.find(t => t.id === tipoSeleccionado)?.nombre : 'Ninguno'}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Debug - Valor del select: {tipoSeleccionado || 'null'} | Tipos disponibles: {tiposPlantilla.map(t => t.id).join(', ')}
                </p>
                {plantilla && (
                  <div className="mt-2 p-2 bg-gray-100 rounded text-xs">
                    <p><strong>Debug Plantilla:</strong></p>
                    <p>Tipo directo: {JSON.stringify(plantilla.tipo)}</p>
                    <p>Tipo info: {JSON.stringify(plantilla.tipo_info)}</p>
                    <p>ID del tipo: {plantilla.tipo?.id || plantilla.tipo_info?.id || 'null'}</p>
                  </div>
                )}
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">HTML con campos</label>
              <EditorDocumento
                textoInicial={htmlConCampos}
                camposDisponibles={campos}
                tiposPlantilla={tiposPlantilla}
                onChange={(nuevoHtml, nuevosCampos) => {
                  setHtmlConCampos(nuevoHtml);
                  const camposActualizados = nuevosCampos.map(c => ({ campo_id: c.campo_id, nombre_variable: c.nombre_variable }));
                  setCamposAsignados(camposActualizados);
                  console.log('Campos actualizados desde editor:', camposActualizados); // Debug
                }}
                onPlantillaCreada={() => {}}
                nombreInicial={nombre}
                descripcionInicial={descripcion}
                tipoInicial={plantilla.tipo}
                modoEdicion={true}
              />
              <p className="text-xs text-gray-500 mt-1">Puedes usar variables como {'{{nombre_cliente}}'} en el HTML.</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Campos asociados</label>
              <ul className="list-disc pl-6 text-gray-700 mb-2">
                {plantilla.campos_asociados.map((campo: CampoPlantilla) => {
                  const info = campos.find(c => c.id === campo.campo);
                  return (
                    <li key={campo.id} className="flex items-center gap-2">
                      <span className="font-semibold">{campo.nombre_variable}</span> → {info?.nombre || 'Campo eliminado'} ({info?.tipo_dato || 'N/A'})
                      <button type="button" className="text-red-600 text-xs ml-2 hover:underline" onClick={() => handleQuitarCampo(campo.id)}>Quitar</button>
                    </li>
                  );
                })}
              </ul>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-500">
                  {campos.length} campos disponibles
                </span>
                <div className="flex gap-2">
                  <button type="button" className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700" onClick={() => setModalCampo(true)}>
                    Crear Nuevo Campo
                  </button>
                  <button type="button" className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700" onClick={() => setModalAsociar(true)}>
                    Asociar campo existente
                  </button>
                </div>
              </div>
            </div>
          </div>
          {/* Columna derecha: vista previa */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1 gap-2 flex-wrap">
              <label className="block text-sm font-medium text-gray-700">Vista previa con datos reales</label>
              <div className="flex gap-2">
                <button
                  type="button"
                  className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 text-xs"
                  onClick={() => descargarHtmlPreview(getPreviewHtml(htmlConCampos, plantilla.campos_asociados, datosPreview))}
                >
                  Descargar HTML
                </button>
                <button
                  type="button"
                  className="bg-emerald-700 text-white px-3 py-1 rounded hover:bg-emerald-800 text-xs"
                  onClick={() => descargarPdfPreview(getPreviewHtml(htmlConCampos, plantilla.campos_asociados, datosPreview))}
                >
                  Descargar PDF
                </button>
              </div>
            </div>
            <div className="mb-2 grid grid-cols-1 gap-2">
              {plantilla.campos_asociados.map((campo: CampoPlantilla) => (
                <div key={campo.id}>
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
            <div className="border border-dashed border-gray-300 rounded-md p-4 bg-gray-50 min-h-[120px] prose max-w-none mt-2" 
              dangerouslySetInnerHTML={{ __html: getPreviewHtml(htmlConCampos, plantilla.campos_asociados, datosPreview).replace(/\n/g, '<br>') }} />
          </div>
        </div>
        {exito && <div className="p-3 bg-green-100 border border-green-400 text-green-700 rounded">{exito}</div>}
        {error && <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">{error}</div>}
        <div className="flex gap-2">
          <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" disabled={cargando}>Guardar</button>
          <button type="button" className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700" onClick={handleDuplicar} disabled={cargando}>Duplicar</button>
          <button type="button" className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400" onClick={() => navigate('/plantillas')}>Cancelar</button>
        </div>
      </form>
      <ModalCrearCampo open={modalCampo} onClose={() => setModalCampo(false)} onCrear={handleCrearCampo} cargando={cargandoCampo} />
      {/* Modal asociar campo existente */}
      {modalAsociar && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <form onSubmit={handleAsociarCampo} className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full">
            <h3 className="text-lg font-semibold mb-4">Asociar campo existente</h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Campo</label>
              <select
                value={nuevoAsociado.campo_id}
                onChange={e => setNuevoAsociado({ ...nuevoAsociado, campo_id: Number(e.target.value) })}
                className="w-full p-2 border border-gray-300 rounded"
                required
              >
                <option value="">Selecciona un campo</option>
                {camposNoAsociados.map(c => (
                  <option key={c.id} value={c.id}>{c.nombre} ({c.tipo_dato})</option>
                ))}
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre de variable</label>
              <input
                type="text"
                value={nuevoAsociado.nombre_variable}
                onChange={e => setNuevoAsociado({ ...nuevoAsociado, nombre_variable: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded"
                required
              />
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400" onClick={() => setModalAsociar(false)}>Cancelar</button>
              <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" disabled={cargandoCampo}>Asociar</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default EditarPlantilla; 