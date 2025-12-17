/**
 * datahubStorage.ts - LocalStorage Helper for Datahubs
 *
 * Handles saving, loading, and managing datahubs in browser localStorage
 */

const STORAGE_KEY = "finexus_datahubs";
const MAX_DATAHUBS = 50; // Prevent localStorage overflow

// ============================================================================
// TYPES
// ============================================================================

interface LayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  minH?: number;
}

interface WidgetConfig {
  datasetId?: string;
  dataSource?: string;
  chartType?: string;
  xAxis?: string;
  yAxis?: string[];
  metric?: string;
  [key: string]: unknown;
}

interface Widget {
  id: string;
  type: 'chart' | 'table' | 'stats' | 'text';
  title: string;
  config: WidgetConfig;
}

export interface Datahub {
  id: string;
  name: string;
  description: string;
  created_at?: string;
  updated_at?: string;
  layout: LayoutItem[];
  widgets: Record<string, Widget>;
}

interface StorageStats {
  count: number;
  maxCount: number;
  sizeBytes: number;
  sizeMB: string;
}

interface Template {
  id: string;
  name: string;
  description: string;
  preview: string;
}

// ============================================================================
// CORE FUNCTIONS
// ============================================================================

/**
 * Get all datahubs from localStorage
 */
export function getAllDatahubs(): Datahub[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const datahubs = JSON.parse(stored) as Datahub[];

    // Sort by updated_at descending
    return datahubs.sort((a, b) =>
      new Date(b.updated_at || '').getTime() - new Date(a.updated_at || '').getTime()
    );
  } catch (error) {
    console.error("Error loading datahubs:", error);
    return [];
  }
}

/**
 * Get single datahub by ID
 */
export function getDatahub(id: string): Datahub | null {
  const datahubs = getAllDatahubs();
  return datahubs.find(d => d.id === id) || null;
}

/**
 * Save datahub (create or update)
 */
export function saveDatahub(datahub: Datahub): boolean {
  try {
    const datahubs = getAllDatahubs();
    const now = new Date().toISOString();

    // Check if exists
    const index = datahubs.findIndex(d => d.id === datahub.id);

    if (index >= 0) {
      // Update existing
      datahubs[index] = {
        ...datahub,
        updated_at: now,
      };
    } else {
      // Create new
      if (datahubs.length >= MAX_DATAHUBS) {
        throw new Error(`Maximum ${MAX_DATAHUBS} datahubs allowed`);
      }

      datahubs.push({
        ...datahub,
        created_at: now,
        updated_at: now,
      });
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(datahubs));
    return true;
  } catch (error) {
    console.error("Error saving datahub:", error);
    throw error;
  }
}

/**
 * Delete datahub by ID
 */
