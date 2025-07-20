import React, { useState, useEffect, useRef } from 'react';
import { PlantillaDocumento, CampoPlantilla } from '../types';
import { generarDocumento } from '../services/api';
import html2pdf from 'html2pdf.js';
import { Document, Packer, Paragraph, TextRun } from 'docx';

interface GenerarDocumentoProps {
  plantilla: PlantillaDocumento;
  onDocumentoGenerado: (htmlResultante: string) => void;
}

function getPreviewHtml(html: string, campos: CampoPlantilla[], datos: Record<string, string>, onClickVar?: (nombre: string) => void) {
  let preview = html;
  campos.forEach(campo => {
    const valor = datos[campo.nombre_variable]?.trim();
    const span = `<span class="preview-var" data-var="${campo.nombre_variable}">${valor || `{{${campo.nombre_variable}}}`}</span>`;
    preview = preview.replaceAll(`{{${campo.nombre_variable}}}`, span);
  });
  return preview;
}

function descargarPdfPreview(html: string) {
  const container = document.createElement('div');
  container.innerHTML = html;
  // Estilos limpios y tamaño A4
  container.style.width = '210mm'; // A4 width
  container.style.minHeight = '297mm'; // A4 height
  container.style.overflow = 'visible';
  container.style.padding = '0';
  container.style.margin = '0';
  container.style.background = 'white';
  html2pdf().from(container).set({
    margin: 10,
    filename: 'documento_generado.pdf',
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  }).save();
}

async function descargarWordPreview(html: string) {
  try {
    // Crear un elemento temporal para parsear el HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    
    // Convertir el HTML a párrafos de Word
    const children = Array.from(tempDiv.childNodes);
    const paragraphs: Paragraph[] = [];
    
    children.forEach(child => {
      if (child.nodeType === Node.TEXT_NODE) {
        // Texto simple
        const text = child.textContent?.trim();
        if (text) {
          paragraphs.push(
            new Paragraph({
              children: [
                new TextRun({
                  text: text,
                  size: 24, // 12pt
                  font: 'Times New Roman'
                })
              ]
            })
          );
        }
      } else if (child.nodeType === Node.ELEMENT_NODE) {
        const element = child as HTMLElement;
        const tagName = element.tagName.toLowerCase();
        
        if (tagName === 'p' || tagName === 'div') {
          // Párrafo
          const text = element.textContent?.trim();
          if (text) {
            paragraphs.push(
              new Paragraph({
                children: [
                  new TextRun({
                    text: text,
                    size: 24, // 12pt
                    font: 'Times New Roman'
                  })
                ]
              })
            );
          }
        } else if (tagName === 'br') {
          // Salto de línea
          paragraphs.push(
            new Paragraph({
              children: [
                new TextRun({
                  text: '',
                  size: 24
                })
              ]
            })
          );
        } else if (tagName === 'h1' || tagName === 'h2' || tagName === 'h3' || tagName === 'h4' || tagName === 'h5' || tagName === 'h6') {
          // Encabezados
          const text = element.textContent?.trim();
          if (text) {
            paragraphs.push(
              new Paragraph({
                children: [
                  new TextRun({
                    text: text,
                    size: tagName === 'h1' ? 36 : tagName === 'h2' ? 32 : 28, // 18pt, 16pt, 14pt
                    font: 'Times New Roman',
                    bold: true
                  })
                ]
              })
            );
          }
        }
      }
    });
    
    // Crear el documento Word
    const docx = new Document({
      sections: [
        {
          properties: {},
          children: paragraphs
        }
      ]
    });
    
    // Generar el archivo
    const blob = await Packer.toBlob(docx);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'documento_generado.docx';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error al generar documento Word:', error);
    alert('Error al generar el documento Word. Intenta descargar en PDF.');
  }
}

