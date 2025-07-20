import React, { useEffect, useState } from 'react';
import { PlantillaDocumento } from '../types';
import { compartirPlantilla, revocarCompartida, getUsuarios, UsuarioSimple, getUsuariosCompartidos, UsuarioCompartido } from '../services/api';

interface ModalCompartirPlantillaProps {
  open: boolean;
  onClose: () => void;
  plantilla: PlantillaDocumento;
  onCompartido: () => void;
}

const ModalCompartirPlantilla: React.FC<ModalCompartirPlantillaProps> = ({ open, onClose, plantilla, onCompartido }) => {
  const [usuarios, setUsuarios] = useState<UsuarioSimple[]>([]);
  const [usuariosSeleccionados, setUsuariosSeleccionados] = useState<number[]>([]);
  const [permisos, setPermisos] = useState<'lectura' | 'edicion'>('lectura');
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [revocando, setRevocando] = useState<number | null>(null);
  const [usuariosCompartidos, setUsuariosCompartidos] = useState<UsuarioCompartido[]>([]);

  const cargarUsuariosCompartidos = async () => {
    if (!plantilla?.id) return;
    const data = await getUsuariosCompartidos(plantilla.id);
    setUsuariosCompartidos(data);
  };

  useEffect(() => {
    if (open) {
      setMensaje(null);
      setUsuariosSeleccionados([]);
      getUsuarios().then(setUsuarios).catch(() => setUsuarios([]));
      cargarUsuariosCompartidos();
    }
    // eslint-disable-next-line
  }, [open, plantilla?.id]);

  const toggleUsuario = (id: number) => {
    setUsuariosSeleccionados(prev =>
      prev.includes(id) ? prev.filter(uid => uid !== id) : [...prev, id]
    );
  };

  const handleCompartir = async () => {
    if (usuariosSeleccionados.length === 0) return;
    setCargando(true);
    setMensaje(null);
    try {
      await compartirPlantilla(plantilla.id, undefined, permisos, usuariosSeleccionados);
      setMensaje('¡Plantilla compartida!');
      setUsuariosSeleccionados([]);
      await cargarUsuariosCompartidos();
      onCompartido();
    } catch (e: any) {
      setMensaje('Error al compartir la plantilla');
    } finally {
      setCargando(false);
    }
  };

  const handleRevocar = async (compartidaId: number) => {
    setRevocando(compartidaId);
    try {
      await revocarCompartida(compartidaId);
      await cargarUsuariosCompartidos();
      onCompartido();
    } catch (e: any) {
      setMensaje('Error al revocar acceso');
    } finally {
      setRevocando(null);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-lg w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Compartir plantilla: {plantilla.nombre}</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-xl">✕</button>
        </div>
        {mensaje && <div className={`p-2 mb-2 rounded ${mensaje.startsWith('¡') ? 'bg-green-100 border border-green-400 text-green-700' : 'bg-red-100 border border-red-400 text-red-700'}`}>{mensaje}</div>}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Selecciona un usuario</label>
          <div className="max-h-40 overflow-y-auto border rounded bg-gray-50">
            {usuarios.length === 0 && <div className="p-2 text-gray-500">No hay otros usuarios.</div>}
            {usuarios.map(u => (
              <div key={u.id} className={`flex items-center gap-2 px-2 py-1 cursor-pointer ${usuariosSeleccionados.includes(u.id) ? 'bg-blue-100' : ''}`}
                onClick={() => toggleUsuario(u.id)}
              >
                <input type="checkbox" checked={usuariosSeleccionados.includes(u.id)} readOnly />
                <span className="font-semibold">{u.username}</span>
                <span className="text-xs text-gray-500">{u.email}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Permisos</label>
          <select
            value={permisos}
            onChange={e => setPermisos(e.target.value as 'lectura' | 'edicion')}
            className="w-full p-2 border border-gray-300 rounded"
          >
            <option value="lectura">Solo lectura</option>
            <option value="edicion">Lectura y edición</option>
          </select>
        </div>
        <button
          onClick={handleCompartir}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 w-full mb-4"
          disabled={cargando || usuariosSeleccionados.length === 0}
        >
          {cargando ? 'Compartiendo...' : 'Compartir'}
        </button>
        <div>
          <h4 className="text-sm font-semibold mb-2">Usuarios con acceso:</h4>
          {usuariosCompartidos.length === 0 && <p className="text-gray-500 text-sm">Nadie más tiene acceso a esta plantilla.</p>}
          <ul className="divide-y divide-gray-200">
            {usuariosCompartidos.map(c => (
              <li key={c.id} className="flex items-center gap-2 py-2">
                <span className="font-semibold">{c.usuario_username}</span>
                <span className="text-xs text-gray-500">({c.permisos})</span>
                <span className="text-xs text-gray-400 ml-auto">{new Date(c.fecha_compartida).toLocaleString()}</span>
                <button
                  onClick={() => handleRevocar(c.id)}
                  className="ml-2 text-red-600 hover:underline text-xs"
                  disabled={revocando === c.id}
                >
                  {revocando === c.id ? 'Revocando...' : 'Revocar'}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ModalCompartirPlantilla; 