export interface WeightEntry {
  id: number;
  date: string; // ISO 8601 datetime string
  weight_kg: number;
  weight_lb: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface WeightEntryCreate {
  date: string; // ISO 8601 datetime string
  weight: number;
  unit: 'kg' | 'lb';
  notes?: string;
}

export interface WeightEntryUpdate {
  date?: string;
  weight?: number;
  unit?: 'kg' | 'lb';
  notes?: string;
}

export interface WeightEntryList {
  entries: WeightEntry[];
  total: number;
}

// For chart data transformation
export interface ChartDataPoint {
  date: string; // Formatted date for display
  weight: number; // In user's preferred unit
  fullDate: Date; // For sorting/filtering
}