const GenerarDocumento: React.FC<GenerarDocumentoProps> = ({
  plantilla,
  onDocumentoGenerado
}) => {
  const [datos, setDatos] = useState<Record<string, any>>({});
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [focusedVar, setFocusedVar] = useState<string | null>(null);
  const [mensaje, setMensaje] = useState('');
  const [mensajeTipo, setMensajeTipo] = useState<'exito' | 'error' | ''>('');
  const inputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  useEffect(() => {
    // Inicializar datos vacíos para cada campo
    const datosIniciales: Record<string, any> = {};
    plantilla.campos_asociados.forEach(campo => {
      datosIniciales[campo.nombre_variable] = '';
    });
    setDatos(datosIniciales);
  }, [plantilla]);

  const handleInputChange = (nombreVariable: string, valor: string) => {
    setDatos(prev => ({
      ...prev,
      [nombreVariable]: valor
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setMensaje('');
    setMensajeTipo('');
    setCargando(true);
    setError(null);

    try {
      const response = await generarDocumento(plantilla.id, datos);
      onDocumentoGenerado(response.html_resultante);
      setMensaje('¡Documento generado correctamente!');
      setMensajeTipo('exito');
    } catch (err) {
      setMensaje('Error al generar el documento. Por favor intenta de nuevo.');
      setMensajeTipo('error');
      setError('Error al generar el documento. Por favor intenta de nuevo.');
      console.error('Error:', err);
    } finally {
      setCargando(false);
    }
  };

  // Manejar click en variable de la vista previa
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.classList.contains('preview-var')) {
        const varName = target.getAttribute('data-var');
        if (varName && inputRefs.current[varName]) {
          setFocusedVar(varName);
          inputRefs.current[varName]?.focus();
        }
      }
    };
    document.addEventListener('click', handler);
    return () => document.removeEventListener('click', handler);
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Generar Documento</h2>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Plantilla: {plantilla.nombre}</h3>
        <p className="text-gray-600">{plantilla.descripcion}</p>
      </div>

      {mensaje && (
        <div className={`p-3 rounded mb-4 ${mensajeTipo === 'exito' ? 'bg-green-100 border border-green-400 text-green-700' : 'bg-red-100 border border-red-400 text-red-700'}`}>
          {mensaje}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-4">Datos del Documento</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {plantilla.campos_asociados.map((campo) => (
              <div key={campo.id} className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  {campo.campo_nombre} ({campo.campo_tipo})
                </label>
                <input
                  ref={(el) => { inputRefs.current[campo.nombre_variable] = el; }}
                  type={campo.campo_tipo === 'fecha' ? 'date' : 
                        campo.campo_tipo === 'numero' ? 'number' : 'text'}
                  value={datos[campo.nombre_variable] || ''}
                  onChange={(e) => handleInputChange(campo.nombre_variable, e.target.value)}
                  className={`w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${focusedVar === campo.nombre_variable ? 'ring-2 ring-emerald-700 border-emerald-700' : ''}`}
                  placeholder={`Ingresa ${campo.campo_nombre.toLowerCase()}`}
                  required
                />
                <p className="text-xs text-gray-500">
                  Variable: {campo.nombre_variable}
                </p>
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={cargando}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {cargando ? 'Generando...' : 'Generar Documento'}
        </button>
      </form>

      {/* Vista previa y botón de PDF SIEMPRE visibles */}
      <div className="mt-8">
        <div className="flex items-center justify-between mb-1 gap-2 flex-wrap">
          <h3 className="text-lg font-semibold">Vista previa</h3>
          <div className="flex gap-2">
            <button
              type="button"
              className="bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 text-xs"
              onClick={() => descargarWordPreview(getPreviewHtml(plantilla.html_con_campos, plantilla.campos_asociados, datos))}
            >
              Descargar Word
            </button>
            <button
              type="button"
              className="bg-emerald-700 text-white px-3 py-1 rounded hover:bg-emerald-800 text-xs"
              onClick={() => descargarPdfPreview(getPreviewHtml(plantilla.html_con_campos, plantilla.campos_asociados, datos))}
            >
              Descargar PDF
            </button>
          </div>
        </div>
        <div
          className="border border-dashed border-gray-300 rounded-md p-4 bg-gray-50 min-h-[120px] prose max-w-none mt-2 cursor-pointer"
          dangerouslySetInnerHTML={{ __html: getPreviewHtml(plantilla.html_con_campos, plantilla.campos_asociados, datos) }}
        />
      </div>
    </div>
  );
};

export default GenerarDocumento; 