export function deleteDatahub(id: string): boolean {
  try {
    const datahubs = getAllDatahubs();
    const filtered = datahubs.filter(d => d.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
    return true;
  } catch (error) {
    console.error("Error deleting datahub:", error);
    throw error;
  }
}

/**
 * Duplicate datahub
 */
export function duplicateDatahub(id: string): Datahub {
  try {
    const original = getDatahub(id);
    if (!original) {
      throw new Error("Datahub not found");
    }

    const now = new Date().toISOString();
    const duplicate: Datahub = {
      ...original,
      id: `datahub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: `${original.name} (Copy)`,
      created_at: now,
      updated_at: now,
    };

    saveDatahub(duplicate);
    return duplicate;
  } catch (error) {
    console.error("Error duplicating datahub:", error);
    throw error;
  }
}

/**
 * Export datahub as JSON
 */
export function exportDatahub(id: string): void {
  const datahub = getDatahub(id);
  if (!datahub) {
    throw new Error("Datahub not found");
  }

  const json = JSON.stringify(datahub, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `${datahub.name.replace(/[^a-z0-9]/gi, "_")}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Import datahub from JSON file
 */
export function importDatahub(file: File): Promise<Datahub> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const result = e.target?.result;
        if (typeof result !== 'string') {
          throw new Error("Failed to read file");
        }

        const datahub = JSON.parse(result) as Datahub;

        // Validate structure
        if (!datahub.name || !datahub.layout || !datahub.widgets) {
          throw new Error("Invalid datahub file format");
        }

        // Generate new ID
        datahub.id = `datahub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        saveDatahub(datahub);
        resolve(datahub);
      } catch (error) {
        reject(error);
      }
    };

    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.readAsText(file);
  });
}

/**
 * Clear all datahubs (use with caution!)
 */
export function clearAllDatahubs(): boolean {
  if (window.confirm("Are you sure you want to delete ALL datahubs? This cannot be undone.")) {
    localStorage.removeItem(STORAGE_KEY);
    return true;
  }
  return false;
}

/**
 * Get storage usage stats
 */
export function getStorageStats(): StorageStats {
  const datahubs = getAllDatahubs();
  const json = localStorage.getItem(STORAGE_KEY) || "[]";

  return {
    count: datahubs.length,
    maxCount: MAX_DATAHUBS,
    sizeBytes: new Blob([json]).size,
    sizeMB: (new Blob([json]).size / 1024 / 1024).toFixed(2),
  };
}

// ============================================================================
// DATAHUB TEMPLATES
// ============================================================================

/**
 * Create blank datahub
 */
export function createBlankDatahub(): Datahub {
  return {
    id: `datahub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    name: "Untitled Datahub",
    description: "",
    layout: [],
    widgets: {},
  };
}

/**
 * Create datahub from template
 */
export function createFromTemplate(templateName: string): Datahub {
  const templates: Record<string, Omit<Datahub, 'id'>> = {
    financial_overview: {
      name: "Financial Overview",
      description: "Key financial metrics and charts",
      layout: [
        { i: "widget_1", x: 0, y: 0, w: 4, h: 2, minW: 2, minH: 2 },
        { i: "widget_2", x: 4, y: 0, w: 4, h: 2, minW: 2, minH: 2 },
        { i: "widget_3", x: 8, y: 0, w: 4, h: 2, minW: 2, minH: 2 },
        { i: "widget_4", x: 0, y: 2, w: 12, h: 4, minW: 6, minH: 3 },
      ],
      widgets: {
        widget_1: {
          id: "widget_1",
          type: "stats",
          title: "Revenue",
          config: { metric: "revenue" },
        },
        widget_2: {
          id: "widget_2",
          type: "stats",
          title: "Net Income",
          config: { metric: "netIncome" },
        },
        widget_3: {
          id: "widget_3",
          type: "stats",
          title: "Total Assets",
          config: { metric: "totalAssets" },
        },
        widget_4: {
          id: "widget_4",
          type: "chart",
          title: "Revenue Trend",
          config: { chartType: "line", dataSource: "financial" },
        },
      },
    },

    market_analysis: {
      name: "Market Analysis",
      description: "Price movements and market data",
      layout: [
        { i: "widget_1", x: 0, y: 0, w: 8, h: 4, minW: 6, minH: 3 },
        { i: "widget_2", x: 8, y: 0, w: 4, h: 4, minW: 3, minH: 3 },
        { i: "widget_3", x: 0, y: 4, w: 12, h: 3, minW: 6, minH: 2 },
      ],
      widgets: {
        widget_1: {
          id: "widget_1",
          type: "chart",
          title: "Stock Price",
          config: { chartType: "line", dataSource: "daily" },
        },
        widget_2: {
          id: "widget_2",
          type: "stats",
          title: "Market Stats",
          config: {},
        },
        widget_3: {
          id: "widget_3",
          type: "table",
          title: "Recent Prices",
          config: { dataSource: "daily" },
        },
      },
    },

    comprehensive: {
      name: "Comprehensive Analysis",
      description: "Complete view with multiple data sources",
      layout: [
        { i: "widget_1", x: 0, y: 0, w: 3, h: 2, minW: 2, minH: 2 },
        { i: "widget_2", x: 3, y: 0, w: 3, h: 2, minW: 2, minH: 2 },
        { i: "widget_3", x: 6, y: 0, w: 3, h: 2, minW: 2, minH: 2 },
        { i: "widget_4", x: 9, y: 0, w: 3, h: 2, minW: 2, minH: 2 },
        { i: "widget_5", x: 0, y: 2, w: 6, h: 4, minW: 4, minH: 3 },
        { i: "widget_6", x: 6, y: 2, w: 6, h: 4, minW: 4, minH: 3 },
        { i: "widget_7", x: 0, y: 6, w: 12, h: 3, minW: 6, minH: 2 },
      ],
      widgets: {
        widget_1: { id: "widget_1", type: "stats", title: "Revenue", config: {} },
        widget_2: { id: "widget_2", type: "stats", title: "Profit Margin", config: {} },
        widget_3: { id: "widget_3", type: "stats", title: "ROE", config: {} },
        widget_4: { id: "widget_4", type: "stats", title: "Debt/Equity", config: {} },
        widget_5: { id: "widget_5", type: "chart", title: "Financial Trends", config: { chartType: "line" } },
        widget_6: { id: "widget_6", type: "chart", title: "Market Performance", config: { chartType: "area" } },
        widget_7: { id: "widget_7", type: "table", title: "Detailed Data", config: {} },
      },
    },
  };

  const template = templates[templateName];
  if (!template) {
    throw new Error("Template not found");
  }

  return {
    id: `datahub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    ...template,
  };
}

/**
 * Get available templates
 */
export function getTemplates(): Template[] {
  return [
    {
      id: "financial_overview",
      name: "Financial Overview",
      description: "Key financial metrics and charts",
      preview: "4 widgets: 3 stats + 1 chart",
    },
    {
      id: "market_analysis",
      name: "Market Analysis",
      description: "Price movements and market data",
      preview: "3 widgets: 1 chart + 1 stats + 1 table",
    },
    {
      id: "comprehensive",
      name: "Comprehensive Analysis",
      description: "Complete view with multiple data sources",
      preview: "7 widgets: 4 stats + 2 charts + 1 table",
    },
  ];
}
