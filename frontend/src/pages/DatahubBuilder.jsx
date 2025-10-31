import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Responsive, WidthProvider } from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import { ArrowLeft,  Save,  Plus,  Eye,  EyeOff,  Download,  Grid3x3,  BarChart3,  Table as TableIcon,  TrendingUp,  FileText,} from "lucide-react";
import { ChartWidget, TableWidget, StatsWidget, TextWidget } from "../components/dashboard/Widgets";
import {  getDatahub,  saveDatahub,  exportDatahub,  createBlankDatahub,} from "../services/datahubStorage";
import ConfigPanel from "../components/dashboard/ConfigPanel";
/**
 * DatahubBuilder.jsx - Drag-and-Drop Datahub Builder
 * 
 * Features:
 * - Free grid layout with react-grid-layout
 * - 4 widget types (chart, table, stats, text)
 * - Side panel configuration
 * - LocalStorage save/load
 * - Max 12 widgets
 * - Auto-responsive
 */

const ResponsiveGridLayout = WidthProvider(Responsive);

function cls(...classes) {
  return classes.filter(Boolean).join(" ");
}

// Widget type definitions
const WIDGET_TYPES = [
  { type: "chart", label: "Chart", icon: BarChart3, color: "blue" },
  { type: "table", label: "Table", icon: TableIcon, color: "emerald" },
  { type: "stats", label: "Stats", icon: TrendingUp, color: "amber" },
  { type: "text", label: "Text", icon: FileText, color: "slate" },
];

const MAX_WIDGETS = 12;

