import React, { useEffect, useState } from 'react';
import html2pdf from 'html2pdf.js';
import { Document, Packer, Paragraph, TextRun } from 'docx';
import { getDocumentosGenerados, getDocumentoGenerado, eliminarPlantilla } from '../services/api';
import { DocumentoGenerado } from '../types';

const ListaDocumentosGenerados: React.FC = () => {
  const [documentos, setDocumentos] = useState<DocumentoGenerado[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewDoc, setPreviewDoc] = useState<DocumentoGenerado | null>(null);
  const [modalEliminar, setModalEliminar] = useState<{ mostrar: boolean; documento: DocumentoGenerado | null }>({ mostrar: false, documento: null });

  const cargarDocumentos = async () => {
    setCargando(true);
    try {
      const data = await getDocumentosGenerados();
      setDocumentos(data);
    } catch (e) {
      setError('Error al cargar documentos generados');
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDocumentos();
  }, []);

  const descargarHtml = (doc: DocumentoGenerado) => {
    const blob = new Blob([doc.html_resultante], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `documento_${doc.id}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const descargarPdf = (doc: DocumentoGenerado) => {
    const container = document.createElement('div');
    container.innerHTML = doc.html_resultante;
    html2pdf().from(container).set({
      margin: 10,
      filename: `documento_${doc.id}.pdf`,
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }).save();
  };

  const descargarWord = async (doc: DocumentoGenerado) => {
    try {
      // Crear un elemento temporal para parsear el HTML
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = doc.html_resultante;
      
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
      a.download = `documento_${doc.id}.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error al generar documento Word:', error);
      alert('Error al generar el documento Word. Intenta descargar en HTML o PDF.');
    }
  };

  const eliminarDocumento = (documento: DocumentoGenerado) => {
    setModalEliminar({ mostrar: true, documento });
  };

  const confirmarEliminar = async () => {
    if (!modalEliminar.documento) return;
    
    setCargando(true);
    try {
      await eliminarPlantilla(modalEliminar.documento.id);
      await cargarDocumentos();
      setModalEliminar({ mostrar: false, documento: null });
    } catch (e) {
      setError('Error al eliminar el documento');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded shadow">
      <h2 className="text-2xl font-bold mb-6">Documentos Generados</h2>
      {cargando && <p>Cargando...</p>}
      {error && <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded mb-4">{error}</div>}
      <div className="space-y-4">
        {documentos.map(doc => (
          <div key={doc.id} className="bg-gray-50 rounded p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-2 border border-gray-200">
            <div>
              <div className="font-semibold text-gray-800">Plantilla: {doc.plantilla_nombre}</div>
              <div className="text-xs text-gray-500">Generado: {new Date(doc.fecha_generacion).toLocaleString()}</div>
              <div className="text-xs text-gray-500">ID: {doc.id}</div>
            </div>
            <div className="flex gap-2 flex-wrap">
              <button onClick={() => setPreviewDoc(doc)} className="bg-gray-700 text-white px-3 py-1 rounded hover:bg-gray-800 text-xs">Vista previa</button>
              <button onClick={() => descargarHtml(doc)} className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 text-xs">Descargar HTML</button>
              <button onClick={() => descargarWord(doc)} className="bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 text-xs">Descargar Word</button>
              <button onClick={() => descargarPdf(doc)} className="bg-emerald-700 text-white px-3 py-1 rounded hover:bg-emerald-800 text-xs">Descargar PDF</button>
              <button onClick={() => eliminarDocumento(doc)} className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 text-xs">Eliminar</button>
            </div>
          </div>
        ))}
      </div>
      {documentos.length === 0 && !cargando && (
        <div className="text-center text-gray-500 py-12">No hay documentos generados.</div>
      )}
      {/* Modal de vista previa */}
      {previewDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg max-w-5xl w-full mx-4 p-6 relative overflow-y-auto max-h-[90vh]" style={{ width: '95vw', maxWidth: '1400px' }}>
            <button
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 text-xl"
              onClick={() => setPreviewDoc(null)}
              title="Cerrar"
            >
              ×
            </button>
            <h3 className="text-lg font-semibold mb-4">Vista previa documento #{previewDoc.id}</h3>
            <div className="prose max-w-none border border-gray-200 rounded p-4 bg-gray-50 mb-4" style={{ minHeight: 120 }}
              dangerouslySetInnerHTML={{ __html: previewDoc.html_resultante }}
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => descargarHtml(previewDoc)} className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 text-xs">Descargar HTML</button>
              <button onClick={() => descargarWord(previewDoc)} className="bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 text-xs">Descargar Word</button>
              <button onClick={() => descargarPdf(previewDoc)} className="bg-emerald-700 text-white px-3 py-1 rounded hover:bg-emerald-800 text-xs">Descargar PDF</button>
              <button onClick={() => setPreviewDoc(null)} className="bg-gray-300 text-gray-700 px-6 py-1 rounded hover:bg-gray-400 text-xs">Cerrar</button>
            </div>
          </div>
        </div>
      )}
      
      {/* Modal de confirmación para eliminar */}
      {modalEliminar.mostrar && modalEliminar.documento && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full">
            <h3 className="text-lg font-semibold mb-4">Confirmar eliminación</h3>
            <p className="text-gray-600 mb-6">
              ¿Seguro que deseas eliminar el documento generado de la plantilla <strong>"{modalEliminar.documento.plantilla_nombre}"</strong>?
            </p>
            <p className="text-sm text-gray-500 mb-2">
              ID: {modalEliminar.documento.id}
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Generado: {new Date(modalEliminar.documento.fecha_generacion).toLocaleString()}
            </p>
            <p className="text-sm text-red-600 mb-6">
              Esta acción no se puede deshacer.
            </p>
            <div className="flex gap-2 justify-end">
              <button 
                onClick={() => setModalEliminar({ mostrar: false, documento: null })} 
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
    </div>
  );
};

export default ListaDocumentosGenerados; 