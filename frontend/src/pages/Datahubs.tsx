// frontend/src/pages/Datahubs.tsx
import React, { useState, useEffect, MouseEvent } from "react";
import { useNavigate } from "react-router-dom";
import {
  Plus,
  Grid3x3,
  Calendar,
  Trash2,
  Copy,
  Download,
} from "lucide-react";
import {
  getAllDatahubs,
  deleteDatahub,
  duplicateDatahub,
  exportDatahub,
  getTemplates,
  createFromTemplate,
  saveDatahub,
} from "../services/datahubStorage";
import type { Datahub } from "../services/datahubStorage";

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface Template {
  id: string;
  name: string;
  description: string;
  preview: string;
}

// ============================================================================
// COMPONENT
// ============================================================================

export default function Datahubs(): React.ReactElement {
  const navigate = useNavigate();
  const [datahubs, setDatahubs] = useState<Datahub[]>([]);
  const [showTemplates, setShowTemplates] = useState(false);

  useEffect(() => {
    loadDatahubs();
  }, []);

  const loadDatahubs = (): void => {
    setDatahubs(getAllDatahubs());
  };

  const handleDelete = (id: string): void => {
    if (window.confirm("Delete this datahub?")) {
      deleteDatahub(id);
      loadDatahubs();
    }
  };

  const handleDuplicate = (id: string): void => {
    duplicateDatahub(id);
    loadDatahubs();
  };

  const handleCreateFromTemplate = (templateId: string): void => {
    const datahub = createFromTemplate(templateId);
    saveDatahub(datahub);
    navigate(`/datahubs/${datahub.id}`);
  };

  const handleCreateBlank = (): void => {
    navigate("/datahubs/new");
  };

  const templates: Template[] = getTemplates();

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Datahubs</h1>
            <p className="text-slate-600 mt-1">
              Create custom data dashboards
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowTemplates(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50"
            >
              <Grid3x3 className="w-4 h-4" />
              Templates
            </button>
            <button
              onClick={handleCreateBlank}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-black text-white hover:bg-black/90"
            >
              <Plus className="w-4 h-4" />
              New Datahub
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="p-6">
        {datahubs.length === 0 ? (
          <div className="text-center py-12">
            <Grid3x3 className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">
              No datahubs yet
            </h3>
            <p className="text-slate-600 mb-6">
              Create your first datahub to get started
            </p>
            <button
              onClick={handleCreateBlank}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-black text-white hover:bg-black/90"
            >
              <Plus className="w-5 h-5" />
              Create Datahub
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {datahubs.map((datahub) => (
              <article
                key={datahub.id}
                className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-lg transition-all cursor-pointer"
                onClick={() => navigate(`/datahubs/${datahub.id}`)}
              >
                <h3 className="font-semibold text-slate-900 mb-2">
                  {datahub.name}
                </h3>
                <p className="text-sm text-slate-600 mb-4 line-clamp-2">
                  {datahub.description || "No description"}
                </p>
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center gap-1">
                    <Grid3x3 className="w-3 h-3" />
                    {Object.keys(datahub.widgets || {}).length} widgets
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {datahub.updated_at
                      ? new Date(datahub.updated_at).toLocaleDateString()
                      : "—"}
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-4 pt-4 border-t border-slate-100">
                  <button
                    onClick={(e: MouseEvent<HTMLButtonElement>) => {
                      e.stopPropagation();
                      handleDuplicate(datahub.id);
                    }}
                    className="p-2 rounded hover:bg-slate-100"
                    title="Duplicate"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e: MouseEvent<HTMLButtonElement>) => {
                      e.stopPropagation();
                      exportDatahub(datahub.id);
                    }}
                    className="p-2 rounded hover:bg-slate-100"
                    title="Export"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e: MouseEvent<HTMLButtonElement>) => {
                      e.stopPropagation();
                      handleDelete(datahub.id);
                    }}
                    className="p-2 rounded hover:bg-rose-100 text-rose-600 ml-auto"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>

      {/* Template Modal */}
      {showTemplates && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-6 z-50">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">
              Choose Template
            </h2>
            <div className="space-y-3 mb-6">
              {templates.map((template) => (
                <button
                  key={template.id}
                  onClick={() => {
                    handleCreateFromTemplate(template.id);
                    setShowTemplates(false);
                  }}
                  className="w-full text-left p-4 rounded-xl border border-slate-200 hover:bg-slate-50 transition-colors"
                >
                  <h3 className="font-medium text-slate-900 mb-1">
                    {template.name}
                  </h3>
                  <p className="text-sm text-slate-600 mb-2">
                    {template.description}
                  </p>
                  <p className="text-xs text-slate-500">{template.preview}</p>
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowTemplates(false)}
              className="w-full px-4 py-2 rounded-xl border border-slate-200 hover:bg-slate-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
