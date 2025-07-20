import React, { useState } from 'react';

const tiposCampo = [
  { value: 'texto', label: 'Texto' },
  { value: 'fecha', label: 'Fecha' },
  { value: 'numero', label: 'Número' },
];

interface ModalCrearCampoProps {
  open: boolean;
  onClose: () => void;
  onCrear: (campo: { nombre: string; tipo_dato: 'texto' | 'fecha' | 'numero' }) => void;
  cargando?: boolean;
}

const ModalCrearCampo: React.FC<ModalCrearCampoProps> = ({ open, onClose, onCrear, cargando }) => {
  const [nombre, setNombre] = useState('');
  const [tipo, setTipo] = useState<'texto' | 'fecha' | 'numero'>('texto');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!nombre.trim()) {
      alert('El nombre del campo es obligatorio');
      return;
    }
    onCrear({ nombre, tipo_dato: tipo });
    setNombre('');
    setTipo('texto');
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full">
        <h3 className="text-lg font-semibold mb-4">Nuevo Campo</h3>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
          <input
            type="text"
            value={nombre}
            onChange={e => setNombre(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de dato</label>
          <select
            value={tipo}
            onChange={e => setTipo(e.target.value as 'texto' | 'fecha' | 'numero')}
            className="w-full p-2 border border-gray-300 rounded"
            required
          >
            {tiposCampo.map(t => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>
        <div className="flex gap-2 justify-end">
          <button type="button" className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400" onClick={onClose}>Cancelar</button>
          <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" disabled={cargando}>Guardar</button>
        </div>
      </form>
    </div>
  );
};

export default ModalCrearCampo; 