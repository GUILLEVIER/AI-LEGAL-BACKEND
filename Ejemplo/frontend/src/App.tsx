import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import SubirDocumento from './components/SubirDocumento';
import EditorDocumento from './components/EditorDocumento';
import GenerarDocumento from './components/GenerarDocumento';
import ListaPlantillas from './components/ListaPlantillas';
import EditarPlantilla from './components/EditarPlantilla';
import FlujoSubirDocumento from './components/FlujoSubirDocumento';
import ListaDocumentosGenerados from './components/ListaDocumentosGenerados';
import ListaFavoritos from './components/ListaFavoritos';
import GestionarTiposPlantilla from './components/GestionarTiposPlantilla';
import PlantillasCompartidasConmigo from './components/PlantillasCompartidasConmigo';
import { 
  SubirDocumentoResponse, 
  CampoDisponible, 
  PlantillaDocumento,
  CrearPlantillaData 
} from './types';
import { 
  getCamposDisponibles, 
  crearCampoDisponible, 
  crearPlantilla, 
  getPlantillas, 
  getPlantilla
} from './services/api';
import Login from './components/Login';

const GenerarDocumentoPage: React.FC = () => {
  const location = useLocation();
  const [plantilla, setPlantilla] = useState<PlantillaDocumento | null>(null);
  const [plantillas, setPlantillas] = useState<PlantillaDocumento[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const params = new URLSearchParams(location.search);
  const plantillaId = params.get('plantilla');

  useEffect(() => {
    getPlantillas().then(setPlantillas);
  }, []);

  useEffect(() => {
    const id = plantillaId || selectedId;
    if (id && plantillas.some(p => p.id === Number(id))) {
      setLoading(true);
      getPlantilla(Number(id)).then(setPlantilla).finally(() => setLoading(false));
    } else {
      setPlantilla(null);
    }
  }, [plantillaId, selectedId, plantillas]);

  // Limpia el estado si la plantilla seleccionada ya no es accesible
  useEffect(() => {
    if (selectedId && !plantillas.some(p => p.id === Number(selectedId))) {
      setSelectedId(null);
    }
  }, [plantillas, selectedId]);

  if ((plantillaId || selectedId) && loading) return <div>Cargando plantilla...</div>;
  if ((plantillaId || selectedId) && !plantilla) return <div>No se encontró la plantilla o no tienes acceso.</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Generar Documento</h2>
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Selecciona una plantilla</label>
        <select
          className="w-full p-2 border border-gray-300 rounded-md max-w-md"
          value={plantilla?.id || ''}
          onChange={e => setSelectedId(e.target.value)}
        >
          <option value="">-- Selecciona una plantilla --</option>
          {plantillas.map(p => (
            <option key={p.id} value={p.id}>{p.nombre}</option>
          ))}
        </select>
      </div>
      {plantilla ? (
        <GenerarDocumento plantilla={plantilla} onDocumentoGenerado={() => {}} />
      ) : (
        <div className="text-gray-600 text-center mt-12">Selecciona una plantilla para generar un documento.</div>
      )}
    </div>
  );
};

const App: React.FC = () => {
  // TODOS los hooks deben ir aquí, antes de cualquier return o condicional
  const [autenticado, setAutenticado] = useState<boolean | null>(null);
  const [paso, setPaso] = useState<'subir' | 'editar' | 'generar'>('subir');
  const [documentoSubido, setDocumentoSubido] = useState<SubirDocumentoResponse | null>(null);
  const [camposDisponibles, setCamposDisponibles] = useState<CampoDisponible[]>([]);
  const [plantillas, setPlantillas] = useState<PlantillaDocumento[]>([]);
  const [plantillaSeleccionada, setPlantillaSeleccionada] = useState<PlantillaDocumento | null>(null);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access');
      if (!token) {
        setAutenticado(false);
        return;
      }
      setAutenticado(true);
    };
    checkAuth();
  }, []);

  useEffect(() => {
    cargarCamposDisponibles();
    cargarPlantillas();
  }, []);

  const cargarCamposDisponibles = async () => {
    try {
      const campos = await getCamposDisponibles();
      setCamposDisponibles(campos);
    } catch (error) {
      console.error('Error al cargar campos:', error);
    }
  };

  const cargarPlantillas = async () => {
    try {
      const plantillasData = await getPlantillas();
      setPlantillas(plantillasData);
    } catch (error) {
      console.error('Error al cargar plantillas:', error);
    }
  };

  const handleDocumentoSubido = (response: SubirDocumentoResponse) => {
    setDocumentoSubido(response);
    setPaso('editar');
  };

  const handlePlantillaCreada = async (htmlConCampos: string, camposAsignados: Array<{campo_id: number, nombre_variable: string}>) => {
    if (!documentoSubido) return;

    setCargando(true);
    try {
      const plantillaData: CrearPlantillaData = {
        nombre: `Plantilla de ${documentoSubido.nombre_original}`,
        descripcion: `Plantilla creada a partir de ${documentoSubido.nombre_original}`,
        html_con_campos: htmlConCampos,
        campos: camposAsignados
      };

      await crearPlantilla(plantillaData);
      await cargarPlantillas(); // Recargar plantillas
      setPaso('generar');
    } catch (error) {
      console.error('Error al crear plantilla:', error);
      alert('Error al crear la plantilla');
    } finally {
      setCargando(false);
    }
  };

  const handleDocumentoGenerado = (htmlResultante: string) => {
    console.log('Documento generado:', htmlResultante);
    // Aquí podrías mostrar una notificación de éxito
  };

  const crearCampoNuevo = async () => {
    const nombre = prompt('Nombre del campo:');
    const tipo = prompt('Tipo de dato (texto/fecha/numero):') as 'texto' | 'fecha' | 'numero';
    
    if (nombre && tipo) {
      try {
        await crearCampoDisponible({ nombre, tipo_dato: tipo });
        await cargarCamposDisponibles();
      } catch (error) {
        console.error('Error al crear campo:', error);
        alert('Error al crear el campo');
      }
    }
  };

  // --- Aquí van los returns condicionales ---
  if (autenticado === null) return <div>Cargando...</div>;
  if (!autenticado) return <Login onLogin={() => setAutenticado(true)} />;

  // --- El resto de tu app ---
  return (
    <Router>
      <div className="flex min-h-screen bg-gray-100">
        <Sidebar />
        <div className="flex-1 ml-64">
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<FlujoSubirDocumento />} />
              <Route path="/plantillas" element={<ListaPlantillas />} />
              <Route path="/plantillas/:id/editar" element={<EditarPlantilla />} />
              <Route path="/favoritos" element={<ListaFavoritos />} />
              <Route path="/tipos-plantilla" element={<GestionarTiposPlantilla />} />
              <Route path="/generar" element={<GenerarDocumentoPage />} />
              <Route path="/documentos-generados" element={<ListaDocumentosGenerados />} />
              <Route path="/compartidas" element={<PlantillasCompartidasConmigo />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
