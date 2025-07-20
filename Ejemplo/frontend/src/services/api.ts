import axios from 'axios';
import {
  DocumentoSubido,
  CampoDisponible,
  PlantillaDocumento,
  DocumentoGenerado,
  CrearPlantillaData,
  GenerarDocumentoData,
  SubirDocumentoResponse,
  TipoPlantillaDocumento,
  PlantillaCompartida
} from '../types';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token JWT a cada petición
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access');
    if (token) {
      config.headers = config.headers || {};
      // @ts-ignore
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;

// Documentos subidos
export const subirDocumento = async (archivo: File): Promise<SubirDocumentoResponse> => {
  const formData = new FormData();
  formData.append('archivo', archivo);
  
  const response = await api.post('/documentos-subidos/subir_documento/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocumentosSubidos = async (): Promise<DocumentoSubido[]> => {
  const response = await api.get('/documentos-subidos/');
  return response.data;
};

// Campos disponibles
export const getCamposDisponibles = async (): Promise<CampoDisponible[]> => {
  const response = await api.get('/campos-disponibles/');
  return response.data;
};

export const crearCampoDisponible = async (campo: Omit<CampoDisponible, 'id'>): Promise<CampoDisponible> => {
  const response = await api.post('/campos-disponibles/', campo);
  return response.data;
};

// Plantillas
export const getPlantillas = async (): Promise<PlantillaDocumento[]> => {
  const response = await api.get('/plantillas/');
  return response.data;
};

export const crearPlantilla = async (plantillaData: CrearPlantillaData): Promise<{ id: number; mensaje: string }> => {
  const response = await api.post('/plantillas/crear_plantilla/', plantillaData);
  return response.data;
};

export const duplicarPlantilla = async (plantillaData: CrearPlantillaData): Promise<PlantillaDocumento> => {
  const response = await api.post('/plantillas/crear_plantilla/', plantillaData);
  return response.data;
};

export const getPlantilla = async (id: number): Promise<PlantillaDocumento> => {
  const response = await api.get(`/plantillas/${id}/`);
  return response.data;
};

export const generarDocumento = async (plantillaId: number, datos: Record<string, any>): Promise<{
  id: number;
  html_resultante: string;
  mensaje: string;
}> => {
  const response = await api.post(`/plantillas/${plantillaId}/generar_documento/`, {
    plantilla_id: plantillaId,
    datos
  });
  return response.data;
};

// Documentos generados
export const getDocumentosGenerados = async (): Promise<DocumentoGenerado[]> => {
  const response = await api.get('/documentos-generados/');
  return response.data;
};

export const getDocumentoGenerado = async (id: number): Promise<DocumentoGenerado> => {
  const response = await api.get(`/documentos-generados/${id}/`);
  return response.data;
};

// Favoritos
export const agregarFavorito = async (plantillaId: number): Promise<{ message: string }> => {
  const response = await api.post('/favoritos/agregar_favorito/', { plantilla_id: plantillaId });
  return response.data;
};

export const quitarFavorito = async (plantillaId: number): Promise<{ message: string }> => {
  const response = await api.delete('/favoritos/quitar_favorito/', { data: { plantilla_id: plantillaId } });
  return response.data;
};

export const getMisFavoritos = async (): Promise<PlantillaDocumento[]> => {
  const response = await api.get('/favoritos/mis_favoritos/');
  return response.data;
};

// Tipos de plantilla
export const getTiposPlantilla = async (): Promise<TipoPlantillaDocumento[]> => {
  const response = await api.get('/tipos-plantilla/');
  return response.data;
};

export const crearTipoPlantilla = async (tipo: Omit<TipoPlantillaDocumento, 'id'>): Promise<TipoPlantillaDocumento> => {
  const response = await api.post('/tipos-plantilla/', tipo);
  return response.data;
}; 

// Compartir plantilla con usuario
export const compartirPlantilla = async (
  plantillaId: number,
  usuarioId?: number,
  permisos: 'lectura' | 'edicion' = 'lectura',
  usuarioIds?: number[]
) => {
  const data: any = { plantilla_id: plantillaId, permisos };
  if (usuarioIds && usuarioIds.length > 0) {
    data.usuario_ids = usuarioIds;
  } else if (usuarioId) {
    data.usuario_id = usuarioId;
  }
  return api.post('/compartidas/compartir/', data);
};

// Revocar acceso a una plantilla compartida
export const revocarCompartida = async (compartidaId: number): Promise<{ message: string }> => {
  const response = await api.delete(`/compartidas/${compartidaId}/revocar/`);
  return response.data;
};

// Listar plantillas compartidas conmigo
export const getPlantillasCompartidasConmigo = async (): Promise<PlantillaCompartida[]> => {
  const response = await api.get('/compartidas/compartidas_conmigo/');
  return response.data;
}; 

// Eliminar plantilla
export const eliminarPlantilla = async (id: number) => {
  return api.delete(`/plantillas/${id}/`);
};

// Actualizar plantilla (PATCH)
export const actualizarPlantilla = async (id: number, data: any) => {
  return api.patch(`/plantillas/${id}/`, data);
}; 

export interface UsuarioSimple {
  id: number;
  username: string;
  email: string;
}

export const getUsuarios = async (): Promise<UsuarioSimple[]> => {
  const response = await api.get('/usuarios/');
  return response.data;
}; 

export interface UsuarioCompartido {
  id: number;
  usuario: number;
  usuario_username: string;
  usuario_email: string;
  permisos: 'lectura' | 'edicion';
  fecha_compartida: string;
}

export const getUsuariosCompartidos = async (plantillaId: number): Promise<UsuarioCompartido[]> => {
  const response = await api.get(`/compartidas/usuarios_compartidos/?plantilla_id=${plantillaId}`);
  return response.data;
}; 