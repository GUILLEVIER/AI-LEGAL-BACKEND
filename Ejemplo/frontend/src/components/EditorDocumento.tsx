import React, { useState, useEffect, useRef } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import { Mark, mergeAttributes } from '@tiptap/core';
import { TextStyle } from '@tiptap/extension-text-style';
import { FontFamily } from '@tiptap/extension-font-family';
import { FontSize } from '@tiptap/extension-font-size';
import { TextAlign } from '@tiptap/extension-text-align';
import { CampoDisponible, TipoPlantillaDocumento } from '../types';
import './EditorDocumento.css';

interface EditorDocumentoProps {
  textoInicial: string;
  camposDisponibles: CampoDisponible[];
  tiposPlantilla?: TipoPlantillaDocumento[];
  onPlantillaCreada: (nombre: string, descripcion: string, htmlConCampos: string, camposAsignados: Array<{campo_id: number, nombre_variable: string}>, tipoId?: number) => void;
  onChange?: (htmlConCampos: string, camposAsignados: Array<{campo_id: number, nombre_variable: string}>) => void;
  onCrearCampo?: () => void;
  nombreInicial?: string;
  descripcionInicial?: string;
  tipoInicial?: TipoPlantillaDocumento;
  modoEdicion?: boolean;
}

interface CampoAsignado {
  campo_id: number;
  nombre_variable: string;
  texto_seleccionado: string;
}

// Extensión para resaltar variables {{campo}}
const VariableMark = Mark.create({
  name: 'variable',
  inclusive: false,
  parseHTML() {
    return [
      {
        tag: 'span[data-variable]',
      },
    ];
  },
  renderHTML({ HTMLAttributes }) {
    return [
      'span',
      mergeAttributes(HTMLAttributes, { 'data-variable': 'true', class: 'variable-highlight' }),
      0,
    ];
  },
  addInputRules() {
    return [
      {
        find: /\{\{([a-zA-Z0-9_]+)\}\}/g,
        handler: ({ state, range, match }) => {
          state.tr.addMark(range.from, range.to, this.type.create());
        },
      },
    ];
  },
});

