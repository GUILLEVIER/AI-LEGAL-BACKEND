import React, { useState, useEffect } from 'react';
import SubirDocumento from './SubirDocumento';
import EditorDocumento from './EditorDocumento';
import { SubirDocumentoResponse, CampoDisponible, CrearPlantillaData, TipoPlantillaDocumento } from '../types';
import { getCamposDisponibles, crearCampoDisponible, crearPlantilla, getPlantillas, getTiposPlantilla } from '../services/api';
import ModalCrearCampo from './ModalCrearCampo';

const tiposCampo = [
  { value: 'texto', label: 'Texto' },
  { value: 'fecha', label: 'Fecha' },
  { value: 'numero', label: 'Número' },
];

const FlujoSubirDocumento: React.FC = () => {
  const [paso, setPaso] = useState<'subir' | 'editar'>('subir');
  const [documentoSubido, setDocumentoSubido] = useState<SubirDocumentoResponse | null>(null);
  const [camposDisponibles, setCamposDisponibles] = useState<CampoDisponible[]>([]);
  const [tiposPlantilla, setTiposPlantilla] = useState<TipoPlantillaDocumento[]>([]);
  const [cargando, setCargando] = useState(false);
  const [exito, setExito] = useState<string | null>(null);
  const [modalCampo, setModalCampo] = useState(false);
  const [nuevoCampo, setNuevoCampo] = useState({ nombre: '', tipo_dato: 'texto' });

  useEffect(() => {
    cargarCamposDisponibles();
    cargarTiposPlantilla();
  }, []);

  const cargarCamposDisponibles = async () => {
    try {
      const campos = await getCamposDisponibles();
      setCamposDisponibles(campos);
    } catch (error) {
      // Manejar error
    }
  };

  const cargarTiposPlantilla = async () => {
    try {
      const tipos = await getTiposPlantilla();
      setTiposPlantilla(tipos);
    } catch (error) {
      // Manejar error
    }
  };

  const handleDocumentoSubido = (response: SubirDocumentoResponse) => {
    setDocumentoSubido(response);
    setPaso('editar');
  };

  const handlePlantillaCreada = async (nombre: string, descripcion: string, htmlConCampos: string, camposAsignados: Array<{campo_id: number, nombre_variable: string}>, tipoId?: number) => {
    if (!documentoSubido) return;
    setCargando(true);
    try {
      const plantillaData: CrearPlantillaData = {
        nombre,
        descripcion,
        html_con_campos: htmlConCampos,
        tipo_id: tipoId,
        campos: camposAsignados
      };
      await crearPlantilla(plantillaData);
      setExito('¡Plantilla creada exitosamente!');
      setPaso('subir');
      setDocumentoSubido(null);
      await cargarCamposDisponibles();
    } catch (error) {
      // Manejar error
    } finally {
      setCargando(false);
    }
  };

  const handleCrearCampo = async (campo: { nombre: string; tipo_dato: 'texto' | 'fecha' | 'numero' }) => {
    setCargando(true);
    try {
      await crearCampoDisponible(campo);
      await cargarCamposDisponibles();
      setModalCampo(false);
    } catch (error) {
      alert('Error al crear el campo');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div>
      {paso === 'subir' && (
        <div>
          <h2 className="text-2xl font-bold text-center mb-6">Subir Documento</h2>
          {exito && <div className="p-3 bg-green-100 border border-green-400 text-green-700 rounded mb-4 text-center">{exito}</div>}
          <SubirDocumento onDocumentoSubido={handleDocumentoSubido} />
        </div>
      )}
      {paso === 'editar' && documentoSubido && (
        <div>
          <h2 className="text-2xl font-bold text-center mb-6">Editar Documento</h2>

          <EditorDocumento
            textoInicial={documentoSubido.texto_extraido}
            camposDisponibles={camposDisponibles}
            tiposPlantilla={tiposPlantilla}
            onPlantillaCreada={handlePlantillaCreada}
            onCrearCampo={() => setModalCampo(true)}
          />
        </div>
      )}
      <ModalCrearCampo open={modalCampo} onClose={() => setModalCampo(false)} onCrear={handleCrearCampo} cargando={cargando} />
      {cargando && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <p className="text-lg">Procesando...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FlujoSubirDocumento; 