export default function DatahubBuilder() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNewDatahub = id === "new";

  // Datahub state
  const [datahub, setDatahub] = useState(null);
  const [layout, setLayout] = useState([]);
  const [widgets, setWidgets] = useState({});

  // UI state
  const [isEditing, setIsEditing] = useState(true);
  const [showConfig, setShowConfig] = useState(false);
  const [activeWidget, setActiveWidget] = useState(null);
  const [showPalette, setShowPalette] = useState(false);

  // Load datahub
  useEffect(() => {
    if (isNewDatahub) {
      const blank = createBlankDatahub();
      setDatahub(blank);
      setLayout(blank.layout);
      setWidgets(blank.widgets);
    } else {
      const loaded = getDatahub(id);
      if (loaded) {
        setDatahub(loaded);
        setLayout(loaded.layout);
        setWidgets(loaded.widgets);
      } else {
        alert("Datahub not found");
        navigate("/datahubs");
      }
    }
  }, [id, isNewDatahub, navigate]);

  useEffect(() => {
    console.log("showConfig =", showConfig, "activeWidget =", activeWidget);
  }, [showConfig, activeWidget]);
  

  // Save datahub
  const handleSave = () => {
    try {
      const updated = {
        ...datahub,
        layout,
        widgets,
      };
      saveDatahub(updated);
      alert("Datahub saved successfully!");
      
      if (isNewDatahub) {
        navigate(`/datahubs/${updated.id}`);
      }
    } catch (error) {
      alert(`Save failed: ${error.message}`);
    }
  };

  // Add widget
  const handleAddWidget = (type) => {
    if (Object.keys(widgets).length >= MAX_WIDGETS) {
      alert(`Maximum ${MAX_WIDGETS} widgets allowed`);
      return;
    }

    const widgetId = `widget_${Date.now()}`;
    const newWidget = {
      id: widgetId,
      type,
      title: `New ${type.charAt(0).toUpperCase() + type.slice(1)}`,
      config: {},
    };

    // Add to layout
    const newLayoutItem = {
      i: widgetId,
      x: (layout.length * 4) % 12,
      y: Infinity, // Puts it at bottom
      w: type === "stats" ? 3 : 6,
      h: type === "stats" ? 2 : 4,
      minW: 2,
      minH: 2,
    };

    setWidgets({ ...widgets, [widgetId]: newWidget });
    setLayout([...layout, newLayoutItem]);
    setShowPalette(false);
  };

  // Remove widget
  const handleRemoveWidget = (widgetId) => {
    const updated = { ...widgets };
    delete updated[widgetId];
    setWidgets(updated);
    setLayout(layout.filter(item => item.i !== widgetId));
    
    if (activeWidget === widgetId) {
      setActiveWidget(null);
      setShowConfig(false);
    }
  };

  // Configure widget
  const handleConfigureWidget = (widgetId) => {
    console.log('Configure clicked:', widgetId, 'showConfig will be:', true);
    setActiveWidget(widgetId);
    setShowConfig(true);
  };

  // Update widget config
  const handleUpdateWidget = (widgetId, updates) => {
    setWidgets({
      ...widgets,
      [widgetId]: { ...widgets[widgetId], ...updates },
    });
  };

  // Layout change
  const handleLayoutChange = (newLayout) => {
    setLayout(newLayout);
  };

  // Export
  const handleExport = () => {
    if (!datahub?.id) return;
    
    const toExport = {
      ...datahub,
      layout,
      widgets,
    };
    exportDatahub(toExport.id);
  };

  if (!datahub) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-slate-500">Loading...</div>
      </div>
    );
  }

  const activeWidgetData = activeWidget ? widgets[activeWidget] : null;
  

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Bar */}
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <button
              onClick={() => navigate("/datahubs")}
              className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            
            <div className="min-w-0">
              <input
                type="text"
                value={datahub.name}
                onChange={(e) => setDatahub({ ...datahub, name: e.target.value })}
                className="text-xl font-semibold bg-transparent border-none focus:outline-none focus:ring-0 px-0 text-slate-900"
                placeholder="Datahub Name"
              />
              <input
                type="text"
                value={datahub.description}
                onChange={(e) => setDatahub({ ...datahub, description: e.target.value })}
                className="text-sm text-slate-600 bg-transparent border-none focus:outline-none focus:ring-0 px-0 mt-1 w-full"
                placeholder="Add description..."
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className={cls(
                "inline-flex items-center gap-2 px-4 py-2 rounded-xl transition-colors",
                isEditing
                  ? "bg-slate-900 text-white"
                  : "bg-white border border-slate-200 text-slate-700 hover:bg-slate-50"
              )}
            >
              {isEditing ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              {isEditing ? "Edit Mode" : "View Mode"}
            </button>

            <button
              onClick={handleExport}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 transition-colors"
            >
              <Download className="w-4 h-4" />
              Export
            </button>

            <button
              onClick={handleSave}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-black text-white hover:bg-black/90 transition-colors"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Canvas */}
        <main className="flex-1 overflow-auto p-6 relative">
          {isEditing && (
            <button
              onClick={() => setShowPalette(!showPalette)}
              className="fixed bottom-6 right-6 z-50 p-4 rounded-full bg-black text-white shadow-lg hover:bg-black/90 transition-all"
            >
              <Plus className="w-6 h-6" />
            </button>
          )}

          {/* Widget Palette */}
          {isEditing && showPalette && (
            <div className="fixed bottom-24 right-6 z-50 bg-white rounded-xl border border-slate-200 shadow-lg p-4 space-y-2 w-64">
              <div className="font-medium text-slate-900 mb-3">Add Widget</div>
              {WIDGET_TYPES.map((wt) => {
                const Icon = wt.icon;
                return (
                  <button
                    key={wt.type}
                    onClick={() => handleAddWidget(wt.type)}
                    className="w-full flex items-center gap-3 p-3 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors text-left"
                  >
                    <Icon className="w-5 h-5 text-slate-600" />
                    <span className="text-sm font-medium text-slate-900">{wt.label}</span>
                  </button>
                );
              })}
              <div className="text-xs text-slate-500 pt-2 border-t border-slate-200">
                {Object.keys(widgets).length} / {MAX_WIDGETS} widgets
              </div>
            </div>
          )}

          {/* Grid */}
          {layout.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-slate-500">
                <Grid3x3 className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                <div className="text-lg font-medium mb-2">Empty Datahub</div>
                <div className="text-sm">Click the + button to add widgets</div>
              </div>
            </div>
          ) : (
            <ResponsiveGridLayout
              className="layout"
              layouts={{ lg: layout }}
              breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
              cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
              rowHeight={60}
              onLayoutChange={handleLayoutChange}
              isDraggable={isEditing}
              isResizable={isEditing}
              draggableHandle=".drag-handle"
              compactType="vertical"
              preventCollision={false}
            >
              {layout.map((item) => {
                const widget = widgets[item.i];
                if (!widget) return null;

                const WidgetComponent = {
                  chart: ChartWidget,
                  table: TableWidget,
                  stats: StatsWidget,
                  text: TextWidget,
                }[widget.type];

                return (
                  <div key={item.i}>
                    <WidgetComponent
                      {...widget}
                      onConfigChange={handleConfigureWidget}
                      onRemove={handleRemoveWidget}
                      isEditing={isEditing}
                    />
                  </div>
                );
              })}
            </ResponsiveGridLayout>
          )}
        </main>

        {/* Config Panel */}
        {showConfig && activeWidgetData && (
          <aside className="w-96 bg-white border-l border-slate-200 overflow-y-auto">
            <ConfigPanel
              widget={activeWidgetData}
              onUpdate={(updates) => handleUpdateWidget(activeWidget, updates)}
              onClose={() => {
                setShowConfig(false);
                setActiveWidget(null);
              }}
            />
          </aside>
        )}
      </div>
    </div>
  );
}