const EditorDocumento: React.FC<EditorDocumentoProps> = ({
  textoInicial,
  camposDisponibles,
  tiposPlantilla = [],
  onPlantillaCreada,
  onChange,
  onCrearCampo,
  nombreInicial = '',
  descripcionInicial = '',
  tipoInicial,
  modoEdicion = false
}) => {
  const [camposAsignados, setCamposAsignados] = useState<CampoAsignado[]>([]);
  const [campoSeleccionado, setCampoSeleccionado] = useState<number | null>(null);
  const [nombreVariable, setNombreVariable] = useState('');
  const [mostrarModal, setMostrarModal] = useState(false);
  const [nombre, setNombre] = useState(nombreInicial);
  const [descripcion, setDescripcion] = useState(descripcionInicial);
  const [tipoSeleccionado, setTipoSeleccionado] = useState<number | null>(tipoInicial?.id || null);

  const [selectionTimeout, setSelectionTimeout] = useState<NodeJS.Timeout | null>(null);

  // Cleanup timeout cuando el componente se desmonte
  useEffect(() => {
    return () => {
      if (selectionTimeout) {
        clearTimeout(selectionTimeout);
      }
    };
  }, [selectionTimeout]);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: 'Edita tu documento aquí...',
      }),
      VariableMark,
      TextStyle,
      FontFamily,
      FontSize,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
    ],
    content: textoInicial,
    onUpdate: ({ editor }) => {
      // Llama a onChange si está definido
      const htmlConCampos = editor.getHTML();
      if (onChange) {
        onChange(htmlConCampos, camposAsignados);
      }
    },
    onSelectionUpdate: ({ editor }) => {
      const { from, to } = editor.state.selection;
      
      // Limpiar timeout anterior si existe
      if (selectionTimeout) {
        clearTimeout(selectionTimeout);
      }
      
      if (from !== to) {
        const textoSeleccionado = editor.state.doc.textBetween(from, to);
        if (textoSeleccionado.trim() && textoSeleccionado.length > 1) {
          // Agregar delay de 500ms para permitir completar la selección
          const timeout = setTimeout(() => {
            setMostrarModal(true);
          }, 700); // 1 segundo
          setSelectionTimeout(timeout);
        }
      } else {
        // Si no hay selección, ocultar modal después de un delay
        const timeout = setTimeout(() => {
          setMostrarModal(false);
        }, 200);
        setSelectionTimeout(timeout);
      }
    },
  });

  const asignarCampo = () => {
    if (!campoSeleccionado || !nombreVariable.trim() || !editor) {
      alert('Por favor selecciona un campo y proporciona un nombre de variable');
      return;
    }

    const { from, to } = editor.state.selection;
    if (from !== to) {
      const textoSeleccionado = editor.state.doc.textBetween(from, to);
      
      // Reemplazar el texto seleccionado con la variable
      const variable = `{{${nombreVariable}}}`;
      editor.chain().focus().deleteRange({ from, to }).insertContent(variable).run();
      
      // Agregar a la lista de campos asignados
      const nuevoCampo: CampoAsignado = {
        campo_id: campoSeleccionado,
        nombre_variable: nombreVariable,
        texto_seleccionado: textoSeleccionado
      };
      
      const nuevosCamposAsignados = [...camposAsignados, nuevoCampo];
      setCamposAsignados(nuevosCamposAsignados);
      
      // Notificar al componente padre sobre el cambio
      if (onChange) {
        const htmlConCampos = editor.getHTML();
        console.log('Asignando campo:', nuevoCampo); // Debug
        console.log('Total campos asignados:', nuevosCamposAsignados); // Debug
        onChange(htmlConCampos, nuevosCamposAsignados);
      }
      
      // Limpiar el modal
      setCampoSeleccionado(null);
      setNombreVariable('');
      setMostrarModal(false);
    }
  };

  const crearPlantilla = () => {
    if (editor) {
      const htmlConCampos = editor.getHTML();
      onPlantillaCreada(nombre, descripcion, htmlConCampos, camposAsignados, tipoSeleccionado || undefined);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Editor de Documento</h2>
        <div className="flex items-center gap-4">
          {onCrearCampo && (
            <>
              <span className="text-sm text-gray-500">
                {camposDisponibles.length} campos disponibles
              </span>
              <button
                onClick={onCrearCampo}
                className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
              >
                Crear Nuevo Campo
              </button>
            </>
          )}
          {!modoEdicion && (
            <button
              onClick={crearPlantilla}
              className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
            >
              Crear Plantilla
            </button>
          )}
        </div>
      </div>
      {!modoEdicion && (
        <div className="mb-4 flex flex-col gap-2">
          <input
            type="text"
            placeholder="Nombre de la plantilla"
            value={nombre}
            onChange={e => setNombre(e.target.value)}
            className="p-2 border border-gray-300 rounded"
            required
          />
          <textarea
            placeholder="Descripción de la plantilla"
            value={descripcion}
            onChange={e => setDescripcion(e.target.value)}
            className="p-2 border border-gray-300 rounded"
            rows={2}
          />
          {tiposPlantilla.length > 0 && (
            <select
              value={tipoSeleccionado || ''}
              onChange={(e) => setTipoSeleccionado(e.target.value ? Number(e.target.value) : null)}
              className="p-2 border border-gray-300 rounded"
            >
              <option value="">-- Seleccionar tipo de plantilla --</option>
              {tiposPlantilla.map((tipo) => (
                <option key={tipo.id} value={tipo.id}>
                  {tipo.nombre}
                </option>
              ))}
            </select>
          )}
        </div>
      )}

      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">
          Selecciona texto en el editor y asígnalo a un campo para crear variables dinámicas
        </p>
        <div className="flex items-center space-x-4">
          <button
            type="button"
            onClick={() => {
              if (editor) {
                const { from, to } = editor.state.selection;
                if (from !== to) {
                  const textoSeleccionado = editor.state.doc.textBetween(from, to);
                  if (textoSeleccionado.trim()) {
                    setMostrarModal(true);
                  } else {
                    alert('Por favor selecciona texto primero');
                  }
                } else {
                  alert('Por favor selecciona texto primero');
                }
              }
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Asignar Campo Manualmente
          </button>
          <span className="text-xs text-gray-500">
            O espera 0.5 segundos después de seleccionar texto
          </span>
        </div>
      </div>

      <div className="toolbar mb-2 flex gap-2">
        <button type="button" onClick={() => editor && editor.chain().focus().toggleBold().run()}><b>B</b></button>
        <button type="button" onClick={() => editor && editor.chain().focus().toggleItalic().run()}><i>I</i></button>
        <button type="button" onClick={() => editor && editor.chain().focus().toggleUnderline().run()}><u>U</u></button>
        <select onChange={e => editor && editor.chain().focus().setFontFamily(e.target.value).run()} defaultValue="">
          <option value="">Fuente</option>
          <option value="Arial">Arial</option>
          <option value="Times New Roman">Times New Roman</option>
          <option value="Courier New">Courier New</option>
        </select>
        <select onChange={e => editor && editor.chain().focus().setFontSize(e.target.value).run()} defaultValue="">
          <option value="">Tamaño</option>
          <option value="12px">12</option>
          <option value="16px">16</option>
          <option value="20px">20</option>
          <option value="24px">24</option>
        </select>
        <button type="button" onClick={() => editor && editor.chain().focus().setTextAlign('left').run()}>Izquierda</button>
        <button type="button" onClick={() => editor && editor.chain().focus().setTextAlign('center').run()}>Centrar</button>
        <button type="button" onClick={() => editor && editor.chain().focus().setTextAlign('right').run()}>Derecha</button>
      </div>

      <div className="mb-6">
        <div className="border border-gray-300 rounded-md p-4 min-h-[400px]">
          <EditorContent editor={editor} />
        </div>
      </div>

      {camposAsignados.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Campos Asignados</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {camposAsignados.map((campo, index) => {
              const campoInfo = camposDisponibles.find(c => c.id === campo.campo_id);
              return (
                <div key={index} className="p-3 bg-gray-50 rounded-md">
                  <p className="text-sm font-medium">{campo.nombre_variable}</p>
                  <p className="text-xs text-gray-600">
                    Campo: {campoInfo?.nombre} ({campoInfo?.tipo_dato})
                  </p>
                  <p className="text-xs text-gray-500">
                    Texto original: "{campo.texto_seleccionado}"
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

            {/* Modal para asignar campo */}
      {mostrarModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Asignar Campo</h3>
            
            {editor && (
              <div className="mb-4 p-3 bg-gray-50 rounded-md">
                <p className="text-sm text-gray-600">
                  <strong>Texto seleccionado:</strong> "{editor.state.doc.textBetween(editor.state.selection.from, editor.state.selection.to)}"
                </p>
              </div>
            )}
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seleccionar Campo
                </label>
                <select
                  value={campoSeleccionado || ''}
                  onChange={(e) => setCampoSeleccionado(Number(e.target.value))}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="">Selecciona un campo</option>
                  {camposDisponibles.map((campo) => (
                    <option key={campo.id} value={campo.id}>
                      {campo.nombre} ({campo.tipo_dato})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre de Variable
                </label>
                <input
                  type="text"
                  value={nombreVariable}
                  onChange={(e) => setNombreVariable(e.target.value)}
                  placeholder="Ej: nombre_cliente"
                  className="w-full p-2 border border-gray-300 rounded-md"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Se usará como {`{{${nombreVariable}}}`} en la plantilla
                </p>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                onClick={() => {
                  setMostrarModal(false);
                  setCampoSeleccionado(null);
                  setNombreVariable('');
                }}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={asignarCampo}
                disabled={!campoSeleccionado || !nombreVariable.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Asignar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EditorDocumento; 