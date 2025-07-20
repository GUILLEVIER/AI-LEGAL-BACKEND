import React, { useState } from 'react';
import { subirDocumento } from '../services/api';
import { SubirDocumentoResponse } from '../types';

interface SubirDocumentoProps {
  onDocumentoSubido: (response: SubirDocumentoResponse) => void;
}

const SubirDocumento: React.FC<SubirDocumentoProps> = ({ onDocumentoSubido }) => {
  const [archivo, setArchivo] = useState<File | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleArchivoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setArchivo(file);
      setError(null);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!archivo) {
      setError('Por favor selecciona un archivo');
      return;
    }

    setCargando(true);
    setError(null);

    try {
      const response = await subirDocumento(archivo);
      onDocumentoSubido(response);
      setArchivo(null);
      // Limpiar el input
      const fileInput = document.getElementById('archivo') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (err) {
      setError('Error al subir el documento. Por favor intenta de nuevo.');
      console.error('Error:', err);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Subir Documento</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="archivo" className="block text-sm font-medium text-gray-700 mb-2">
            Seleccionar archivo
          </label>
          <input
            id="archivo"
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.gif,.txt,.docx"
            onChange={handleArchivoChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            required
          />
          <p className="mt-1 text-xs text-gray-500">
            Formatos soportados: PDF, JPG, PNG, GIF, TXT, DOCX
          </p>
        </div>

        {error && (
          <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={cargando || !archivo}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {cargando ? 'Subiendo...' : 'Subir Documento'}
        </button>
      </form>

      {archivo && (
        <div className="mt-4 p-3 bg-gray-50 rounded-md">
          <p className="text-sm text-gray-600">
            <strong>Archivo seleccionado:</strong> {archivo.name}
          </p>
          <p className="text-xs text-gray-500">
            Tamaño: {(archivo.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>
      )}
    </div>
  );
};

export default SubirDocumento; 